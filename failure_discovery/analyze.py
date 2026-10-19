"""Discover candidate behavior groups from saved sensor-proxy traces, never causes."""
import os
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_name] = '1'
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
from datetime import datetime

import numpy as np
from scipy.spatial.transform import Rotation
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
# Explicit allowlist: no physical properties, oracle contacts, simulator velocities,
# old failure names, or policy observations may enter features/metric calculations.
SIGNALS = ('input__object_pose_tcp_m_wxyz', 'input__object_pose_world_m_wxyz',
           'input__tcp_pose_world_m_wxyz', 'input__finger_width_m',
           'input__finger_force_mean_world_n', 'input__action_applied',
           'input__object_goal_distance_m', 'meta__state_time_s')
CHANNELS = ([f'object_in_gripper_{a}_m' for a in 'xyz'] +
            [f'relative_rotation_{a}_rad' for a in 'xyz'] +
            [f'object_displacement_{a}_m' for a in 'xyz'] +
            [f'gripper_displacement_{a}_m' for a in 'xyz'] +
            ['finger_width_m', 'left_net_force_n', 'right_net_force_n'] +
            [f'applied_action_{i}' for i in range(5)] + ['object_goal_distance_m'])


def resample(values, length):
    values = np.asarray(values, dtype=float)
    old = np.linspace(0, 1, len(values))
    new = np.linspace(0, 1, length)
    if values.ndim == 1:
        return np.interp(new, old, values)[:, None]
    return np.column_stack([np.interp(new, old, col) for col in values.T])


def longest_steady_hold(time, relative_pose, goal_distance, force,
                        target_m=.025, translation_m=.003, rotation_rad=np.deg2rad(5),
                        contact_n=.05, terminal_only=False):
    """Longest interval near goal, bilateral force proxy, bounded relative excursion.

    Not an oracle grasp/contact label. Excursions are measured from interval start;
    thus two samples can differ by up to twice the stated translation/angle limit.
    """
    rot = Rotation.from_quat(relative_pose[:, 3:], scalar_first=True)
    eligible = (goal_distance <= target_m) & (force.min(axis=1) >= contact_n)
    longest = 0.
    for start in np.flatnonzero(eligible):
        angle = (rot[start:].__mul__(rot[start].inv())).magnitude()
        distance = np.linalg.norm(relative_pose[start:, :3] - relative_pose[start, :3], axis=1)
        good = eligible[start:] & (angle <= rotation_rad) & (distance <= translation_m)
        stop = np.flatnonzero(~good)
        end = start + (int(stop[0]) - 1 if len(stop) else len(good) - 1)
        if end >= start and (not terminal_only or end == len(time) - 1):
            longest = max(longest, float(time[end] - time[start]))
    return longest


def extract(signals, length=60):
    """Pure sensor-proxy transform. It cannot read an episode's label namespace."""
    d = signals
    relative = d['input__object_pose_tcp_m_wxyz']
    obj = d['input__object_pose_world_m_wxyz']
    tcp = d['input__tcp_pose_world_m_wxyz']
    time = d['meta__state_time_s']
    if len(time) < 2 or np.any(np.diff(time) <= 0):
        raise ValueError('Need increasing state times and at least two samples')
    n = len(time)
    forces = np.linalg.norm(d['input__finger_force_mean_world_n'], axis=-1)
    if forces.shape != (n - 1, 2):
        raise ValueError('Mean forces must have one row per completed action')
    state_force = np.vstack([np.zeros((1, 2)), forces])
    rot = Rotation.from_quat(relative[:, 3:], scalar_first=True)
    rel_rot = (rot * rot[0].inv()).as_rotvec()
    actions = d['input__action_applied']
    if actions.shape != (n - 1, 5):
        raise ValueError('Expected the existing five-action policy')
    # State traces and completed-action traces each resampled over their actual
    # time support. Actions describe intervals, represented at interval midpoints.
    action_time = (time[:-1] + time[1:]) / 2
    sample_time = np.linspace(time[0], time[-1], length)
    action_features = np.column_stack([np.interp(sample_time, action_time, a) for a in actions.T])
    state_features = np.column_stack([relative[:, :3], rel_rot,
        obj[:, :3] - obj[0, :3], tcp[:, :3] - tcp[0, :3],
        d['input__finger_width_m'], state_force,
        d['input__object_goal_distance_m']])
    state_resampled = resample(state_features, length)
    features = np.column_stack([state_resampled[:, :15], action_features, state_resampled[:, 15:]])
    if not np.isfinite(features).all():
        raise ValueError('Nonfinite sensor trace')
    bilateral = state_force.min(axis=1) >= .05
    motion_mask = bilateral[1:] & bilateral[:-1]
    translation = np.linalg.norm(np.diff(relative[:, :3], axis=0), axis=1)
    angular = (rot[1:] * rot[:-1].inv()).magnitude()
    hold = longest_steady_hold(time, relative, d['input__object_goal_distance_m'], state_force)
    terminal_hold = longest_steady_hold(time, relative, d['input__object_goal_distance_m'],
                                        state_force, terminal_only=True)
    metrics = dict(
        final_target_error_m=float(d['input__object_goal_distance_m'][-1]),
        minimum_target_error_m=float(d['input__object_goal_distance_m'].min()),
        relative_translation_path_during_bilateral_force_m=(float(translation[motion_mask].sum()) if motion_mask.any() else None),
        relative_rotation_path_during_bilateral_force_rad=(float(angular[motion_mask].sum()) if motion_mask.any() else None),
        longest_steady_hold_s=hold,
        terminal_steady_hold_s=terminal_hold,
        stability_success_proxy=terminal_hold >= .5 - 1e-9,
        bilateral_force_duration_s=float(np.diff(time)[bilateral[1:]].sum()),
        episode_duration_s=float(time[-1] - time[0]),
    )
    return features, metrics


def fit_model(x, k, random_state):
    scaler = StandardScaler().fit(x)
    z = scaler.transform(x)
    # PCA and scaling are fitted only on training starting states.
    pca = PCA(n_components=min(20, len(x) - 1, x.shape[1]), svd_solver='full').fit(z)
    z = pca.transform(z)
    km = KMeans(n_clusters=k, random_state=random_state, n_init=20).fit(z)
    return scaler, pca, km


def project(model, x):
    scaler, pca, km = model
    return pca.transform(scaler.transform(x))


def predict(model, x):
    return model[2].predict(project(model, x))


def safe_silhouette(x, labels):
    unique = np.unique(labels)
    return float(silhouette_score(x, labels)) if 1 < len(unique) < len(labels) else None


def save_csv(path, rows):
    if not rows:
        path.write_text('')
        return
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def select_episodes(dataset, maximum, single_factors=None):
    # Seed is used only to balance sampling and separate starting states.
    by_seed = {}
    index_path = dataset / 'episodes.json'
    if single_factors and not index_path.exists():
        raise ValueError('Single-factor selection needs the completed episode index')
    if index_path.exists():
        entries = json.loads(index_path.read_text())
        if single_factors:
            allowed = set(single_factors)
            if any('changed_factors' not in e for e in entries):
                raise ValueError('This index does not declare independent experiment factors')
            entries = [e for e in entries if len(e['changed_factors']) <= 1
                       and set(e['changed_factors']) <= allowed]
        for entry in entries:
            if Path(entry['file']).name != entry['file']:
                raise ValueError('Invalid indexed filename')
            by_seed.setdefault(int(entry['seed']), []).append(dataset / entry['file'])
    else:
        for path in sorted(dataset.glob('*.npz')):
            with np.load(path, allow_pickle=False) as d:
                seed = int(d['label__seed'])
            by_seed.setdefault(seed, []).append(path)
    # Round-robin sampling across seeds; hash order avoids condition-name ordering.
    pools = {s: sorted(paths, key=lambda p: hashlib.sha256(p.name.encode()).hexdigest())
             for s, paths in by_seed.items()}
    result = []
    for i in range(max(map(len, pools.values()), default=0)):
        for seed in sorted(pools):
            if i < len(pools[seed]) and len(result) < maximum:
                result.append((seed, pools[seed][i]))
    return result


def run(args):
    if args.max_episodes < 30 or args.samples < 10:
        raise ValueError('Use at least 30 episodes and 10 trajectory samples')
    selected = select_episodes(args.dataset, args.max_episodes, getattr(args, 'single_factors', None))
    if not selected:
        raise ValueError('No completed NPZ episodes found')
    rows, traces, source = [], [], []
    for seed, path in selected:
        with np.load(path, allow_pickle=False) as d:
            if int(d['label__seed']) != seed:
                raise ValueError('Indexed starting seed disagrees with recording')
            signals = {k: d[k].copy() for k in SIGNALS}
            feature, metrics = extract(signals, args.samples)
            # Used only to select the failure subset, not as a feature or failure type.
            original_success = bool(d['label__held_goal_success_final'])
        source.append(dict(file=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        rows.append(dict(episode=path.stem, seed=seed, original_success=original_success,
                         cluster='success_reference' if original_success else '', split='', **metrics))
        traces.append(feature)
    traces = np.stack(traces)
    flat = traces.reshape(len(traces), -1)
    seeds = sorted(set(r['seed'] for r in rows))
    if len(seeds) < 5:
        raise ValueError('Need at least five distinct starting seeds for held-out validation')
    test_seeds = seeds[-max(2, round(len(seeds) * .2)):]
    failures = np.array([not r['original_success'] for r in rows])
    test = failures & np.array([r['seed'] in test_seeds for r in rows])
    train = failures & ~test
    if train.sum() < 12 or test.sum() < 6:
        raise ValueError('Need at least 12 training failures and six held-out failures')
    candidates = []
    models = {}
    for k in range(2, min(6, int(train.sum()) // 3) + 1):
        model = fit_model(flat[train], k, args.random_seed)
        score = safe_silhouette(project(model, flat[train]), model[2].labels_)
        if score is not None:
            candidates.append(dict(k=k, training_silhouette=score))
            models[k] = model
    if not candidates:
        raise ValueError('No usable candidate grouping; traces may lack distinct variation')
    best = max(candidates, key=lambda r: r['training_silhouette'])
    k = best['k']
    model = models[k]
    labels = predict(model, flat)
    held_labels = labels[test]
    held_silhouette = safe_silhouette(project(model, flat[test]), held_labels)
    # Independent seed subsets; refit representation and grouping each time.
    # Compare assignments on the SAME unseen seed panel, ignoring label numbering.
    train_seeds = sorted(set(seeds) - set(test_seeds))
    rng = np.random.default_rng(args.random_seed)
    agreement = []
    subset_counts = []
    for repeat in range(8):
        keep = rng.choice(train_seeds, max(2, int(np.ceil(.75 * len(train_seeds)))), replace=False)
        mask = train & np.array([r['seed'] in keep for r in rows])
        if mask.sum() > k:
            alternate = fit_model(flat[mask], k, args.random_seed + repeat + 1)
            alternate_labels = predict(alternate, flat[test])
            agreement.append(float(adjusted_rand_score(held_labels, alternate_labels)))
            subset_counts.append(len(np.unique(alternate_labels)))
    for i, row in enumerate(rows):
        row['split'] = 'held_out_seed' if row['seed'] in test_seeds else 'training_seed'
        if failures[i]:
            row['cluster'] = f'group_{int(labels[i]) + 1}'
    out = args.output or ROOT / 'failure_discovery' / 'results' / datetime.now().strftime('pilot_%Y%m%d_%H%M%S')
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    save_csv(out / 'episode_metrics.csv', rows)
    # Reveal metadata ONLY after the feature extraction, model selection and fit.
    physical = []
    for row, (_, path) in zip(rows, selected):
        with np.load(path, allow_pickle=False) as d:
            physical.append(dict(episode=row['episode'], cluster=row['cluster'], seed=row['seed'],
                condition_id=str(d['label__condition_id']), mass_kg=float(d['label__mass_kg']),
                object_static_friction=float(d['label__object_static_friction']),
                size_xyz_m=json.dumps(d['label__size_xyz_m'].tolist()), shape=str(d['label__shape']),
                com_offset_m=json.dumps(d['label__com_offset_m'].tolist()),
                full_condition_json=str(d['label__condition_json'])))
    save_csv(out / 'physical_settings_revealed_after_grouping.csv', physical)
    unique_conditions = sorted(set(p['condition_id'] for p in physical))
    counts = []
    for condition in unique_conditions:
        subset = [p for p in physical if p['condition_id'] == condition]
        count = dict(condition_id=condition, sampled_episodes=len(subset),
                     successes=sum(p['cluster'] == 'success_reference' for p in subset))
        count.update({f'group_{g + 1}': sum(p['cluster'] == f'group_{g + 1}' for p in subset) for g in range(k)})
        counts.append(count)
    save_csv(out / 'condition_group_counts.csv', counts)
    report = dict(status='exploratory_candidates_not_verified_failure_mechanisms',
        source_dataset=str(args.dataset.resolve()), episodes=len(rows), failures=int(failures.sum()),
        original_successes=int((~failures).sum()), stability_success_proxy=sum(r['stability_success_proxy'] for r in rows),
        original_success_but_not_stable_proxy=sum(r['original_success'] and not r['stability_success_proxy'] for r in rows),
        training_failures=int(train.sum()), held_out_failures=int(test.sum()), held_out_seeds=test_seeds,
        chosen_groups=k, candidates=candidates, held_out_silhouette=held_silhouette,
        held_out_group_counts={f'group_{g+1}': int((held_labels == g).sum()) for g in range(k)},
        group_counts={f'group_{g+1}': int((failures & (labels == g)).sum()) for g in range(k)},
        seed_subset_agreement_ari=agreement, seed_subset_groups_present_on_holdout=subset_counts,
        mean_seed_subset_agreement_ari=float(np.mean(agreement)) if agreement else None,
        pca_components=int(model[1].n_components_), pca_explained_variance=float(model[1].explained_variance_ratio_.sum()),
        random_seed=args.random_seed, resampled_points=args.samples, channels=CHANNELS,
        single_factor_selection=getattr(args, 'single_factors', None),
        selection='Optional design-factor filter, then round robin by seed, SHA256(filename) order; no outcome-based sampling. Factor values never enter features.',
        feature_allowlist=list(SIGNALS),
        thresholds=dict(target_error_m=.025, relative_excursion_from_interval_start_m=.003,
                        relative_angle_from_interval_start_deg=5, finger_force_proxy_n=.05, minimum_terminal_hold_s=.5),
        notes=['Thresholds are provisional, not tuned to outcomes or physical properties.',
               'Bilateral net finger force is a sensor proxy; it does not prove object contact or secure grasp.',
               'Stability uses sampled 20 Hz relative poses; fast motion between samples can be missed.',
               'Original success selects failures; the new stability proxy is reported separately and requires a hold ending at the final timestep.',
               'PCA, scaling and K selection use training seeds only. No cause or old failure-type labels enter fitting.',
               'Reset-aligned normalized-time traces can cluster task phase, geometry or timing rather than mechanisms.',
               'Held-out seeds test new starts, not new physical conditions.',
               'ARI compares eight seed-subset refits on one fixed held-out panel; it is not failure-label accuracy.',
               'Condition counts are exploratory associations with unequal small samples, not causal estimates.',
               'K >= 2 forces a partition; silhouette alone does not establish that distinct failure types exist.'])
    (out / 'scores.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    provenance = dict(source_files=source, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out / 'manifest.json').write_text(json.dumps(provenance, indent=2) + '\n')
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    z = project(model, flat)
    for group in range(k):
        for split, marker in [(train, 'o'), (test, '^')]:
            mask = split & (labels == group)
            axes[0].scatter(z[mask, 0], z[mask, 1], color=f'C{group}', marker=marker,
                            label=f'Group {group+1}' if marker == 'o' else None, alpha=.75)
        mask = failures & (labels == group)
        axes[1].scatter([r['final_target_error_m'] for r, m in zip(rows, mask) if m],
                        [r['longest_steady_hold_s'] for r, m in zip(rows, mask) if m],
                        color=f'C{group}', alpha=.7)
    axes[0].set(xlabel='Trajectory component 1', ylabel='Trajectory component 2',
                title='Candidate groups: circles=train, triangles=unseen starts')
    axes[0].legend()
    axes[1].set(xlabel='Final object-to-target distance (m)', ylabel='Longest steady hold proxy (s)',
                title='How failures fall short of stable success')
    fig.savefig(out / 'groups.png', dpi=150)
    plt.close(fig)
    panels = [(20, 'Object-to-target distance (m)'), (2, 'Object Z in gripper frame (m)'),
              (12, 'Finger opening (m)'), (13, 'Left net finger force (N)'),
              (14, 'Right net finger force (N)'), (5, 'Relative rotation Z (rad)')]
    fig, axes = plt.subplots(3, 2, figsize=(12, 10), constrained_layout=True)
    for ax, (channel, title) in zip(axes.flat, panels):
        for group in range(k):
            series = traces[failures & (labels == group), :, channel]
            mean = series.mean(axis=0)
            lo, hi = np.percentile(series, [25, 75], axis=0)
            x = np.linspace(0, 100, args.samples)
            ax.plot(x, mean, color=f'C{group}', label=f'Group {group+1} (n={len(series)})')
            ax.fill_between(x, lo, hi, color=f'C{group}', alpha=.15)
        ax.set(title=title, xlabel='Episode progress (%)')
    axes.flat[0].legend()
    fig.suptitle('Recorded behavior: mean and middle 50%; groups are unnamed candidates')
    fig.savefig(out / 'group_traces.png', dpi=150)
    plt.close(fig)
    representatives = []
    for group in range(k):
        indices = np.flatnonzero(failures & (labels == group))
        order = np.argsort(np.linalg.norm(z[indices] - model[2].cluster_centers_[group], axis=1))
        representatives.extend(dict(group=f'group_{group+1}', episode=rows[i]['episode'],
                                    source_file=str(selected[i][1]), split=rows[i]['split'])
                               for i in indices[order[:3]])
    save_csv(out / 'representative_episodes.csv', representatives)
    summary = (f'# Failure discovery pilot\n\nAnalyzed {len(rows)} saved episodes: '
        f'{int(failures.sum())} original failures and {int((~failures).sum())} original successes.\n\n'
        f'Found **{k} candidate behavior groups**. These are not verified physical failure types.\n\n'
        f'- Failure group sizes: {report["group_counts"]}. Small groups may be outliers rather than failure types.\n'
        f'- Held-out silhouette: {held_silhouette}. Higher indicates more separated groups; negative indicates overlap.\n'
        f'- Mean seed-subset agreement (ARI): {report["mean_seed_subset_agreement_ari"]}. '
        'One means identical assignments up to group names; zero is chance-level agreement.\n'
        f'- Seed-subset refits collapsing to one held-out group: {sum(n == 1 for n in subset_counts)}/{len(subset_counts)}.\n'
        f'- Stable-success proxy: {report["stability_success_proxy"]} episodes. '
        'This uses provisional thresholds and does not replace original success.\n\n'
        'See scores.json for all assumptions and limitations. '
        'Next: inspect representatives, check threshold sensitivity, and reproduce groups on a larger sample. '
        'Physical settings are revealed in separate CSVs after grouping; no causal conclusion is established.\n')
    (out / 'SUMMARY.md').write_text(summary)
    (out / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Failure discovery pilot</title>'
        '<style>body{max-width:1200px;margin:30px auto;font:17px sans-serif}img{width:100%}pre{white-space:pre-wrap}</style>'
        '<h1>Failure discovery pilot</h1><pre>' + html.escape(summary) + '</pre>'
        '<img src="groups.png"><img src="group_traces.png">'
        '<p><a href="episode_metrics.csv">Episode metrics</a> · '
        '<a href="scores.json">Scores and assumptions</a> · '
        '<a href="representative_episodes.csv">Representative episodes</a></p>')
    print(json.dumps(dict(output=str(out), **{key: report[key] for key in
          ['episodes', 'failures', 'chosen_groups', 'held_out_silhouette', 'mean_seed_subset_agreement_ari']})))
    return out


# -----------------------------------------------------------------------------
# STEP 3 — FUTURE / DISABLED: which robot measurements indicate each failure group?
# Keep this beside discovery because it reuses its traces, group assignments and
# seed split. It must NOT change how the groups were discovered above.
#
# Intended output: one row per (failure group, measurement family), containing
# recognition F1 with all measurements, F1 after removing that family, and the
# difference. A larger positive decrease makes that family a candidate indicator
# of that group. Retain negative differences rather than hiding them.
#
# This diagnoses the learned behavior groups; it does not prove physical causes.
# Group labels already depend on these traces, so reconstructing them is partly
# circular. Held-out seeds test whether that reconstruction transfers to new
# starts, NOT whether the groups are true failure mechanisms. Group reliability
# must be checked separately using the discovery validation above.
#
# Available robot-side signals: estimated object pose relative to gripper, object
# and gripper movement, finger width, net finger-force proxies, commanded actions,
# and object-to-goal distance. Their reality depends on available sensors/estimators.
# Exact sim mass/friction/CoM, oracle contact and old failure names stay excluded.
# The current reported 40 g mass estimate is constant: these data cannot establish
# its influence. Add other estimated quantities only when a real estimator logs
# them; never substitute simulator truth and call it a measurable estimate.
#
# Example implementation sketch below is entirely commented out. Do not call it
# from run() until the candidate groups are stable and this protocol is reviewed.
#
# def measurement_indicators(traces, group_ids, train_mask, test_mask):
#     from sklearn.pipeline import make_pipeline
#     from sklearn.linear_model import LogisticRegression
#     from sklearn.metrics import f1_score
#     from sklearn.dummy import DummyClassifier
#
#     # Inputs contain FAILURE EPISODES ONLY, with masks split by whole seeds.
#     # Group discovery/selection and any hyperparameter tuning use training seeds.
#     # Never select the best signal using the held-out results and then report
#     # that same panel as an independent final test. Reserve extra seeds if tuning.
#     families = {
#         'object_in_gripper_position': [0, 1, 2],
#         'object_in_gripper_orientation': [3, 4, 5],
#         'object_movement': [6, 7, 8],
#         'gripper_movement': [9, 10, 11],
#         'finger_opening': [12],
#         'finger_force': [13, 14],
#         'commanded_action': [15, 16, 17, 18, 19],
#         'object_to_target_distance': [20],
#     }
#     group_ids = np.asarray(group_ids)
#     groups = np.unique(group_ids[train_mask])
#     x = traces.reshape(len(traces), -1)
#     n_channels = traces.shape[2]
#
#     def evaluate(columns):
#         model = make_pipeline(StandardScaler(), LogisticRegression(
#             class_weight='balanced', max_iter=2000, random_state=17))
#         model.fit(x[train_mask][:, columns], group_ids[train_mask])
#         prediction = model.predict(x[test_mask][:, columns])
#         return f1_score(group_ids[test_mask], prediction, labels=groups,
#                         average=None, zero_division=0)
#
#     baseline = DummyClassifier(strategy='most_frequent')
#     baseline.fit(x[train_mask], group_ids[train_mask])
#     chance = f1_score(group_ids[test_mask], baseline.predict(x[test_mask]),
#                      labels=groups, average=None, zero_division=0)
#     full_f1 = evaluate(np.arange(x.shape[1]))
#     result = []
#     for name, channels in families.items():
#         # Remove this family at EVERY timestep and refit. Merely zeroing it
#         # after fitting creates an artificial input rather than a fair ablation.
#         keep_channels = np.ones(n_channels, dtype=bool)
#         keep_channels[channels] = False
#         keep = np.flatnonzero(np.tile(keep_channels, traces.shape[1]))
#         reduced_f1 = evaluate(keep)
#         for i, group in enumerate(groups):
#             result.append(dict(group=int(group), measurement=name,
#                 full_f1=float(full_f1[i]), majority_baseline_f1=float(chance[i]),
#                 without_measurement_f1=float(reduced_f1[i]),
#                 indicator_f1_drop=float(full_f1[i] - reduced_f1[i])))
#     return result
#
# Before enabling:
# - Report per-group support; scores for rare groups are unreliable.
# - Repeat across whole-seed splits and report uncertainty, not just one ranking.
# - Correlated signals can replace each other: a small removal effect does not
#   prove a measurement is useless. Also test useful pairs / families together.
# - The sketch uses full episodes for POST-HOC diagnosis. For early warning,
#   rebuild features from observations up to fixed real-time cutoffs only;
#   do not resample a future full episode into a prefix or use future event times.
# - To ask whether a controllable variable CAUSES a failure, use matched-seed
#   interventions separately. Do not treat this sensor ranking as causal proof.
# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=ROOT / 'runs/failure_collection/varied_fixed40g')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--single-factors', nargs='+', help='Use nominal and only isolated changes to these design factors; exclude mixed settings')
    parser.add_argument('--max-episodes', type=int, default=120)
    parser.add_argument('--samples', type=int, default=60)
    parser.add_argument('--random-seed', type=int, default=17)
    run(parser.parse_args())


if __name__ == '__main__':
    main()

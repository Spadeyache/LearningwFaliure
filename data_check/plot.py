#!/usr/bin/env python3
"""Read plots.md and generate one isolated episode/parameter plot per table row."""
import argparse
import csv
import hashlib
import html
import json
import os
from pathlib import Path
import re
import textwrap

os.environ.setdefault('MPLCONFIGDIR', '/tmp/failure-simple-plots')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
VARIABLES = {
    'mass': ('Mass', 'g', 1000),
    'object_friction': ('Object friction', 'coefficient', 1),
    'size': ('Size', 'mm', 1000),
    'shape': ('Shape', 'category', 1),
    'com': ('COM X offset', 'mm', 1000),
    'goal_height': ('Lift height', 'cm', 100),
    'finger_friction': ('Finger friction', 'coefficient', 1),
    'table_friction': ('Table friction', 'coefficient', 1),
}


def settings(condition):
    p = condition['properties']
    return dict(mass=p['mass_kg'], object_friction=p['static_friction'],
                size=p['size_xyz_m'][0], shape=p['shape'], com=p['com_offset_m'][0],
                goal_height=condition['goal_clearance_m'], finger_friction=p['finger_friction'],
                table_friction=p['table_friction'])


def read_requests(path):
    """Only the Markdown table under '## Plots' controls what is generated."""
    text = Path(path).read_text()
    match = re.search(r'^## Plots\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if not match:
        raise ValueError('Markdown needs a section named ## Plots')
    table = [line.strip() for line in match[1].splitlines() if line.strip().startswith('|')]
    cells = [[cell.strip().strip('`') for cell in line.strip('|').split('|')] for line in table]
    if len(cells) < 3 or cells[0] != ['Plot', 'Variables', 'Conditions', 'Reference', 'Title']:
        raise ValueError('Expected Plot | Variables | Conditions | Reference | Title table')
    requests = []
    for values in cells[2:]:
        if len(values) != 5:
            raise ValueError('Each plot row needs exactly five cells; do not use | in titles')
        name, variables, conditions, reference, title = values
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', name):
            raise ValueError('Plot names must use lowercase letters, digits, underscores or hyphens')
        variables = [v.strip() for v in variables.split(',')]
        if not variables or set(variables) - set(VARIABLES) or len(set(variables)) != len(variables):
            raise ValueError(f'{name}: invalid or repeated variable name')
        ids = []
        for part in conditions.split(','):
            part = part.strip()
            if re.fullmatch(r'C\d{2}-C\d{2}', part):
                low, high = [int(x[1:]) for x in part.split('-')]
                if low > high:
                    raise ValueError('Condition ranges must ascend')
                ids.extend(f'C{i:02d}' for i in range(low, high + 1))
            elif re.fullmatch(r'C\d{2}', part):
                ids.append(part)
            else:
                raise ValueError(f'{name}: invalid condition list {part!r}')
        if reference.lower() not in ('yes', 'no'):
            raise ValueError('Reference must be yes or no')
        if not title:
            raise ValueError('Every plot needs a title')
        requests.append(dict(name=name, variables=variables, conditions=sorted(set(ids)),
                             reference=reference.lower() == 'yes', title=title))
    if not requests or len({r['name'] for r in requests}) != len(requests):
        raise ValueError('Need nonempty uniquely named plot requests')
    return text, requests


def load_episodes(dataset):
    """Use original collection order and verify outcomes/properties against NPZs."""
    manifest = json.loads((dataset / 'manifest.json').read_text())
    index = json.loads((dataset / 'episodes.json').read_text())
    conditions = {f'C{i:02d}': c for i, c in enumerate(manifest['conditions'], 1)}
    ids = {c['condition_id']: key for key, c in conditions.items()}
    rows, hashes = [], {}
    for number, entry in enumerate(index, 1):
        name = entry['file']
        if Path(name).name != name or name in hashes:
            raise ValueError('Invalid or duplicate episode filename')
        path = dataset / name
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        with np.load(path, allow_pickle=False) as a:
            cid = ids[str(a['label__condition_id'])]
            if cid != ids[entry['condition_id']] or int(a['label__seed']) != entry['seed']:
                raise ValueError('Episode index disagrees with archive')
            success = bool(a['label__success_final'])
            if success != entry['success'] or str(a['meta__experiment_identity']) != manifest['identity']:
                raise ValueError('Outcome or experiment identity mismatch')
            actual = dict(mass=float(a['label__mass_kg']), object_friction=float(a['label__object_static_friction']),
                size=float(a['label__size_xyz_m'][0]), shape=str(a['label__shape']), com=float(a['label__com_offset_m'][0]),
                goal_height=float(a['label__goal_clearance_m']), finger_friction=float(a['label__finger_static_friction'].mean()),
                table_friction=float(a['label__table_static_friction']))
        expected = settings(conditions[cid])
        for variable in VARIABLES:
            equal = actual[variable] == expected[variable] if variable == 'shape' else np.isclose(actual[variable], expected[variable], rtol=1e-6, atol=1e-8)
            if not equal:
                raise ValueError('Physics readback differs from condition: ' + variable)
        rows.append(dict(episode=number, file=name, condition=cid, seed=entry['seed'], success=success,
                         values=expected, actual=actual))
    if len(index) != len(list(dataset.glob('*.npz'))):
        raise ValueError('Index does not cover every episode')
    return manifest, conditions, rows, hashes


def select(request, conditions, rows):
    """Explicit condition rows make each comparison transparent and editable."""
    nominal = next(key for key, c in conditions.items() if not c['changed_properties'])
    selected = set(request['conditions'])
    if request['reference']:
        selected.add(nominal)
    if selected - set(conditions):
        raise ValueError(f"{request['name']}: unknown conditions {selected - set(conditions)}")
    base = settings(conditions[nominal])
    for cid in selected:
        values = settings(conditions[cid])
        hidden = [v for v in VARIABLES if v not in request['variables'] and values[v] != base[v]]
        if hidden:
            raise ValueError(f"{request['name']}: {cid} also changes unlisted variables {hidden}")
    result = [row for row in rows if row['condition'] in selected]
    if not result:
        raise ValueError('Plot selection has no episodes')
    return result, sum(row['condition'] == nominal for row in result)


def draw(request, rows, total, nominal_count, output):
    fig, axes = plt.subplots(len(request['variables']), 1, sharex=True, squeeze=False,
                             figsize=(20, max(4, 2.4 * len(request['variables']))))
    x = np.array([r['episode'] for r in rows])
    success = np.array([r['success'] for r in rows])
    for variable, ax in zip(request['variables'], axes.flat):
        title, unit, scale = VARIABLES[variable]
        values = [r['values'][variable] for r in rows]
        if variable == 'shape':
            levels = sorted(set(values)); y = np.array([levels.index(v) for v in values])
            ax.set_yticks(range(len(levels)), levels); ax.set_ylim(-.35, len(levels) - .65)
        else:
            y = np.array(values) * scale; levels = sorted(set(y)); ax.set_yticks(levels)
            margin = max((max(levels) - min(levels)) * .2, .01)
            ax.set_ylim(min(levels) - margin, max(levels) + margin)
        for mask, color, marker, label in [(success, '#17864b', 'o', 'Success'), (~success, '#d43f3a', 'x', 'Failure')]:
            ax.scatter(x[mask], y[mask], c=color, marker=marker, s=19, linewidths=.85, alpha=.85, label=label, zorder=3)
        ax.set_xlim(.5, total + .5); ax.set_xticks([1, *range(50, total + 1, 50)])
        ax.set_ylabel(title + '\n(' + unit + ')'); ax.grid(alpha=.2)
    axes[0, 0].legend(loc='upper right', ncol=2)
    axes[-1, 0].set_xlabel(f'Original collection episode number 1–{total}; unrelated episodes are blank')
    fig.suptitle('\n'.join(textwrap.wrap(request['title'], 110)), fontsize=15)
    fig.text(.01, .01, f'{len(rows)} displayed attempts; {nominal_count} nominal references. Green = success; red = failure. Settings outside the listed variables stay nominal.', fontsize=9)
    fig.tight_layout(rect=(0, .06, 1, .94))
    fig.savefig(output, dpi=150); plt.close(fig)


def write_gallery(report, folder, finished=False):
    refresh = '' if finished else '<meta http-equiv="refresh" content="5">'
    combined = '<a href="combined.html"><b>Open all plots combined</b></a> · <a href="combined.png">Combined PNG</a>' if (folder/'combined.html').exists() else 'Individual plots appear below as they finish. The combined view is built at the end.'
    sections = [f'<!doctype html><html><head><meta charset="utf-8">{refresh}<title>Isolated experiment plots</title><style>body{{font:16px system-ui;margin:28px;max-width:1450px;color:#17202a}}img{{width:100%}}section{{margin:35px 0;border-top:1px solid #ddd}}a{{color:#175a99}}</style></head><body>',
        '<h1>Isolated experiment plots</h1>', f'<p>{"Complete" if finished else "Rendering"}: {len(report)} plots ready. {combined}</p>',
        '<p>Green circles succeed; red crosses fail. Original episode numbers are retained; unrelated trials are blank.</p><ul>']
    for r in report:
        sections.append(f'<li><a href="#{r["name"]}">{html.escape(r["title"])}</a> ({r["count"]} attempts)</li>')
    sections.append('</ul>')
    for r in report:
        sections.append(f'<section id="{r["name"]}"><h2>{html.escape(r["title"])}</h2><p>{r["successes"]}/{r["count"]} successes including {r["nominal_references"]} nominal references. Conditions: {", ".join(r["condition_ids"])}.</p><a href="{r["file"]}"><img loading="lazy" src="{r["file"]}" alt="{html.escape(r["title"])}"></a></section>')
    sections.append('</body></html>')
    (folder/'index.html').write_text('\n'.join(sections))


def update_run_list():
    root = HERE/'plots'
    if not root.exists():
        return
    runs = sorted((p for p in root.iterdir() if p.is_dir() and (p/'index.html').exists()), key=lambda p:p.stat().st_mtime, reverse=True)
    lines = ['<!doctype html><html><head><meta charset="utf-8"><title>Plot runs</title></head><body style="font:18px system-ui;margin:35px"><h1>Plot runs</h1><p>Each run has its own folder. Open individual plots while rendering; the combined view appears at the end.</p><ul>']
    for run in runs:
        link = f'<a href="{run.name}/combined.html">Combined view</a> · ' if (run/'combined.html').exists() else ''
        lines.append(f'<li><b>{html.escape(run.name)}</b> · {link}<a href="{run.name}/index.html">Individual plots</a></li>')
    lines.append('</ul></body></html>')
    (root/'index.html').write_text('\n'.join(lines))


def main():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=HERE/'plots.md')
    parser.add_argument('--dataset', type=Path, default=HERE.parent/'runs/failure_collection/varied_fixed40g')
    parser.add_argument('--output', type=Path, help='Optional run folder; otherwise create a fresh timestamped folder')
    parser.add_argument('--only', nargs='+', help='Generate only these Markdown plot names; default is every row')
    parser.add_argument('--check', action='store_true', help='Validate every Markdown row without drawing plots')
    args = parser.parse_args()
    text, all_requests = read_requests(args.plan)
    manifest, conditions, episodes, hashes = load_episodes(args.dataset)
    fingerprint = re.search(r'^Dataset fingerprint: `([^`]+)`',text,re.M)
    if fingerprint and fingerprint[1] != manifest['identity']:
        raise ValueError('Markdown condition IDs belong to a different experiment')
    all_selections = [(r,*select(r,conditions,episodes)) for r in all_requests]
    if args.only:
        unknown = set(args.only)-{r['name'] for r in all_requests}
        if unknown:
            parser.error('Unknown plot names: '+', '.join(sorted(unknown)))
    selections = [s for s in all_selections if not args.only or s[0]['name'] in args.only]
    covered = {row['condition'] for _,rows,_ in all_selections for row in rows}
    print(f'{len(all_requests)} Markdown rows; {len(covered)}/{len(conditions)} conditions covered; rendering {len(selections)} plots.',flush=True)
    if args.check:
        return
    output = args.output or HERE/'plots'/datetime.now(ZoneInfo('America/New_York')).strftime('run_%Y-%m-%d_%H%M%S_%f')
    output.mkdir(parents=True,exist_ok=True)
    previous = output/'selections.json'
    old = json.loads(previous.read_text()) if previous.exists() else []
    selected_names = {r['name'] for r,_,_ in selections}
    current = {r['name']:r for r in all_requests}
    # Preserve unaffected plots only for an explicit single-plot rebuild in an
    # existing run; changed Markdown rows must be generated before reappearing.
    byname = {}
    if args.only:
        for item in old:
            name = item['name']
            if name in current and name not in selected_names and all(item[k]==current[name][k] for k in ('variables','conditions','reference','title')) and (output/item['file']).exists():
                byname[name] = item
    for item in old:
        name = item['file']
        if Path(name).name == name and name.endswith('.png') and item['name'] not in current:
            (output/name).unlink(missing_ok=True)
    # Remove a stale combined view before updating any of its constituent plots.
    for name in ('combined.png','combined.html','combined_layout.json'):
        (output/name).unlink(missing_ok=True)
    order = {r['name']:i for i,r in enumerate(all_requests)}
    report = sorted(byname.values(),key=lambda r:order[r['name']])
    write_gallery(report,output)
    update_run_list()
    print('Run folder:',output,flush=True)
    for request,rows,refs in selections:
        draw(request,rows,len(episodes),refs,output/(request['name']+'.png'))
        byname[request['name']] = dict(**request,file=request['name']+'.png',count=len(rows),
            successes=sum(r['success'] for r in rows),nominal_references=refs,
            episodes=[r['episode'] for r in rows],condition_ids=sorted({r['condition'] for r in rows}))
        report = sorted(byname.values(),key=lambda r:order[r['name']])
        (output/'selections.json').write_text(json.dumps(report,indent=2)+'\n')
        write_gallery(report,output)
        print('Saved',request['name'],f'({len(rows)} attempts)',flush=True)
    for name,before in hashes.items():
        if hashlib.sha256((args.dataset/name).read_bytes()).hexdigest()!=before:
            raise RuntimeError('A source episode changed during plotting')
    with (output/'episodes.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['episode','file','condition','seed','success',*VARIABLES])
        for row in episodes:
            writer.writerow([row['episode'],row['file'],row['condition'],row['seed'],row['success'],*[row['actual'][v] for v in VARIABLES]])
    print('Building combined view from the saved PNGs...',flush=True)
    from combine_plots import combine
    combined = combine(output)
    write_gallery(report,output,finished=True)
    (output/'manifest.json').write_text(json.dumps(dict(plan_sha256=hashlib.sha256(text.encode()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        combiner_sha256=hashlib.sha256(Path(__file__).with_name('combine_plots.py').read_bytes()).hexdigest(),
        dataset=str(args.dataset.resolve()),source_episode_sha256=hashes,source_unchanged=True,
        requested_plots=sorted(selected_names),plot_count=len(report),combined=combined),indent=2)+'\n')
    update_run_list()
    print(f'Done: {len(report)} plots + one combined image/view. Original episode hashes unchanged.',flush=True)


if __name__=='__main__':
    main()

"""Group failed attempts by observed responses to exact matched interventions.

No motion-based clustering, named failure taxonomy, estimator or new rollouts.
Only recorded final outcomes from a complete mass/friction grid are used.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import html
import itertools
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from robot_adaptation.paths import ROOT


def canonical(value):
    return round(float(value),12)


def save_json(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def save_csv(path,rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def find_grid(conditions,masses,frictions):
    nominal=next(c for c in conditions if not c['changed_factors'])['factor_values']
    grid={}
    for c in conditions:
        v=c['factor_values']
        if any(v[k]!=nominal[k] for k in nominal if k not in ('mass','object_friction')):
            continue
        key=(canonical(v['mass']),canonical(v['object_friction']))
        if key[0] in masses and key[1] in frictions:
            if key in grid:raise ValueError('Duplicate physical setting')
            grid[key]=c
    missing=set(itertools.product(masses,frictions))-set(grid)
    if missing:raise ValueError('Untested settings cannot be treated as failures. Missing grid cells: '+str(sorted(missing)))
    return grid


def read_grid(dataset,grid,manifest):
    entries=json.loads((dataset/'episodes.json').read_text())
    index={}
    for row in entries:
        key=(row['condition_id'],int(row['seed']))
        if key in index:raise ValueError('Duplicate condition/seed')
        index[key]=row
    seeds=list(range(manifest['config']['start_seed'],manifest['config']['start_seed']+manifest['config']['seed_count']))
    records={};reference={};hashes={}
    for (mass,friction),condition in sorted(grid.items()):
        for seed in seeds:
            key=(condition['condition_id'],seed)
            if key not in index:raise ValueError('Missing matched seed; no imputation allowed: '+str(key))
            row=index[key];name=row['file']
            if Path(name).name!=name:raise ValueError('Invalid filename')
            path=dataset/name
            with np.load(path,allow_pickle=False) as d:
                if str(d['label__condition_id'])!=key[0] or int(d['label__seed'])!=seed:raise ValueError('Index mismatch')
                if str(d['meta__experiment_identity'])!=manifest['identity']:raise ValueError('Experiment mismatch')
                if str(d['meta__checkpoint_sha256'])!=manifest['checkpoint_sha256']:raise ValueError('Policy changed')
                if not np.isclose(float(d['label__mass_kg']),mass,rtol=1e-6,atol=1e-9):raise ValueError('Mass readback mismatch')
                if not np.isclose(float(d['label__object_static_friction']),friction,rtol=1e-6,atol=1e-9):raise ValueError('Friction readback mismatch')
                success=bool(d['label__success_final'])
                if success!=row['success']:raise ValueError('Outcome mismatch')
                reset=(d['label__initial_object_pose_world_m_wxyz'].copy(),d['input__joint_position_rad_m'][0].copy(),
                       d['input__goal_position_world_m'].copy(),d['meta__state_time_s'].copy(),
                       d['input__reported_mass_kg'].copy())
                if seed in reference:
                    for before,after in zip(reference[seed],reset):
                        if not np.array_equal(before,after):raise ValueError('Unmatched initial state, goal, timing or supplied estimate')
                else:reference[seed]=reset
            hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
            records[(mass,friction,seed)]=dict(episode=row['episode_id'],file=name,seed=seed,mass=mass,friction=friction,success=success)
    return seeds,records,hashes


def observed_profile(source,records,masses,frictions):
    """Potential outcomes are LOOKUPS of observed trials, never inferred values.

    Setting a property to its existing value is a no-change control. Its observed
    failure is retained in the response vector but marked as not an intervention.
    """
    responses=[]
    for variable,values in [('mass',masses),('object_friction',frictions)]:
        for value in values:
            target=(value,source['friction'],source['seed']) if variable=='mass' else (source['mass'],value,source['seed'])
            if target not in records:raise ValueError('Missing counterfactual match; do not fill it with zero')
            match=records[target]
            current=source['mass'] if variable=='mass' else source['friction']
            responses.append(dict(variable=variable,target_value=value,changed=value!=current,
                                  success=match['success'],target_episode=match['episode']))
    return responses


def build_profiles(records,masses,frictions):
    failed=[r for _,r in sorted(records.items()) if not r['success']]
    responses={r['episode']:observed_profile(r,records,masses,frictions) for r in failed}
    signatures={e:''.join('1' if r['success'] else '0' for r in rr) for e,rr in responses.items()}
    ids={signature:f'R{i+1:02d}' for i,signature in enumerate(sorted(set(signatures.values())))}
    rows=[];evidence=[]
    for source in failed:
        profile=ids[signatures[source['episode']]]
        outcomes=responses[source['episode']]
        joint=[r for r in records.values() if r['seed']==source['seed'] and r['mass']!=source['mass'] and
               r['friction']!=source['friction'] and r['success']]
        minimum=1 if any(r['changed'] and r['success'] for r in outcomes) else (2 if joint else None)
        row=dict(episode=source['episode'],file=source['file'],seed=source['seed'],source_mass_kg=source['mass'],
                 source_object_friction=source['friction'],response_group=profile,signature=signatures[source['episode']],
                 mass_values_restoring_success_kg=json.dumps([r['target_value'] for r in outcomes if r['variable']=='mass' and r['changed'] and r['success']]),
                 friction_values_restoring_success=json.dumps([r['target_value'] for r in outcomes if r['variable']=='object_friction' and r['changed'] and r['success']]),
                 minimum_changed_factors_among_tested_successes=minimum,
                 successful_joint_settings=json.dumps([[r['mass'],r['friction']] for r in joint]))
        rows.append(row)
        for result in outcomes:evidence.append(dict(source_episode=source['episode'],response_group=profile,seed=source['seed'],**result))
    summaries=[]
    for signature,profile in ids.items():
        subset=[r for r in rows if r['response_group']==profile]
        summaries.append(dict(response_group=profile,signature=signature,failed_cases=len(subset),
            distinct_seeds=len({r['seed'] for r in subset}),
            source_settings=json.dumps(sorted({(r['source_mass_kg'],r['source_object_friction']) for r in subset})),
            tested_joint_change_needed_cases=sum(r['minimum_changed_factors_among_tested_successes']==2 for r in subset),
            no_tested_success_cases=sum(r['minimum_changed_factors_among_tested_successes'] is None for r in subset)))
    return rows,evidence,summaries


def run(args):
    masses=sorted({canonical(x) for x in args.mass_values});frictions=sorted({canonical(x) for x in args.friction_values})
    if len(masses)<2 or len(frictions)<2 or not np.isfinite(masses+frictions).all() or min(masses+frictions)<=0:
        raise ValueError('Need at least two finite positive values per variable')
    manifest=json.loads((args.dataset/'manifest.json').read_text())
    if manifest['status']!='complete':raise ValueError('Use a completed indexed collection')
    grid=find_grid(manifest['conditions'],masses,frictions)
    seeds,records,hashes=read_grid(args.dataset,grid,manifest)
    rows,evidence,summaries=build_profiles(records,masses,frictions)
    if not rows:raise ValueError('No failed cases in this grid')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    save_csv(output/'failure_response_profiles.csv',rows)
    save_csv(output/'matched_intervention_evidence.csv',evidence)
    save_csv(output/'response_groups.csv',summaries)
    save_csv(output/'observed_grid.csv',list(records.values()))
    # Seed-level repetition check: rows within a seed are dependent and are NOT
    # counted as independent tests of a classifier or of statistical significance.
    seed_checks=[]
    for seed in seeds:
        held=[r for r in rows if r['seed']==seed]
        seen={r['signature'] for r in rows if r['seed']!=seed}
        seed_checks.append(dict(seed=seed,failed_cases=len(held),profiles_seen_in_other_seeds=sum(r['signature'] in seen for r in held)))
    cases_with_joint=sum(r['minimum_changed_factors_among_tested_successes']==2 for r in rows)
    routes=Counter()
    for row in rows:
        mass_helped=bool(json.loads(row['mass_values_restoring_success_kg']))
        friction_helped=bool(json.loads(row['friction_values_restoring_success']))
        route=('either_variable_alone' if mass_helped and friction_helped else
               'mass_change_only_among_tested_single_changes' if mass_helped else
               'friction_change_only_among_tested_single_changes' if friction_helped else
               'joint_change_only_within_tested_grid' if row['minimum_changed_factors_among_tested_successes']==2 else
               'no_tested_success')
        routes[route]+=1
    report=dict(method='Exact equivalence of measured intervention-response vectors',
        source_dataset=str(args.dataset.resolve()),source_dataset_identity=manifest['identity'],
        physical_policy='Existing frozen custom policy; supplied mass estimate remains 40g',
        mass_values_kg=masses,object_friction_values=frictions,seeds=seeds,
        observed_settings=len(grid),observed_episodes=len(records),failed_source_cases=len(rows),
        success_episodes=sum(r['success'] for r in records.values()),response_groups=len(summaries),
        groups=summaries,tested_success_routes=dict(routes),seed_repetition_checks=seed_checks,
        cases_with_no_single_factor_success_but_tested_joint_success=cases_with_joint,
        missing_matches=0,initial_pose_robot_goal_timing_and_estimate_matched=True,
        notes=['Group labels describe observed responses, not unique physical mechanisms.',
               '1 means recorded success for the same seed at that target setting; 0 means recorded failure.',
               'No-change settings are controls, flagged changed=false; reusing their outcome adds no independent evidence.',
               'All other experiment factors stay nominal. Mass changes also derive inertia; object friction changes static and sliding friction together.',
               'Joint success after no single-factor success is only a conclusion within the tested levels, not proof that no other single change could work.',
               'Each seed contributes several dependent failures and reused targets. Seed repetition is descriptive, not classification accuracy or significance.',
               'No trajectory clustering, old failure labels, estimator, policy training or new rollouts are used.',
               'No environmental change is interpreted as a tested estimator-input correction. Those are different interventions.',
               'Profiles are specific to this frozen policy, task, intervention levels and success definition.'],
        status='descriptive_intervention_response_groups_not_validated_mechanism_labels')
    save_json(output/'summary.json',report)
    labels=[f'Mass → {m*1000:g} g' for m in masses]+[f'Friction → {f:g}' for f in frictions]
    matrix=np.array([[int(v) for v in group['signature']] for group in summaries])
    fig,ax=plt.subplots(figsize=(11,max(4,.6*len(summaries))),constrained_layout=True)
    ax.imshow(matrix,cmap=ListedColormap(['#d96459','#17864b']),vmin=0,vmax=1,aspect='auto')
    ax.set_xticks(range(len(labels)),labels,rotation=25,ha='right')
    ax.set_yticks(range(len(summaries)),[f'{g["response_group"]}: {g["failed_cases"]} cases, {g["distinct_seeds"]} seeds' for g in summaries])
    for i in range(len(summaries)):
        for j in range(len(labels)):ax.text(j,i,'Success' if matrix[i,j] else 'Failure',ha='center',va='center',color='white',fontsize=9)
    ax.set_title('Failures grouped by observed response to matched parameter settings')
    fig.savefig(output/'response_profiles.png',dpi=150);plt.close(fig)
    counts=np.array([[sum(records[(mass,friction,seed)]['success'] for seed in seeds) for friction in frictions] for mass in masses])
    fig,ax=plt.subplots(figsize=(7,5),constrained_layout=True)
    image=ax.imshow(counts/len(seeds),vmin=0,vmax=1,cmap='RdYlGn',aspect='auto')
    ax.set_xticks(range(len(frictions)),[f'{f:g}' for f in frictions]);ax.set_yticks(range(len(masses)),[f'{m*1000:g}' for m in masses])
    ax.set(xlabel='Object friction',ylabel='Actual mass (g)',title='Complete matched grid: success counts')
    for i in range(len(masses)):
        for j in range(len(frictions)):ax.text(j,i,f'{counts[i,j]}/{len(seeds)}',ha='center',va='center',fontsize=18)
    fig.colorbar(image,ax=ax,label='Success rate');fig.savefig(output/'success_grid.png',dpi=150);plt.close(fig)
    # Every source file is checked again after all analysis; nothing writes to it.
    for name,expected in hashes.items():
        if hashlib.sha256((args.dataset/name).read_bytes()).hexdigest()!=expected:raise RuntimeError('Source episode changed')
    save_json(output/'manifest.json',dict(script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        dataset_manifest_sha256=hashlib.sha256((args.dataset/'manifest.json').read_bytes()).hexdigest(),
        source_episode_sha256=hashes,source_unchanged=True))
    text=(f'# Intervention-response test\n\n{len(records)} recorded attempts across {len(grid)} mass/friction settings and {len(seeds)} seeds. '
        f'{len(rows)} failed cases form {len(summaries)} observed response profiles.\n\n'
        'No failure names were supplied: each group contains failed cases with the same recorded target-setting outcomes. '
        'Changing mass keeps friction fixed; changing friction keeps mass fixed. Joint settings are checked separately. '
        'No-change targets are marked as controls in the evidence CSV. No missing trial is assumed to have failed.\n\n'
        f'{cases_with_joint} failed cases had no successful single-variable target among these levels, but had a successful tested joint change. '
        'This is a bounded experimental result, not a universal claim that both parameters must change.\n\n'
        'These are physical interventions on the simulator, not grip-command changes or updates to an estimated policy input. '
        'All selected trials come from the custom-policy dataset, not the stock policy.\n\n'
        'Different response profiles do not prove distinct physical mechanisms; equal profiles need not mean equal causes. '
        'Repeatability across these ten seeds is descriptive. The next test is finer intervention levels and additional held-out starts.\n')
    (output/'METHOD_AND_RESULTS.md').write_text(text)
    table='<table><tr><th>Group</th><th>Failed cases</th><th>Distinct seeds</th><th>Response vector</th></tr>'
    for g in summaries:table+=f'<tr><td>{g["response_group"]}</td><td>{g["failed_cases"]}</td><td>{g["distinct_seeds"]}</td><td>{g["signature"]}</td></tr>'
    table+='</table>'
    page='<!doctype html><meta charset="utf-8"><title>Intervention-response groups</title><style>body{font:17px system-ui;max-width:1150px;margin:30px auto}img{width:100%}pre{white-space:pre-wrap}td,th{padding:8px;border-bottom:1px solid #ddd}</style>'
    page+='<h1>Failure groups defined by experimental responses</h1><pre>'+html.escape(text)+'</pre>'+table
    route_table='<h2>Which tested physical changes restored success?</h2><table><tr><th>Observed route</th><th>Failed cases</th></tr>'
    for route,count in routes.items():route_table+=f'<tr><td>{html.escape(route.replace("_"," "))}</td><td>{count}</td></tr>'
    page+=route_table+'</table><p>These counts describe alternatives for the 51 failed source cases; target trials are reused and are not independent new experiments.</p>'
    page+='<h2>Observed response patterns</h2><p>Green = recorded success; red = recorded failure. Columns are shared target settings, not newly simulated attempts.</p><img src="response_profiles.png">'
    page+='<h2>Individual and joint parameter effects</h2><img src="success_grid.png">'
    page+='<p><a href="failure_response_profiles.csv">Each failed case and its successful alternatives</a> · <a href="matched_intervention_evidence.csv">Exact matched-trial evidence</a> · <a href="summary.json">Summary and limits</a></p>'
    (output/'index.html').write_text(page)
    print(json.dumps(dict(output=str(output),observed_episodes=len(records),failed_cases=len(rows),response_groups=len(summaries),tested_joint_change_needed=cases_with_joint)),flush=True)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=ROOT/'runs/failure_collection/dense_single_pair_fixed40g')
    parser.add_argument('--mass-values',type=float,nargs='+',default=[.04,.1,.5])
    parser.add_argument('--friction-values',type=float,nargs='+',default=[.1,.4,1.])
    parser.add_argument('--output',type=Path,default=ROOT/'runs/failure_discovery'/datetime.now().strftime('response_%Y%m%d_%H%M%S_%f'))
    run(parser.parse_args())


if __name__=='__main__':
    main()

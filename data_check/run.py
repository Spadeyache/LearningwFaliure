#!/usr/bin/env python3
"""Generate all A–H diagnostics from the retained dataset; never modify episodes."""
import os
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'.deps'))
os.environ.setdefault('MPLCONFIGDIR','/tmp/failure-data-check-mpl')
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import csv
import html
import json
import numpy as np
from PIL import Image
from threadpoolctl import threadpool_limits
from data import load_dataset,sha256,CHANNELS,UNITS,FACTORS,factor_values
from models import analyze
from plots import Plotter


def clean(value):
    if isinstance(value,np.ndarray):return clean(value.tolist())
    if isinstance(value,np.generic):return clean(value.item())
    if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [clean(v) for v in value]
    if isinstance(value,float) and not np.isfinite(value):return None
    return value


def write_json(path,value):
    Path(path).write_text(json.dumps(clean(value),indent=2,allow_nan=False)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dataset',type=Path,default=HERE.parent/'runs/failure_collection/varied_fixed40g')
    ap.add_argument('--output',type=Path,default=HERE/'plots')
    sections=('coverage','variables','traces','measurements','atlas','classification','gripper','confounds')
    ap.add_argument('--sections',nargs='+',choices=sections,default=list(sections),help='Regenerate selected sections after a complete run')
    args=ap.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    derived=out.parent/'derived';derived.mkdir(exist_ok=True)
    print('Loading retained episode files',flush=True);d=load_dataset(args.dataset)
    if not np.allclose(d['gap'][d['single']=='nominal'],0,atol=1e-10):raise AssertionError('Nominal gap is nonzero')
    with (out/'conditions.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['plot_id','condition_id','description','design_families',*FACTORS,'episodes','successes'])
        for i,c in enumerate(d['conditions']):
            vals=factor_values(c);ix=d['condition']==i
            writer.writerow([f'C{i+1:02d}',c['condition_id'],d['descriptions'][i],';'.join(c['design_families']),*[vals[k] for k in FACTORS],int(ix.sum()),int(d['success'][ix].sum())])
    with (out/'episodes.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['file','condition','seed','single_variable_or_group','changed_factors','success','rule','lift_time_s','nominal_lift_time_s','reset_matches_nominal'])
        for r in d['records']:writer.writerow([r['path'].name,f"C{r['condition']+1:02d}",r['seed'],r['single'],';'.join(r['active']),r['success'],r['rule'],r['lift_time'],r['nominal_lift_time'],r['reset_matches_nominal']])
    np.savez_compressed(derived/'gaps.npz',residual=d['gap'],residual_channels=np.array(CHANNELS),units=np.array(UNITS),
        residual_valid_mask=d['valid'],time_s=d['time'],lift_aligned_residual=d['lift_gap'],lift_valid_mask=d['lift_valid'],
        lift_relative_time_s=d['lift_time'],episode_files=np.array([r['path'].name for r in d['records']]),
        matched_nominal_files=np.array([f"{d['baseline']['condition_id']}_seed{r['seed']}.npz" for r in d['records']]),
        nominal_lift_time_s=np.array([r['nominal_lift_time'] for r in d['records']]),
        nominal_reset_match=np.array([r['reset_matches_nominal'] for r in d['records']]))
    print('Seed-grouped model evaluation (no training changes to robot policy)',flush=True)
    with threadpool_limits(limits=1):m=analyze(d)
    p=Plotter(d,m,out)
    old_entries=[]
    if set(args.sections)!=set(sections):
        old=json.loads((out/'analysis_manifest.json').read_text())
        if old['source_episode_sha256']!=d['hashes']:raise ValueError('Partial regeneration requires the same input dataset')
        previous=json.loads((out/'scores.json').read_text());p.divergence=previous['divergence'];p.geometry_transfer=previous['geometry_transfer'];old_entries=old['entries']
    for method in args.sections:
        print('Generating',method,flush=True);getattr(p,method)()
    from episode_parameters import generate
    p.entries.extend(generate(args.dataset,out))
    combined={e['file']:e for e in old_entries}
    combined.update({e['file']:e for e in p.entries});p.entries=[combined[k] for k in sorted(combined)]
    scores=dict(dataset=str(args.dataset.resolve()),episodes=len(d['records']),successes=int(d['success'].sum()),
        failures=int((~d['success']).sum()),single_variable_episodes=len(m['indices']),
        class_labels=FACTORS,channels=CHANNELS,channel_units=UNITS,
        interpretation='Predict changed physical variable; not individual causal diagnosis or deployment validation.',
        controls='5-fold GroupKFold by seed; training-fold scaler; training-fold channel ranking; logistic C=1; balanced class weights.',
        gap_alignment='Shifted minus same-seed nominal at same elapsed time; orientation uses log(R_shift R_nominal^-1). Diagnostic lift alignment shifts both by nominal lift time.',
        missing_nominal_lift_seeds=sorted(set(r['seed'] for r in d['records'] if not np.isfinite(r['nominal_lift_time']))),
        nonidentical_reset_episodes=sum(not r['reset_matches_nominal'] for r in d['records']),
        nonidentical_reset_note='Geometry changes initial support height and goal position; lift target also changes goal. These gaps include those initial/task differences.',
        selected_channel_cv=m['selected'],all_channel_cv=m['all'],channel_cv=dict(zip(CHANNELS,m['channel_scores'])),
        accuracy_vs_channel_count={i+1:r for i,r in enumerate(m['counts'])},time_since_nominal_lift=m['time_scores'],
        confusion=m['confusion'],dynamic_control_cv=m['dynamic'],dynamic_failures_cv=m['dynamic_failures'],
        pca_explained_variance=m['pca_variance'],single_to_combo=m['combo'],
        divergence=p.divergence,geometry_transfer=p.geometry_transfer,
        limitations=['10 seeds; small, correlated dataset. No independent deployment test.',
            'Magnitude coverage does not contain the requested 0.5/2/4 series for mass or object friction.',
            'Classifier labels are interventions, not ground-truth failure causes. Successes included unless explicitly failure-only.',
            'Matched nominal trajectories are extra information unavailable in a single real-world deployment episode.',
            'Nominal-lift alignment is sim-only diagnostic conditioning; use reset alignment for complete coverage.',
            'No actuator-effort trace: commanded ceiling use does not establish true motor saturation.',
            'No detected failure onset is replaced with a fabricated event time.',
            'All plots are exploratory; selecting channels or thresholds using these scores requires a new independent test.'])
    write_json(out/'scores.json',scores)
    with (out/'predictions.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['file','seed','actual_shifted_variable','predicted_shifted_variable'])
        for i,pred in zip(m['indices'],m['selected']['pred']):writer.writerow([d['records'][i]['path'].name,int(d['seed'][i]),d['single'][i],pred])
    for entry in p.entries:
        with Image.open(out/entry['file']) as im:im.verify()
    after={name:sha256(args.dataset/name) for name in d['hashes']}
    if after!=d['hashes']:raise RuntimeError('Source episode hashes changed during analysis')
    versions={}
    import importlib.metadata
    for name in ('numpy','scipy','matplotlib','scikit-learn'):versions[name]=importlib.metadata.version(name)
    write_json(out/'analysis_manifest.json',dict(source_episode_sha256=d['hashes'],
        analysis_code_sha256={f.name:sha256(f) for f in HERE.glob('*.py')},versions=versions,
        source_unchanged=True,plot_count=len(p.entries),entries=p.entries))
    from inventory import generate_inventory
    generate_inventory(args.dataset,out)
    overview=[e for e in p.entries if '/' not in e['file']];detail=[e for e in p.entries if '/' in e['file']]
    content=['<!doctype html><html><head><meta charset="utf-8"><title>Pick-and-lift data check</title>',
        '<style>body{font:16px system-ui;margin:32px;max-width:1250px;background:#f5f7fa;color:#17202a}img{max-width:100%;background:white}section{background:white;padding:20px;margin:22px 0;border-radius:10px}p{line-height:1.5}a{color:#175a99}nav a{margin-right:12px}</style></head><body>',
        '<h1>Pick-and-lift data check</h1>',
        f'<p>{len(d["records"])} episodes · {int(d["success"].sum())} successes · {int((~d["success"]).sum())} failures. Fixed reported mass: 40 g.</p>',
        '<p><b>Nominal is not guaranteed success:</b> only 4 of its 10 attempts succeeded. Gaps compare against nominal conditions, not an ideal successful demonstration.</p>',
        '<p><b>Read first:</b> Labels identify which properties were changed, not proven causes of individual failures. All classification uses held-out seeds. Gaps require a matched nominal run. Missing experiments are not simulated or invented.</p>',
        '<p><a href="experiment_inventory.html">Exhaustive experiment inventory</a> · <a href="scores.json">Scores and limitations</a> · <a href="conditions.csv">Condition key</a> · <a href="episodes.csv">Episode index</a> · <a href="predictions.csv">Held-out predictions</a></p>',
        '<nav>'+''.join(f'<a href="#{e["file"]}">{e["title"].split(" · ")[0]}</a>' for e in overview)+'</nav>']
    for e in overview:content.append(f'<section id="{e["file"]}"><h2>{html.escape(e["title"])}</h2><p>{html.escape(e["note"])}</p><a href="{e["file"]}"><img loading="lazy" src="{e["file"]}" alt="{html.escape(e["title"])}"></a></section>')
    content.append('<h2>Detailed condition traces and measured parameter pairs</h2><ul>')
    for e in detail:content.append(f'<li><a href="{e["file"]}">{html.escape(e["title"])}</a></li>')
    content.append('</ul></body></html>');(out/'index.html').write_text('\n'.join(content))
    print(json.dumps(dict(plots=len(p.entries),selected_accuracy=m['selected']['accuracy'],selected_balanced_accuracy=m['selected']['balanced_accuracy'],source_unchanged=True,index=str(out/'index.html'))),flush=True)


if __name__=='__main__':main()

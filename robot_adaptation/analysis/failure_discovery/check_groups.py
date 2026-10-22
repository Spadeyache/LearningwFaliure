"""Validate discovered groups across seed splits and reveal controlled settings."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import adjusted_rand_score
from .analyze import ROOT, SIGNALS, extract, fit_model, project, predict, safe_silhouette, save_csv
import matplotlib.pyplot as plt


def check(folder):
    rows=list(csv.DictReader((folder/'episode_metrics.csv').open()))
    report=json.loads((folder/'scores.json').read_text())
    frames=[];descriptions=[]
    for row in rows:
        path=Path(report['source_dataset'])/(row['episode']+'.npz')
        with np.load(path,allow_pickle=False) as data:
            signals={k:data[k].copy() for k in SIGNALS}
        frames.append(extract(signals,report['resampled_points'])[0])
        obj=signals['input__object_pose_world_m_wxyz'][:,:3]
        descriptions.append(dict(episode=row['episode'],group=row['cluster'],
            peak_object_rise_m=float((obj[:,2]-obj[0,2]).max()),
            final_object_rise_m=float(obj[-1,2]-obj[0,2]),
            final_object_xy_displacement_m=float(np.linalg.norm(obj[-1,:2]-obj[0,:2]))))
    save_csv(folder/'behavior_descriptors.csv',descriptions)
    x=np.stack(frames).reshape(len(rows),-1)
    seeds=np.array([int(r['seed']) for r in rows]); failures=np.array([r['original_success']=='False' for r in rows])
    reference=np.array([int(r['cluster'].split('_')[-1]) if failures[i] else -1 for i,r in enumerate(rows)])
    # Freeze the original grouping for later assignment, rather than refitting it
    # whenever another physical setting is analyzed. All arrays are pickle-free.
    original_train=failures & ~np.isin(seeds,report['held_out_seeds'])
    original_model=fit_model(x[original_train],report['chosen_groups'],report['random_seed'])
    np.testing.assert_array_equal(predict(original_model,x[failures])+1,reference[failures])
    scaler,pca,cluster=original_model
    np.savez_compressed(folder/'candidate_model.npz',standardizer_mean=scaler.mean_,standardizer_scale=scaler.scale_,
        pca_mean=pca.mean_,pca_components=pca.components_,cluster_centers=cluster.cluster_centers_,
        channels=np.asarray(report['channels']),samples=np.asarray(report['resampled_points']))
    # Check the portable transform reproduces sklearn's group assignments.
    z=((x-scaler.mean_)/scaler.scale_-pca.mean_) @ pca.components_.T
    portable=np.linalg.norm(z[:,None,:]-cluster.cluster_centers_[None,:,:],axis=-1).argmin(axis=1)
    np.testing.assert_array_equal(portable,predict(original_model,x))
    folds=[]
    for held_seeds in np.array_split(np.unique(seeds),5):
        test=failures & np.isin(seeds,held_seeds);train=failures & ~np.isin(seeds,held_seeds)
        choices=[]
        for k in range(2,min(6,int(train.sum())//3)+1):
            model=fit_model(x[train],k,17)
            score=safe_silhouette(project(model,x[train]),model[2].labels_)
            if score is not None:choices.append((score,k,model))
        score,k,model=max(choices,key=lambda item:item[0])
        prediction=predict(model,x[test])
        folds.append(dict(held_out_seeds=held_seeds.tolist(),training_failures=int(train.sum()),
            held_out_failures=int(test.sum()),selected_groups=k,groups_present_on_holdout=len(np.unique(prediction)),
            held_out_silhouette=safe_silhouette(project(model,x[test]),prediction),
            agreement_with_reference_grouping_ari=float(adjusted_rand_score(reference[test],prediction))))
    validation=dict(folds=folds,mean_reference_agreement_ari=float(np.mean([f['agreement_with_reference_grouping_ari'] for f in folds])),
        interpretation='Assignment agreement, not failure-type accuracy. Reference groups share training data with some folds; this tests consistency, not an independent semantic ground truth.',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        frozen_model_sha256=hashlib.sha256((folder/'candidate_model.npz').read_bytes()).hexdigest())
    (folder/'seed_split_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    groups=sorted({r['cluster'] for r in rows if r['cluster']!='success_reference'})
    summaries=[]
    for group in groups:
        subset=[d for d in descriptions if d['group']==group]
        summaries.append(dict(group=group,episodes=len(subset),median_peak_rise_m=float(np.median([d['peak_object_rise_m'] for d in subset])),
            median_final_xy_displacement_m=float(np.median([d['final_object_xy_displacement_m'] for d in subset])),
            episodes_rising_above_5cm=sum(d['peak_object_rise_m']>.05 for d in subset)))
    save_csv(folder/'behavior_summary.csv',summaries)
    metadata={r['episode']:json.loads(r['full_condition_json']) for r in csv.DictReader((folder/'physical_settings_revealed_after_grouping.csv').open())}
    baseline={int(r['seed']):r for r in rows if not metadata[r['episode']]['changed_factors']}
    rates=[]
    for factor in report['single_factor_selection'] or []:
        values=sorted({metadata[r['episode']]['factor_values'][factor] for r in rows if set(metadata[r['episode']]['changed_factors'])<={factor}})
        for value in values:
            selected=[r for r in rows if set(metadata[r['episode']]['changed_factors'])<={factor} and metadata[r['episode']]['factor_values'][factor]==value]
            if {int(r['seed']) for r in selected}!=set(baseline):raise ValueError('Unmatched seed coverage')
            item=dict(factor=factor,value=value,attempts=len(selected),successes=sum(r['original_success']=='True' for r in selected))
            for group in groups:
                item[group+'_count']=sum(r['cluster']==group for r in selected)
                item[group+'_rate']=item[group+'_count']/len(selected)
                item[group+'_paired_entries']=sum(r['cluster']==group and baseline[int(r['seed'])]['cluster']!=group for r in selected)
                item[group+'_paired_exits']=sum(r['cluster']!=group and baseline[int(r['seed'])]['cluster']==group for r in selected)
            rates.append(item)
    save_csv(folder/'controlled_group_rates.csv',rates)
    if rates:
        variables=report['single_factor_selection'];fig,axes=plt.subplots(len(variables),1,figsize=(12,4*len(variables)),squeeze=False,constrained_layout=True)
        for factor,ax in zip(variables,axes.flat):
            subset=[r for r in rates if r['factor']==factor];n=np.array([r['attempts'] for r in subset]);bottom=np.zeros(len(subset));xs=np.arange(len(subset))
            for name,color in [('success_reference','#17864b')]+[(g,f'C{i}') for i,g in enumerate(groups)]:
                count=np.array([r['successes'] if name=='success_reference' else r[name+'_count'] for r in subset]);y=100*count/n
                ax.bar(xs,y,bottom=bottom,color=color,label='Success' if name=='success_reference' else name);bottom+=y
            vals=[r['value']*1000 if factor=='mass' else r['value'] for r in subset]
            ax.set_xticks(xs,[f'{v:g}' for v in vals]);ax.set(ylim=(0,100),ylabel='Percent of all 10 attempts',xlabel='Actual mass (g)' if factor=='mass' else factor.replace('_',' '),title='After grouping: '+factor.replace('_',' '));ax.legend(ncol=len(groups)+1)
        fig.savefig(folder/'controlled_group_rates.png',dpi=150);plt.close(fig)
    interpretation=(
        '# First failure-identification test\n\n'
        f'{len(rows)} attempts; {int(failures.sum())} failures. Physical settings and existing failure names were excluded from clustering.\n\n'
        f'Candidate groups: {report["group_counts"]}. Five seed-split checks give mean reference-assignment ARI {validation["mean_reference_agreement_ari"]:.3f}. '
        'ARI measures grouping agreement, not correctness of failure names.\n\n'
        '## What the groups look like\n\n'
        + '\n'.join(f'- {s["group"]}: {s["episodes"]} failures; median peak object rise {s["median_peak_rise_m"]*100:.1f} cm; '
                    f'median final sideways displacement {s["median_final_xy_displacement_m"]*100:.1f} cm. '
                    f'{s["episodes_rising_above_5cm"]}/{s["episodes"]} rise above 5 cm.' for s in summaries)
        + '\n\nThese are broad trajectory groups with overlap, not yet clean, mutually exclusive physical mechanisms. '
        'The first group contains both lifting and low-lift attempts. Representative GIFs replay recorded poses without running physics or a policy.\n\n'
        '## Controlled settings\n\n'
        'The rate plot reveals settings only after grouping. Every bar includes all ten matched starts, including successes. '
        'The CSV records paired entries/exits relative to the same-seed nominal run. These are effects on learned group assignments; '
        'they do not establish a unique physical cause or demonstrate that adding a parameter improves a policy. '
        'Mass changes also change derived inertia.\n\n'
        '## Next validation\n\n'
        'Inspect more examples and substructure inside the broad groups, test sensitivity to representation/timing, and replicate on additional conditions. '
        'Changing a representation to split desired names would not be independent discovery. No estimator, recovery or measurement-ranking stage has been enabled.\n')
    (folder/'IDENTIFICATION.md').write_text(interpretation)
    page=(folder/'index.html').read_text().split('<!-- GROUP CHECK -->')[0]
    page+='<!-- GROUP CHECK --><h2>Identification checks</h2><pre>'+html.escape(interpretation)+'</pre>'
    if rates:page+='<h2>Physical settings revealed after grouping</h2><img src="controlled_group_rates.png">'
    example_path=folder/'examples.json'
    if example_path.exists():
        page+='<h2>Recorded-pose examples (no new episodes)</h2>'
        for example in json.loads(example_path.read_text()):page+=f'<h3>{html.escape(example["group"])}</h3><img style="width:384px" src="{html.escape(example["file"])}">'
    page+='<p><a href="seed_split_validation.json">Seed-split validation</a> · <a href="controlled_group_rates.csv">Controlled group rates</a></p>'
    (folder/'index.html').write_text(page)
    print(json.dumps(dict(seed_split_validation=validation,behavior=summaries)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    check(parser.parse_args().folder)


if __name__=='__main__':
    main()

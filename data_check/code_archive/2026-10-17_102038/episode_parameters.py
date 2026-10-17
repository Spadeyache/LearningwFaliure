"""Parameter settings versus actual collection episode order, colored by outcome.

Pair views show JOINT SETTINGS, not invented unmeasured combinations or products.
"""
from pathlib import Path
from itertools import combinations
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data import FACTORS,FACTOR_NAMES,factor_values,sha256

SUCCESS='#17864b';FAIL='#d43f3a'
SCALES={'mass':1000,'size':1000,'com':1000,'goal_height':100}
UNITS={'mass':'g','object_friction':'coefficient','size':'mm','shape':'category','com':'mm',
       'goal_height':'cm','finger_friction':'coefficient','table_friction':'coefficient'}
NAMES=dict(zip(FACTORS,FACTOR_NAMES))


def label(f,v):
    return str(v) if isinstance(v,str) else f'{v*SCALES.get(f,1):g}'


def ordered_rows(dataset):
    dataset=Path(dataset);manifest=json.loads((dataset/'manifest.json').read_text())
    episodes=json.loads((dataset/'episodes.json').read_text());conditions={c['condition_id']:c for c in manifest['conditions']}
    rows=[];seen=set()
    for i,e in enumerate(episodes,1):
        path=dataset/e['file']
        if path.name in seen:raise ValueError('Duplicate episode')
        seen.add(path.name)
        with np.load(path,allow_pickle=False) as a:
            if bool(a['label__success_final'])!=e['success']:raise ValueError('Index outcome mismatch')
            if int(a['label__seed'])!=e['seed']:raise ValueError('Index seed mismatch')
            actual={'mass':float(a['label__mass_kg']),'object_friction':float(a['label__object_static_friction']),
                'size':float(a['label__size_xyz_m'][0]),'shape':str(a['label__shape']),
                'com':float(a['label__com_offset_m'][0]),'goal_height':float(a['label__goal_clearance_m']),
                'finger_friction':float(a['label__finger_static_friction'].mean()),
                'table_friction':float(a['label__table_static_friction'])}
            requested=factor_values(conditions[e['condition_id']])
            for f in FACTORS:
                if f=='shape':
                    if actual[f]!=requested[f]:raise ValueError('Shape readback mismatch')
                elif not np.isclose(actual[f],requested[f],rtol=1e-6,atol=1e-8):raise ValueError('Readback mismatch: '+f)
        # Canonical requested decimal levels avoid separating float32 readback roundoff.
        rows.append(dict(episode=i,file=e['file'],condition=e['condition_id'],seed=e['seed'],
                         success=e['success'],values=requested,actual=actual))
    if len(seen)!=len(list(dataset.glob('*.npz'))):raise ValueError('Collection index omits files')
    return manifest,rows


def scatter(ax,x,y,success):
    for ok,color,mark in [(True,SUCCESS,'o'),(False,FAIL,'x')]:
        mask=success==ok
        ax.scatter(x[mask],np.array(y)[mask],color=color,marker=mark,s=19,linewidths=.85,
                   alpha=.85,label='Success' if ok else 'Failure',zorder=3)
    ax.set_xlim(0.5,len(x)+.5);ax.set_xticks([1,*range(50,len(x)+1,50)])
    ax.grid(axis='y',alpha=.2);ax.set_xlabel('Episode number (actual collection order)')


def generate(dataset,out):
    dataset=Path(dataset);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    manifest,rows=ordered_rows(dataset);x=np.arange(1,len(rows)+1);ok=np.array([r['success'] for r in rows])
    boundaries=[i+.5 for i in range(1,len(rows)) if rows[i]['condition']!=rows[i-1]['condition']]
    entries=[]
    def save(fig,name,title,note):
        fig.suptitle(title,fontsize=15);fig.text(.01,.01,note,fontsize=9)
        fig.tight_layout(rect=(0,.04,1,.96));p=out/(name+'.png');p.parent.mkdir(exist_ok=True,parents=True)
        fig.savefig(p,dpi=150);plt.close(fig);entries.append(dict(file=name+'.png',title=title,note=note))
    fig,axes=plt.subplots(8,1,figsize=(20,20),sharex=True)
    for f,ax in zip(FACTORS,axes):
        values=[r['values'][f] for r in rows]
        if f=='shape':y=[['cube','sphere'].index(v) for v in values];ax.set_yticks([0,1],['cube','sphere']);ax.set_ylim(-.35,1.35)
        else:
            y=np.array(values)*SCALES.get(f,1);levels=sorted(set(y));ax.set_yticks(levels)
            margin=max((max(levels)-min(levels))*.2,.01);ax.set_ylim(min(levels)-margin,max(levels)+margin)
        scatter(ax,x,y,ok);ax.set_ylabel(NAMES[f]+'\n('+UNITS[f]+')');ax.set_xlabel('')
        for b in boundaries:ax.axvline(b,c='.8',lw=.35,zorder=0)
    axes[0].legend(loc='upper right',ncol=2);axes[-1].set_xlabel('Episode number 1–600 (collection order; each 10-episode block is one physical condition)')
    save(fig,'I01_parameters_vs_episode','Parameter values by episode · green success / red failure',
         'Each point is one attempt. Shared columns show all settings for that same attempt. All 600 trials shown; other parameters can vary together.')
    # Every pair of variables, with exact joint setting on the vertical axis.
    pair_entries=[]
    for a,b in combinations(FACTORS,2):
        levels=sorted(set((r['values'][a],r['values'][b]) for r in rows))
        yy=[levels.index((r['values'][a],r['values'][b])) for r in rows]
        fig,ax=plt.subplots(figsize=(20,max(4,len(levels)*.45)))
        scatter(ax,x,yy,ok);ax.set_yticks(range(len(levels)),[f'{label(a,v)} {UNITS[a]} | {label(b,w)} {UNITS[b]}' for v,w in levels]);ax.set_ylabel(f'{NAMES[a]} | {NAMES[b]}');ax.set_ylim(-.6,len(levels)-.4);ax.legend(loc='upper right',ncol=2)
        for z in boundaries:ax.axvline(z,c='.9',lw=.3,zorder=0)
        name=f'I02_pairs/{a}__{b}'
        save(fig,name,f'{NAMES[a]} + {NAMES[b]} joint settings by episode',
            'Only sampled joint settings appear. Other variables may also differ; this is an episode overview, not an isolated pair-effect estimate.')
        pair_entries.append(entries[-1])
    # Every complete physical combination actually tested.
    ci={c['condition_id']:j for j,c in enumerate(manifest['conditions'])};fig,ax=plt.subplots(figsize=(20,18))
    yy=[ci[r['condition']] for r in rows];scatter(ax,x,yy,ok);ax.set_yticks(range(len(ci)),[f'C{j+1:02d}' for j in range(len(ci))]);ax.invert_yaxis();ax.set_ylabel('Complete physical combination (see conditions.csv for all settings)');ax.legend(loc='upper right',ncol=2)
    save(fig,'I03_complete_combinations_vs_episode','All 60 tested physical combinations by episode',
         'One row per complete setting; 10 attempts per row. C01 is nominal. Unmeasured combinations are not included.')
    with (out/'episode_parameter_values.csv').open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['episode_number','file','condition_id','seed','success',*FACTORS])
        for r in rows:writer.writerow([r['episode'],r['file'],r['condition'],r['seed'],r['success'],*[r['actual'][f] for f in FACTORS]])
    from isolated_parameters import generate_isolated
    entries.extend(generate_isolated(manifest,rows,out))
    return entries


def main():
    import argparse
    root=Path(__file__).resolve().parent
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=root.parent/'runs/failure_collection/varied_fixed40g')
    parser.add_argument('--output',type=Path,default=root/'plots')
    args=parser.parse_args();entries=generate(args.dataset,args.output)
    from inventory import generate_inventory
    generate_inventory(args.dataset,args.output)
    # Extend the existing gallery/manifest without rerunning the statistical models.
    out=args.output;mp=out/'analysis_manifest.json'
    if mp.exists():
        import html
        m=json.loads(mp.read_text());known={e['file']:e for e in m['entries']};known.update({e['file']:e for e in entries});m['entries']=list(known.values());m['plot_count']=len(known)
        m['analysis_code_sha256']={f.name:sha256(f) for f in root.glob('*.py')};mp.write_text(json.dumps(m,indent=2)+'\n')
        ip=out/'index.html';text=ip.read_text();start='<!-- EPISODE-PARAMETER-VIEWS -->';end='<!-- END-EPISODE-PARAMETER-VIEWS -->'
        if start in text:text=text[:text.index(start)]+text[text.index(end)+len(end):]
        isolated=[e for e in entries if e['file'].startswith('J')]
        section=[start,'<section><h2>Start here: isolated situations</h2><p>Original episode axis and colors preserved. Each row or page excludes unrelated interventions; blank episode positions are intentional.</p>',
                 '<a href="J01_single_variable_overview.png"><img src="J01_single_variable_overview.png" alt="Isolated single-variable plots"></a><ul>'+''.join(f'<li><a href="{e["file"]}">{html.escape(e["title"])}</a></li>' for e in isolated if e['file']!='J01_single_variable_overview.png')+'</ul></section>','<section><h2>Parameter values versus episode · success / failure</h2><p>Episode numbering follows actual collection order. Green circles succeed; red crosses fail. Shared X positions refer to the same attempt.</p>',
                 '<p><a href="episode_parameter_values.csv">Episode-number lookup and actual values</a></p>',
                 '<a href="I01_parameters_vs_episode.png"><img src="I01_parameters_vs_episode.png" alt="Parameter values by episode colored by success"></a>',
                 '<h3>Every measured parameter pair</h3><ul>']
        for e in entries:
            if e['file'].startswith('I02_pairs/'):section.append(f'<li><a href="{e["file"]}">{html.escape(e["title"])}</a></li>')
        section+=['</ul><a href="I03_complete_combinations_vs_episode.png">All 60 complete combinations by episode</a>',
                  '<p>These plots expose patterns across trials. To isolate an individual parameter effect, use B1/B2 controls that hold the other settings fixed.</p></section>',end]
        text=text.replace('<h1>Pick-and-lift data check</h1>','<h1>Pick-and-lift data check</h1>\n'+'\n'.join(section))
        ip.write_text(text)
    print(f'Created {len(entries)} episode-parameter plots, including isolated single-variable and combination views.',flush=True)


if __name__=='__main__':main()

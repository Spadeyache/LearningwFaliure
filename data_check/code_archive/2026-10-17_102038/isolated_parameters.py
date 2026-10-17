"""Isolated experiment views: original episode positions, with unrelated trials blank."""
from collections import defaultdict
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from data import FACTORS,factor_values
from episode_parameters import NAMES,SCALES,UNITS,scatter


def generate_isolated(manifest,rows,out):
    out=Path(out);entries=[];selections=[]
    nominal=next(c for c in manifest['conditions'] if not c['changed_properties'])
    base=factor_values(nominal);byid={c['condition_id']:c for c in manifest['conditions']}
    active={c['condition_id']:tuple(f for f in FACTORS if factor_values(c)[f]!=base[f]) for c in manifest['conditions']}
    n=len(rows)
    def candidates(factors,mode='allowed',family=None):
        wanted=set(factors);result=[]
        for r in rows:
            changed=set(active[r['condition']])
            if not changed:result.append(r);continue
            include=(changed==wanted) if mode=='exact' else (changed<=wanted)
            if family is not None:include=include and family in byid[r['condition']]['design_families']
            if include:result.append(r)
        # Assert every unselected factor remains at its nominal setting.
        for r in result:
            assert all(r['values'][f]==base[f] for f in FACTORS if f not in wanted)
        return result
    def draw(ax,f,selected):
        x=np.array([r['episode'] for r in selected]);ok=np.array([r['success'] for r in selected]);values=[r['values'][f] for r in selected]
        if f=='shape':
            y=[['cube','sphere'].index(v) for v in values];ax.set_yticks([0,1],['cube','sphere']);ax.set_ylim(-.3,1.3)
        else:
            y=np.array(values)*SCALES.get(f,1);levels=sorted(set(y));ax.set_yticks(levels)
            margin=max((max(levels)-min(levels))*.2,.01);ax.set_ylim(min(levels)-margin,max(levels)+margin)
        scatter(ax,x,y,ok)
        # Shared helper normally infers width from sample count; preserve the
        # original global episode coordinates even when only 20/30 are present.
        ax.set_xlim(.5,n+.5);ax.set_xticks([1,*range(50,n+1,50)])
        ax.set_ylabel(f'{NAMES[f]}\n({UNITS[f]})');ax.grid(axis='x',alpha=.15)
    def page(factors,selected,name,title,note):
        if not any(active[r['condition']] for r in selected):return
        fig,axes=plt.subplots(len(factors),1,figsize=(20,max(4,len(factors)*2.4)),sharex=True,squeeze=False)
        for f,ax in zip(factors,axes.flat):draw(ax,f,selected)
        axes[0,0].legend(loc='upper right',ncol=2)
        for ax in axes.flat:ax.set_xlabel('')
        axes[-1,0].set_xlabel(f'Original collection episode number 1–{n}; excluded episodes are blank')
        fig.suptitle(title,fontsize=15);fig.text(.01,.01,f'{len(selected)} displayed attempts, including 10 nominal references. '+note,fontsize=9)
        fig.tight_layout(rect=(0,.06,1,.94));p=out/(name+'.png');p.parent.mkdir(parents=True,exist_ok=True);fig.savefig(p,dpi=150);plt.close(fig)
        entries.append(dict(file=name+'.png',title=title,note=note))
        selections.append(dict(file=name+'.png',factors=list(factors),episodes=[r['episode'] for r in selected],
                               nominal_episodes=[r['episode'] for r in selected if not active[r['condition']]],
                               condition_ids=sorted({r['condition'] for r in selected}),count=len(selected)))
    fig,axes=plt.subplots(8,1,figsize=(20,20),sharex=True)
    for f,ax in zip(FACTORS,axes):
        selected=candidates([f]);draw(ax,f,selected);ax.set_xlabel('')
        ax.set_title(f'Only {NAMES[f].lower()} changes · {len(selected)} attempts including nominal',loc='left',fontsize=10)
        page([f],selected,f'J01_single/{f}',f'{NAMES[f]} only · all other physical settings fixed',
             'Green success; red failure. The same ten starting seeds are reused across settings.')
    axes[0].legend(loc='upper right',ncol=2);axes[-1].set_xlabel(f'Original episode number 1–{n}; no unrelated runs shown')
    fig.suptitle('Single-variable tests only · each row excludes all other interventions',fontsize=15)
    fig.text(.01,.01,'Green success; red failure. The nominal 10 attempts appear in every row. Each variable row has its own filtered episode subset.',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.96));fig.savefig(out/'J01_single_variable_overview.png',dpi=150);plt.close(fig)
    entries.insert(0,dict(file='J01_single_variable_overview.png',title='Isolated single-variable tests · all eight variables',note='Only one variable differs from nominal in each row. Original episode numbers and success/failure colors are preserved.'))
    for a,b in manifest['config']['paired_factors']:
        for direction in ('together','opposite'):
            family=f'{direction}:{a}+{b}';selected=candidates([a,b],family=family)
            page([a,b],selected,f'J02_pairs/{a}__{b}__{direction}',
                 f'{NAMES[a]} + {NAMES[b]} · {"same" if direction=="together" else "opposite"}-direction changes only',
                 'All other physical settings fixed at nominal. Direction denotes ordered levels, not equal increments.')
        page([a,b],candidates([a,b]),f'J02_pairs/{a}__{b}__all_tested',
             f'{NAMES[a]} + {NAMES[b]} · all tested joint settings with other factors fixed',
             'Includes nominal, isolated changes and sampled two-factor combinations. Unmeasured settings stay absent.')
    groups=sorted({v for v in active.values() if len(v)>=2},key=lambda v:(len(v),v))
    for factors in groups:
        page(factors,candidates(factors,mode='exact'),'J03_combinations/'+'__'.join(factors),
             'Only this combination varies: '+' + '.join(NAMES[f] for f in factors),
             'Every displayed non-nominal attempt changes exactly these factors. Factors outside this set remain fixed.')
    (out/'isolated_selections.json').write_text(json.dumps(dict(definition='Original collection order; exact physical-factor isolation; nominal references included',selections=selections),indent=2)+'\n')
    return entries

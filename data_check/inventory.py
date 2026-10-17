"""Exhaustive inventory of actual collected conditions, never hypothetical ones."""
from pathlib import Path
import csv
import html
import json
from data import FACTORS,factor_values

HEADERS=['Mass (g)','Object friction','Size (mm)','Shape','COM X (mm)','Lift (cm)','Finger friction','Table friction']


def generate_inventory(dataset,out):
    dataset=Path(dataset);out=Path(out);m=json.loads((dataset/'manifest.json').read_text());episodes=json.loads((dataset/'episodes.json').read_text())
    baseline=next(c for c in m['conditions'] if not c['changed_properties']);base=factor_values(baseline)
    records=[]
    for i,c in enumerate(m['conditions'],1):
        values=factor_values(c);active=[f for f in FACTORS if values[f]!=base[f]];families=c['design_families']
        kind='Nominal reference' if not active else ('Single variable' if len(active)==1 else ('Designed pair' if any(f.startswith(('together:','opposite:')) for f in families) else 'Mixed combination'))
        directions=['same direction' if f.startswith('together:') else 'opposite directions' for f in families if f.startswith(('together:','opposite:')) and active]
        if not active:plot='J01_single_variable_overview.png'
        elif len(active)==1:plot='J01_single/'+active[0]+'.png'
        elif kind=='Designed pair':
            family=next(f for f in families if f.startswith(('together:','opposite:')))
            direction,pair=family.split(':');plot='J02_pairs/'+pair.replace('+','__')+'__'+direction+'.png'
        else:plot='J03_combinations/'+'__'.join(active)+'.png'
        numbers=[j for j,e in enumerate(episodes,1) if e['condition_id']==c['condition_id']]
        successes=sum(e['success'] for e in episodes if e['condition_id']==c['condition_id'])
        display=[values['mass']*1000,values['object_friction'],values['size']*1000,values['shape'],values['com']*1000,values['goal_height']*100,values['finger_friction'],values['table_friction']]
        records.append(dict(id=f'C{i:02d}',episode_start=min(numbers),episode_end=max(numbers),kind=kind,direction=', '.join(directions),active=active,values=display,n=len(numbers),successes=successes,plot=plot))
    assert len(records)==60 and sum(r['n'] for r in records)==600
    with (out/'experiment_inventory.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Condition','Episode start','Episode end','Pattern','Direction','Changed factors',*HEADERS,'Attempts','Successes','Plot'])
        for r in records:w.writerow([r['id'],r['episode_start'],r['episode_end'],r['kind'],r['direction'],' + '.join(r['active']) or 'none',*r['values'],r['n'],r['successes'],r['plot']])
    text=['<!doctype html><html><head><meta charset="utf-8"><title>All collected experiment patterns</title><style>body{font:15px system-ui;margin:26px;color:#17202a}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid #ddd;padding:9px;text-align:left}th{background:#eaf0f5;position:sticky;top:0}tr:nth-child(even){background:#f7f9fb}a{color:#175a99}.wrap{overflow:auto}</style></head><body>',
          '<h1>All collected experiment patterns</h1><p>60 unique settings × 10 starting seeds = 600 attempts. These are one dataset with several experiment designs.</p>',
          '<p><b>Breakdown:</b> 1 nominal reference + 15 isolated shifts + 12 designed paired shifts + 32 mixed settings. The nominal reference is shared, not an extra ten trials for every comparison.</p>',
          '<p><b>Both pair directions were collected</b> for mass/object-friction, mass/size and mass/lift-height: two same-direction settings and two opposite-direction settings per pair. These use ordered low/high levels; they are not a continuous linear sweep. All nine mass/friction grid cells were covered, including the nominal and single-variable settings.</p>',
          '<p><b>Nominal:</b> 100 g, object friction 0.4, 40 mm cube, COM X=0 mm, lift 20 cm, finger friction 0.2, table friction 0.3. The policy estimate is 40 g throughout.</p>',
          '<p>Every row uses the same ten seeds 2000–2009, with seeded initial positions/orientations. Shape or size changes can change the support height. Each plot link opens its isolated situation, including nominal reference trials.</p>',
          '<p><a href="index.html">Plot gallery</a> · <a href="experiment_inventory.csv">Download exact inventory as CSV</a></p>',
          '<div class="wrap"><table><tr>'+''.join('<th>'+html.escape(x)+'</th>' for x in ['Condition','Episodes','Pattern / direction','Changed factors',*HEADERS,'Successes','Isolated plot'])+'</tr>']
    for r in records:
        cells=[r['id'],f"{r['episode_start']}–{r['episode_end']}",r['kind']+(': '+r['direction'] if r['direction'] else ''),' + '.join(r['active']) or 'none',*[f'{x:g}' if isinstance(x,(int,float)) else str(x) for x in r['values']],f"{r['successes']}/{r['n']}"]
        text.append('<tr>'+''.join('<td>'+html.escape(x)+'</td>' for x in cells)+f'<td><a href="{r["plot"]}">Open plot</a></td></tr>')
    text+=['</table></div><p>The 32 mixed settings are seeded selections, not an exhaustive factorial sweep over every mathematically possible setting. All other unlisted combinations remain untested.</p></body></html>']
    (out/'experiment_inventory.html').write_text('\n'.join(text))
    return records


if __name__=='__main__':
    root=Path(__file__).resolve().parent
    result=generate_inventory(root.parent/'runs/failure_collection/varied_fixed40g',root/'plots')
    print('Wrote all',len(result),'actual conditions, with exact settings, episode ranges, outcomes and isolated plot links.')

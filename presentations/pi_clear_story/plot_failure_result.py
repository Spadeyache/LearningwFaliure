from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path('/home/ubuntu/faliure')
rows=list(csv.DictReader((root/'failure_discovery/results/mass_friction_discovery/episode_metrics.csv').open()))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(6.2,2.8),layout='constrained')
fig.patch.set_facecolor('#FFFFFF');ax.set_facecolor('#FFFFFF')
for name,color in [('group_1','#087F7B'),('group_2','#B76E25')]:
 selected=[r for r in rows if r['cluster']==name]
 ax.scatter([100*float(r['final_target_error_m']) for r in selected],[float(r['longest_steady_hold_s']) for r in selected],s=24,color=color,alpha=.6,label=f"Group {name[-1]} (n={len(selected)})")
ax.set(xlabel='Final distance to target (cm)',ylabel='Steady-hold proxy (s)')
ax.legend(frameon=False,fontsize=11,loc='upper right')
ax.grid(axis='y',color='#D8DFD9',linewidth=.6)
fig.savefig(root/'presentations/pi_clear_story/failure_behavior_groups.png',dpi=200)
print('Saved failure-group figure from recorded episode metrics.')

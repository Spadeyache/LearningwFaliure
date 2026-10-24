"""Replot two completed analyses for slide five; no new trials or fitting."""
from pathlib import Path
from collections import defaultdict
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('/home/ubuntu/faliure')
OUT = ROOT / 'presentations/pi_clear_story'
rows = list(csv.DictReader((ROOT / 'failure_discovery/results/mass_friction_discovery/episode_metrics.csv').open()))
episodes = json.loads((ROOT / 'runs/failure_collection/dense_single_pair_fixed40g/episodes.json').read_text())
rates = defaultdict(list)
for episode in episodes:
    if 'single:mass' in episode['design_families']:
        rates[1000 * episode['factor_values']['mass']].append(int(episode['success']))
assert len(rates) == 12 and all(len(values) == 10 for values in rates.values())
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'text.color': '#183139', 'axes.labelcolor': '#183139',
                     'xtick.color': '#62747A', 'ytick.color': '#62747A'})
fig, axes = plt.subplots(1, 2, figsize=(8.7, 1.8), layout='constrained',
                         gridspec_kw={'wspace': .17})
for name, color in [('group_1', '#087F7B'), ('group_2', '#B76E25')]:
    selected = [row for row in rows if row['cluster'] == name]
    axes[0].scatter([100 * float(row['final_target_error_m']) for row in selected],
                    [float(row['longest_steady_hold_s']) for row in selected],
                    s=12, color=color, alpha=.65, label=f'Group {name[-1]}')
axes[0].set(xlabel='Final distance to target (cm)', ylabel='Steady hold (s)')
axes[0].legend(frameon=False, fontsize=8, loc='upper right')
mass = sorted(rates)
success = [sum(rates[m]) / 10 for m in mass]
axes[1].plot(mass, success, 'o-', color='#087F7B', markersize=4, linewidth=1.1)
axes[1].set(xlabel='Actual mass (g); other factors fixed', ylabel='Successful lifts / 10',
            ylim=(-.06, 1.06), yticks=[0, .5, 1], yticklabels=['0', '5', '10'])
axes[1].text(.98, .95, 'Same 10 starts per mass', transform=axes[1].transAxes,
             ha='right', va='top', fontsize=8)
for ax in axes:
    ax.grid(axis='y', color='#E7EBEC', linewidth=.6)
fig.patch.set_facecolor('white')
fig.savefig(OUT / 'two_completed_analyses.png', dpi=220)
fig_mass, ax = plt.subplots(figsize=(4.2, 1.8), layout='constrained')
ax.plot(mass, success, 'o-', color='#087F7B', markersize=4, linewidth=1.1)
ax.set(xlabel='Actual mass (g); other factors fixed', ylabel='Successful lifts / 10',
       ylim=(-.06, 1.06), yticks=[0, .5, 1], yticklabels=['0', '5', '10'])
ax.text(.98, .95, 'Same 10 starts per mass', transform=ax.transAxes,
        ha='right', va='top', fontsize=8)
ax.grid(axis='y', color='#E7EBEC', linewidth=.6)
fig_mass.savefig(OUT / 'mass_sweep_only.png', dpi=220)
(OUT / 'two_analyses_plot_values.json').write_text(json.dumps({
    'mass_only_success_counts': {str(m): sum(rates[m]) for m in mass},
    'starts_per_mass': 10, 'motion_groups': {'group_1': 115, 'group_2': 39},
    'notes': 'Descriptive outcomes across seeded starts; no unique cause inferred.'
}, indent=2) + '\n')
print('Saved two analyses from existing recorded outcomes.')

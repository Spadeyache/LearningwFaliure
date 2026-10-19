"""Dense, reproducible interventions: nominal, singles and two-factor pairs only."""
from copy import deepcopy
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import numpy as np
from .environment import normalized_properties

FACTOR_NAMES = ('mass','object_friction','dynamic_friction_ratio','finger_friction','table_friction',
                'size','shape','com_x','com_y','com_z','goal_height','restitution','linear_damping',
                'angular_damping','spawn_x','spawn_y','spawn_yaw','inertia_scale')


def levels(spec, count, nominal=True):
    if spec['type']=='categorical':
        return list(spec['values'])
    values=[round(float(v),12) for v in np.linspace(spec['min'],spec['max'],count)]
    if nominal:
        values.append(float(spec['nominal']))
    return sorted(set(values))


def load_settings(path, seed_count=None):
    config=json.loads(Path(path).read_text())
    if seed_count is not None:
        config['seed_count']=seed_count
    required={'design','levels_per_factor','seed_count','start_seed','episode_steps','contact_threshold_n',
              'reported_mass_kg','pair_design','factors'}
    if set(config)!=required or config['design']!='dense_single_pair':
        raise ValueError('Expected the dense_single_pair config with its documented keys')
    for key in ('levels_per_factor','seed_count','start_seed','episode_steps'):
        minimum=3 if key=='levels_per_factor' else (0 if key=='start_seed' else 1)
        if type(config[key]) is not int or config[key]<minimum:
            raise ValueError('Invalid '+key)
    if config['start_seed']+config['seed_count']>2**31:
        raise ValueError('Seed range exceeds 31 bits')
    for key in ('contact_threshold_n','reported_mass_kg'):
        if not np.isfinite(config[key]) or config[key]<=0:
            raise ValueError('Invalid '+key)
    if config['reported_mass_kg']!=.04:
        raise ValueError('This experiment holds the policy estimate fixed at 40 grams')
    if config['pair_design']!='all_directions':
        raise ValueError('pair_design must be all_directions: every numeric pair in both directions')
    if set(config['factors'])-set(FACTOR_NAMES) or not config['factors']:
        raise ValueError('Unknown or absent factors')
    # All definitions remain present. Disable a factor rather than removing its nominal.
    if set(config['factors'])!=set(FACTOR_NAMES):
        raise ValueError('Keep every factor definition; set enabled=false to hold one fixed')
    for name,spec in config['factors'].items():
        if type(spec.get('enabled')) is not bool:
            raise ValueError('Each factor needs enabled=true/false')
        if spec.get('type')=='numeric':
            if set(spec)!={'type','enabled','min','nominal','max','unit'}:
                raise ValueError('Invalid numeric definition: '+name)
            if not np.isfinite([spec['min'],spec['nominal'],spec['max']]).all() or not spec['min']<spec['max'] or not spec['min']<=spec['nominal']<=spec['max']:
                raise ValueError('Invalid numeric bounds: '+name)
        elif spec.get('type')=='categorical' and name=='shape':
            if set(spec)!={'type','enabled','values','nominal','unit'} or len(set(spec['values']))!=len(spec['values']) or spec['nominal'] not in spec['values'] or not set(spec['values'])<={'cube','sphere'}:
                raise ValueError('Shape must use cube/sphere values and include nominal')
        else:
            raise ValueError('Invalid factor type: '+name)
    return config


def properties_for(values):
    """Combine semantic factors, including independent components of the COM."""
    size=float(values['size']);mass=float(values['mass']);scale=float(values['inertia_scale'])
    if size<=0 or scale<=0:
        raise ValueError('Size and inertia scale must be positive')
    if not 0<values['dynamic_friction_ratio']<=1:
        raise ValueError('Sliding/static friction ratio must be in (0,1]')
    if not .02<=values['goal_height']<=.4:
        raise ValueError('Lift height must stay in [0.02,0.4] m')
    if abs(values['spawn_x'])>.08 or abs(values['spawn_y'])>.08 or abs(values['spawn_yaw'])>np.pi:
        raise ValueError('Spawn offsets exceed the configured tabletop envelope')
    props=dict(shape=values['shape'],size_xyz_m=[size]*3,mass_kg=mass,
        com_offset_m=[values['com_x'],values['com_y'],values['com_z']],
        static_friction=values['object_friction'],dynamic_friction=round(values['object_friction']*values['dynamic_friction_ratio'],12),
        finger_friction=values['finger_friction'],table_friction=values['table_friction'],
        restitution=values['restitution'],linear_damping=values['linear_damping'],angular_damping=values['angular_damping'])
    if scale!=1:
        moment=mass*size**2*(.1 if values['shape']=='sphere' else 1/6)
        props['inertia_principal_kg_m2']=[moment*scale]*3
    return normalized_properties(props)


def conditions(config):
    specs=config['factors'];base={k:s['nominal'] for k,s in specs.items()}
    base_props=properties_for(base);result={};count=config['levels_per_factor']
    enabled=[k for k in FACTOR_NAMES if specs[k]['enabled']]
    def add(overrides,family):
        values=dict(base);values.update(overrides)
        changed=[k for k in FACTOR_NAMES if values[k]!=base[k]]
        if len(changed)>2:
            raise AssertionError('A condition changed more than two experiment factors')
        props=properties_for(values)
        payload=dict(properties=props,goal_clearance_m=values['goal_height'],
            spawn_offset_m=[values['spawn_x'],values['spawn_y']],spawn_yaw_offset_rad=values['spawn_yaw'])
        identity=hashlib.sha256(json.dumps(payload,sort_keys=True,allow_nan=False).encode()).hexdigest()[:16]
        if identity not in result:
            raw_changes=[k for k in props if props[k]!=base_props[k]]
            for name in ('goal_height','spawn_x','spawn_y','spawn_yaw'):
                if name in changed:raw_changes.append(name)
            result[identity]=dict(condition_id=identity,**payload,changed_factors=changed,
                factor_values=values,changed_properties=raw_changes,design_families=[])
        else:
            if result[identity]['factor_values']!=values:
                raise ValueError('Two distinct factors mapped to identical physical settings')
        if family not in result[identity]['design_families']:
            result[identity]['design_families'].append(family)
    add({},'baseline')
    for name in enabled:
        for value in levels(specs[name],count):
            add({name:value},'single:'+name)
    for a,b in combinations(enabled,2):
        if specs[a]['type']==specs[b]['type']=='numeric':
            left=levels(specs[a],count,nominal=False);right=levels(specs[b],count,nominal=False)
            for x,y in zip(left,right):add({a:x,b:y},f'together:{a}+{b}')
            for x,y in zip(left,reversed(right)):add({a:x,b:y},f'opposite:{a}+{b}')
        else:
            for x,y in product(levels(specs[a],count),levels(specs[b],count)):
                add({a:x,b:y},f'categorical_cross:{a}+{b}')
    return list(result.values())


def write_plan(path,config,plan):
    """Readable review list of available ranges and actual experiment families."""
    base={k:s['nominal'] for k,s in config['factors'].items()}
    lines=['# Next collection: dense single and pair sweeps','',
        f"{len(plan):,} unique settings × {config['seed_count']} seeds = {len(plan)*config['seed_count']:,} episodes.",
        'At most two declared factors change per setting. Fixed policy mass estimate: 40 g. No new data has been collected by writing this plan.','',
        '| Factor | Nominal | Numeric levels / categories | Unit | Enabled |','| --- | --- | --- | --- | --- |']
    for name,spec in config['factors'].items():
        values=', '.join(f'{v:g}' if isinstance(v,(int,float)) else v for v in levels(spec,config['levels_per_factor']))
        lines.append(f"| {name} | {spec['nominal']} | {values} | {spec['unit']} | {spec['enabled']} |")
    lines+=['','## Pair designs','',
        'Every enabled numeric pair is sampled in both same-direction and opposite-direction sweeps. These use evenly spaced physical values from low to high; categorical shape pairs use all collected level combinations.',
        'The nominal value is additionally retained for every single-factor comparison. Duplicate settings are run once and retain all applicable design-family labels.',
        'These are diagonal pair sweeps, not the complete two-dimensional factorial grid. Reused starting seeds vary initial states but do not count as extra property interventions.',
        'Mass changes derive inertia from mass and size. Inertia-scale interventions are explicitly synthetic independent inertia changes. Dynamic-friction ratio changes sliding friction while holding static friction fixed.',
        'Spawn X/Y/yaw are offsets from the same seeded reset. The vertical goal follows the spawn; changing spawn also moves the target XY by design.','',
        '## Actual family coverage','', '| Family | Unique settings (references may overlap) |','| --- | --- |']
    families=sorted({f for c in plan for f in c['design_families']})
    for family in families:lines.append(f"| {family} | {sum(family in c['design_families'] for c in plan)} |")
    Path(path).write_text('\n'.join(lines)+'\n')

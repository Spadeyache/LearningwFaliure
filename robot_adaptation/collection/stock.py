"""Short, gated single-factor sweeps of an unchanged official PickCube PPO policy."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.utils.structs.pose import Pose
from mani_skill.utils.geometry.rotation_conversions import quaternion_multiply

from .collect import ROOT, digest, rollout, runtime_metadata, write_json
from robot_adaptation.simulation.environment import CollectionEnv, normalized_properties
from .schema import save_episode, describe
from .provenance import snapshot_sources

EXAMPLE = ROOT / 'robot_adaptation/policy/examples/maniskill_pick_cube'


def official_policy():
    # Reuse the existing pinned downloader and original upstream network.
    sys.path.insert(0, str(EXAMPLE))
    spec = importlib.util.spec_from_file_location('stock_pickcube_runner', EXAMPLE / 'run_pretrained.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model, metadata, url = module.download_model('pd_ee_delta_pos')
    return module, model, metadata, url


def validate_config(config):
    for key in ('seed_count', 'levels_per_factor', 'episode_steps'):
        if type(config[key]) is not int or config[key] < (3 if key == 'levels_per_factor' else 1):
            raise ValueError('Invalid ' + key)
    if config['design'] != 'stock_single' or not 0 < config['minimum_baseline_success_rate'] <= 1:
        raise ValueError('Invalid design or baseline gate')
    if config['start_seed'] < 0 or config['contact_threshold_n'] <= 0:
        raise ValueError('Invalid seed or force threshold')
    for name, spec in config['factors'].items():
        if spec['type'] == 'numeric':
            if not np.isfinite([spec['min'], spec['nominal'], spec['max']]).all() or not spec['min'] <= spec['nominal'] <= spec['max']:
                raise ValueError('Invalid bounds for ' + name)
        elif name != 'shape' or spec['type'] != 'categorical' or spec['nominal'] not in spec['values']:
            raise ValueError('Invalid categorical factor')
    return config


def make_plan(config):
    base = {k: s['nominal'] for k, s in config['factors'].items()}
    plan = {}
    def add(values, family):
        changed = [k for k in base if values[k] != base[k]]
        if len(changed) > 1:
            raise ValueError('Short collection allows single factors only')
        props = normalized_properties(dict(shape=values['shape'], size_xyz_m=[values['size']]*3,
            mass_kg=values['mass'], com_offset_m=[values['com_x'], values['com_y'], values['com_z']],
            static_friction=values['object_friction'], dynamic_friction=values['object_friction']*values['dynamic_friction_ratio'],
            finger_friction=values['finger_friction'], table_friction=values['table_friction'],
            restitution=values['restitution'], linear_damping=values['linear_damping'], angular_damping=values['angular_damping']))
        condition = dict(factor_values=dict(values), properties=props, changed_factors=changed,
            changed_properties=list(changed), spawn_offset_m=[values['spawn_x'], values['spawn_y']],
            spawn_yaw_offset_rad=values['spawn_yaw'], goal_height_range_max_m=values['goal_height'])
        identity = digest(condition)[:16]
        if identity not in plan:
            plan[identity] = dict(condition_id=identity, **condition, design_families=[])
        plan[identity]['design_families'].append(family)
    add(base, 'baseline')
    for name, spec in config['factors'].items():
        if not spec['enabled']:
            continue
        levels = spec['values'] if spec['type'] == 'categorical' else sorted(set(
            [round(float(x), 12) for x in np.linspace(spec['min'], spec['max'], config['levels_per_factor'])] + [spec['nominal']]))
        for value in levels:
            values = dict(base); values[name] = value
            add(values, 'single:' + name)
    return list(plan.values())


class StockCollectionEnv(CollectionEnv):
    """Native task/reward/success/controller. Patch only the declared factor."""
    collection_description = 'Official PickCube task: random XYZ goal, original geometric success and native four-action controller'

    def __init__(self, condition):
        self.condition = condition
        self.changed = set(condition['changed_factors'])
        super().__init__(condition['properties'])

    def _load_agent(self, options):
        if 'finger_friction' in self.changed:
            CollectionEnv._load_agent(self, options)
        else:
            PickCubeEnv._load_agent(self, options)

    def _load_scene(self, options):
        if self.changed & {'shape', 'size'}:
            CollectionEnv._load_scene(self, options)
            return
        PickCubeEnv._load_scene(self, options)
        body = self.cube._bodies[0]
        p = self.properties
        # Native construction is retained for baseline and non-geometry shifts.
        if 'mass' in self.changed:
            ratio = p['mass_kg'] / body.mass
            inertia = np.asarray(body.inertia).copy() * ratio
            body.set_mass(p['mass_kg']); body.set_inertia(inertia)
        if self.changed & {'com_x', 'com_y', 'com_z'}:
            import sapien
            body.set_cmass_local_pose(sapien.Pose(p=p['com_offset_m']))
        if 'inertia_scale' in self.changed:
            body.set_inertia(np.asarray(body.inertia) * self.condition['factor_values']['inertia_scale'])
        if self.changed & {'object_friction', 'dynamic_friction_ratio', 'restitution'}:
            self._material(body, p['static_friction'], p['dynamic_friction'], p['restitution'])
        if 'table_friction' in self.changed:
            self._material(self.table_scene.table._bodies[0], p['table_friction'], p['table_friction'], 0.)
        for factor in ('linear_damping', 'angular_damping'):
            if factor in self.changed:
                getattr(body, 'set_' + factor)(p[factor])

    def _initialize_episode(self, env_idx, options):
        self._contacts_stale = True
        PickCubeEnv._initialize_episode(self, env_idx, options)
        # The random target remains independently sampled, as in native PickCube.
        # Spawn changes do not move the goal with the object.
        if self.changed & {'shape', 'size', 'spawn_x', 'spawn_y', 'spawn_yaw'}:
            pose = self.cube.pose.raw_pose.clone()
            pose[:, :2] += torch.tensor(self.condition['spawn_offset_m'], device=self.device)
            angle = self.condition['spawn_yaw_offset_rad'] / 2
            yaw = torch.tensor([[np.cos(angle), 0., 0., np.sin(angle)]], device=self.device, dtype=pose.dtype)
            pose[:, 3:] = quaternion_multiply(yaw, pose[:, 3:])
            pose[:, 2] = self.support_height(pose[:, 3:])
            self.cube.set_pose(Pose.create(pose))
        if 'goal_height' in self.changed:
            goal = self.goal_site.pose.p.clone()
            u = (goal[:, 2] - self.cube_half_size) / self.max_goal_height
            goal[:, 2] = self.cube_half_size + u * self.condition['goal_height_range_max_m']
            self.goal_site.set_pose(Pose.create_from_pq(goal))


def write_plan(path, config, plan):
    lines = ['# Official policy: short single-variable collection', '',
        f'{len(plan)} settings × {config["seed_count"]} seeds = {len(plan)*config["seed_count"]} attempts.',
        f'Baseline gate: at least {config["minimum_baseline_success_rate"]:.0%} FINAL success in the nominal attempts.',
        'If the gate fails, save the baseline and stop before physical sweeps.',
        'Original 42 inputs / 4 actions; no weight input, grip-strength branch, or custom vertical-lift goal.',
        'Original 50-step horizon and geometric success; final and any-time flags both saved.',
        'Native task on CPU is not a claim of identical behavior to the published GPU runtime.', '',
        '| Factor | Nominal | Short sweep |', '| --- | --- | --- |']
    for name, spec in config['factors'].items():
        values = sorted({c['factor_values'][name] for c in plan})
        lines.append(f'| {name} | {spec["nominal"]} | {", ".join(map(str, values))} |')
    lines += ['', 'Goal height denotes the maximum of the native random height range, not a fixed vertical lift.',
              'Restitution and linear damping start at zero and cannot vary below zero. Sliding/static ratio cannot exceed one.',
              'Mass/size shifts also change derived inertia. Inertia-scale shifts are explicitly synthetic.',
              'The default gate uses only ten starts and is a screening check, not a precise reliability estimate.']
    Path(path).write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'configs/failure_collection_stock_short.json')
    parser.add_argument('--output', type=Path, default=ROOT/'runs/collection'/
                        ('stock_' + datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')))
    parser.add_argument('--seed-count', type=int)
    parser.add_argument('--levels', type=int)
    parser.add_argument('--plan-only', action='store_true')
    parser.add_argument('--baseline-only', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if args.seed_count is not None: config['seed_count'] = args.seed_count
    if args.levels is not None: config['levels_per_factor'] = args.levels
    validate_config(config)
    plan = make_plan(config)
    print(json.dumps(dict(settings=len(plan), seeds=config['seed_count'], planned_episodes=len(plan)*config['seed_count'],
                          baseline_gate=config['minimum_baseline_success_rate'], single_factors_only=True)), flush=True)
    if args.plan_only:
        return
    torch.set_num_threads(1)
    runner, checkpoint, metadata, url = official_policy()
    if config['episode_steps'] != metadata['env_info']['max_episode_steps']:
        raise ValueError('Keep the published task horizon unchanged')
    runtime = runtime_metadata()
    runtime['official_policy_source_sha256'] = digest({name: hashlib.sha256((EXAMPLE/name).read_bytes()).hexdigest()
        for name in ('run_pretrained.py', 'ppo_upstream.py')})
    identity = digest(dict(config=config, checkpoint=hashlib.sha256(checkpoint.read_bytes()).hexdigest(), runtime=runtime, conditions=plan))
    output = args.output.resolve()
    if output.exists():
        if not args.resume: raise FileExistsError('Choose a new output folder or use --resume')
        manifest = json.loads((output/'manifest.json').read_text())
        if manifest['identity'] != identity: raise ValueError('Resume requires identical code, policy and settings')
    else:
        output.mkdir(parents=True)
        manifest = dict(identity=identity, config=config, conditions=plan, checkpoint=str(checkpoint),
            checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(), checkpoint_url=url,
            published_metadata=metadata, runtime=runtime, status='running', policy_inputs=42, policy_actions=4,
            success_definition='Original PickCube: object within 0.025m of native random goal and arm nearly static; no added grasp requirement',
            retries=False, clustering=False)
        source = output/'source'
        extra = list(EXAMPLE.glob('*.py')) + [ROOT/'robot_adaptation/policy/MANISKILL_LICENSE']
        snapshot_sources(source, extra)
        write_json(output/'config.json',config)
        write_plan(output/'plan.md',config,plan)
    write_json(output/'manifest.json',manifest)
    records = []
    try:
        with torch.inference_mode():
            for i, condition in enumerate(plan):
                env = StockCollectionEnv(condition)
                agent = runner.load_agent(env,checkpoint).eval().requires_grad_(False)
                try:
                    for seed in range(config['start_seed'],config['start_seed']+config['seed_count']):
                        eid = f'{condition["condition_id"]}_seed{seed}'
                        path = output/(eid+'.npz')
                        if path.exists():
                            with np.load(path,allow_pickle=False) as archive: data={k:archive[k] for k in archive.files}
                            if str(data['meta__experiment_identity']) != identity: raise ValueError('Mismatched saved episode')
                        else:
                            def policy(observation):
                                obs = runner.vector(observation)
                                return agent.get_action(obs,deterministic=True)
                            data,_ = rollout(env,policy,seed,config)
                            data.update({
                                'meta__experiment_identity':np.asarray(identity),'meta__episode_id':np.asarray(eid),
                                'meta__checkpoint_sha256':np.asarray(manifest['checkpoint_sha256']),
                                'label__condition_id':np.asarray(condition['condition_id']),
                                'label__condition_json':np.asarray(json.dumps(condition,sort_keys=True)),
                                'label__changed_factors':np.asarray(condition['changed_factors'],dtype='U64'),
                                'label__changed_properties':np.asarray(condition['changed_properties'],dtype='U64'),
                                'label__factor_values_json':np.asarray(json.dumps(condition['factor_values'],sort_keys=True)),
                                'label__design_families':np.asarray(condition['design_families']),
                                'label__spawn_offset_xy_m':np.asarray(condition['spawn_offset_m']),
                                'label__spawn_yaw_offset_rad':np.asarray(condition['spawn_yaw_offset_rad']),
                                'label__goal_height_range_max_m':np.asarray(condition['goal_height_range_max_m'])})
                            if data['sim__policy_observation'].shape[1]!=42 or data['input__action_applied'].shape[1]!=4:
                                raise ValueError('Official policy interface changed')
                            save_episode(path,data)
                        if not records: write_json(output/'schema.json',describe(data))
                        pair=np.linalg.norm(data['sim__physics_object_pair_force_world_n'],axis=-1).max(axis=0)
                        record=dict(episode_id=eid,file=path.name,seed=seed,condition_id=condition['condition_id'],
                            design_families=condition['design_families'],changed_factors=condition['changed_factors'],
                            changed_properties=condition['changed_properties'],properties=condition['properties'],factor_values=condition['factor_values'],
                            success=bool(data['label__success_final']),success_any=bool(data['label__success_any']),
                            failure_type=str(data['label__failure_type']),grasped=bool(data['sim__is_grasped'].any()),
                            bilateral_force_verified=bool(np.all(pair>config['contact_threshold_n'])))
                        if record['grasped'] and not record['bilateral_force_verified']: raise RuntimeError('Missing grasp forces')
                        records.append(record)
                        write_json(output/'episodes.json',records)
                        print(f'{len(records)}/{len(plan)*config["seed_count"]} {eid} success={record["success"]}',flush=True)
                finally:
                    env.close()
                if i==0:
                    rate=sum(r['success'] for r in records)/len(records)
                    gate=dict(episodes=len(records),successes=sum(r['success'] for r in records),success_rate=rate,
                              minimum=config['minimum_baseline_success_rate'],passed=rate>=config['minimum_baseline_success_rate'])
                    write_json(output/'baseline_check.json',gate)
                    if not gate['passed'] or args.baseline_only:
                        manifest['status']='baseline_rejected' if not gate['passed'] else 'baseline_only_complete'
                        print('Baseline check:',json.dumps(gate),'No sweep started.',flush=True)
                        break
            else:
                manifest['status']='complete'
        write_json(output/'summary.json',dict(episodes=len(records),successes=sum(r['success'] for r in records),
            failures=sum(not r['success'] for r in records),status=manifest['status']))
    except BaseException:
        manifest['status']='interrupted_or_failed'
        raise
    finally:
        write_json(output/'manifest.json',manifest)


if __name__=='__main__': main()

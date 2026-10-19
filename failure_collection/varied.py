"""Fixed trained policy, independent/same-direction/opposite-direction physics sweeps.

Run via scripts/collect_varied.sh; --plan-only writes no files and runs no physics.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import torch
from mani_skill.utils.structs.pose import Pose
from mani_skill.utils.geometry.rotation_conversions import quaternion_multiply

from .collect import ROOT, digest, rollout, runtime_metadata, write_json
from .environment import CollectionEnv
from .schema import describe, save_episode, validate_episode

from .grip_controller import install_strength_controller
from .inference import Agent, POLICY_ARCHITECTURE


class WeightedCollectionEnv(CollectionEnv):
    """45-input/5-action trained interface; reported weight never uses true mass.

    Goal is directly above the spawn: pick, lift, and hold, without lateral carry.
    Independent object materials replace the training task's mass/friction coupling.
    """
    episode_schema_version = 'pick_failure_v3'
    collection_description = 'WeightedCollectionEnv: held object within 2.5cm of vertical goal, arm static'

    def __init__(self, properties, *, reported_mass_kg, goal_clearance_m, grip_force_limits_n,
                 spawn_offset_m=None, spawn_yaw_offset_rad=0.0):
        self.spawn_offset_m = [0.,0.] if spawn_offset_m is None else list(spawn_offset_m)
        self.spawn_yaw_offset_rad = float(spawn_yaw_offset_rad)
        self.reported_mass_kg = float(reported_mass_kg)
        self.goal_clearance_m = float(goal_clearance_m)
        self.grip_force_limits_n = list(grip_force_limits_n)
        super().__init__(properties)

    def _load_agent(self, options):
        super()._load_agent(options)
        install_strength_controller(self)

    def _initialize_episode(self, env_idx, options):
        super()._initialize_episode(env_idx, options)
        self.agent.controller.controllers['gripper'].reset_env_idx = env_idx
        if any(self.spawn_offset_m) or self.spawn_yaw_offset_rad:
            pose = self.cube.pose.raw_pose.clone()
            pose[:, :2] += torch.tensor(self.spawn_offset_m,device=self.device)
            angle = self.spawn_yaw_offset_rad/2
            yaw = torch.tensor([[np.cos(angle),0.,0.,np.sin(angle)]],device=self.device,dtype=pose.dtype)
            pose[:, 3:] = quaternion_multiply(yaw,pose[:, 3:])
            pose[:, 2] = self.support_height(pose[:, 3:])
            self.cube.set_pose(Pose.create(pose))
        goal = self.cube.pose.p.clone()
        goal[:, 2] += self.goal_clearance_m
        self.goal_site.set_pose(Pose.create_from_pq(goal))

    def _get_obs_extra(self, info):
        measurements = super()._get_obs_extra(info)
        gravity = float(np.linalg.norm(self.scene.px.get_config().gravity))
        measurements['object_weight_n'] = torch.full((1, 1), self.reported_mass_kg,
            device=self.device, dtype=torch.float32) * gravity
        forces = []
        for link, sign in ((self.agent.finger1_link, 1), (self.agent.finger2_link, -1)):
            force = self.scene.get_pairwise_contact_forces(link, self.cube)
            axis = sign * link.pose.to_transformation_matrix()[:, :3, 1]
            value = (force * axis).sum(-1, keepdim=True).clamp_min(0)
            forces.append(torch.zeros_like(value) if self._contacts_stale else value)
        measurements['left_finger_force_n'], measurements['right_finger_force_n'] = forces
        return measurements

    def evaluate(self):
        info = super().evaluate()
        info['success'] = info['success'] & info['is_grasped']
        return info


from .design import conditions, load_settings, write_plan


def load_agent(checkpoint):
    saved = json.loads(checkpoint.with_name('manifest.json').read_text())
    if (saved.get('status') != 'complete' or saved.get('observations') != 45
            or saved.get('actions') != 5 or saved.get('policy_architecture') != POLICY_ARCHITECTURE):
        raise ValueError('Requires a completed 45-input/5-action branched trained policy')
    agent = Agent()
    agent.load_state_dict(torch.load(checkpoint, map_location='cpu', weights_only=True), strict=True)
    agent.eval().requires_grad_(False)
    return agent, saved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'configs/failure_collection_varied.json')
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'runs/failure_collection/dense_single_pair_fixed40g')
    parser.add_argument('--seed-count', type=int, help='Override the single seed-count configuration value')
    parser.add_argument('--plan-only', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--write-plan', type=Path, help='Write the configured ranges and experiment families as Markdown')
    args = parser.parse_args()
    config = load_settings(args.config, args.seed_count)
    plan = conditions(config)
    print(json.dumps(dict(conditions=len(plan), seeds=config['seed_count'],
                         episodes=len(plan)*config['seed_count'], reported_mass_kg=config['reported_mass_kg'],
                         factors=sum(s['enabled'] for s in config['factors'].values()),
                         max_changed_factors=max(len(c['changed_factors']) for c in plan))), flush=True)
    if args.write_plan is not None:
        write_plan(args.write_plan,config,plan)
    if args.plan_only:
        return
    if args.checkpoint is None:
        parser.error('--checkpoint is required for collection')
    checkpoint = args.checkpoint.resolve()
    torch.set_num_threads(1)
    agent, trained = load_agent(checkpoint)
    checkpoint_hash = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    provenance = runtime_metadata()
    provenance['trained_interface_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (Path(__file__).with_name('inference.py'), Path(__file__).with_name('grip_controller.py'))}
    identity = digest(dict(config=config, conditions=plan, checkpoint=checkpoint_hash, runtime=provenance))
    output = args.output.resolve()
    if output.exists():
        if not args.resume:
            raise FileExistsError('Output exists; choose a new directory or use --resume')
        manifest = json.loads((output/'manifest.json').read_text())
        if manifest['identity'] != identity:
            raise ValueError('Resume requires identical config, policy and collection code/runtime')
    else:
        if args.resume:
            raise FileNotFoundError('Cannot resume a missing output directory')
        output.mkdir(parents=True)
        manifest = dict(identity=identity, config=config, conditions=plan, checkpoint=str(checkpoint),
            checkpoint_sha256=checkpoint_hash, training_manifest=trained, runtime=provenance,
            success_definition='held within 0.025m of vertical goal and each arm speed <=0.2rad/s',
            status='running', retries=False, clustering=False)
        source = output/'source'
        source.mkdir()
        for path in Path(__file__).parent.glob('*.py'):
            shutil.copy2(path, source/path.name)
        shutil.copy2(Path(__file__).with_name('MANISKILL_LICENSE'), source/'MANISKILL_LICENSE')
        write_json(output/'config.json', config)
        write_plan(output/'plan.md',config,plan)
    write_json(output/'manifest.json', manifest)
    records = []
    try:
        with torch.inference_mode():
            for condition in plan:
                env = None
                try:
                    for seed in range(config['start_seed'], config['start_seed'] + config['seed_count']):
                        episode_id = f"{condition['condition_id']}_seed{seed}"
                        path = output/(episode_id + '.npz')
                        if path.exists():
                            with np.load(path, allow_pickle=False) as archive:
                                data = {k: archive[k] for k in archive.files}
                            validate_episode(data)
                            if str(data['meta__experiment_identity']) != identity or int(data['label__seed']) != seed:
                                raise ValueError('Existing episode does not match experiment')
                        else:
                            if env is None:
                                env = WeightedCollectionEnv(condition['properties'],
                                    reported_mass_kg=config['reported_mass_kg'],
                                    goal_clearance_m=condition['goal_clearance_m'],
                                    grip_force_limits_n=trained['settings']['grip_force_limits_n'],
                                    spawn_offset_m=condition['spawn_offset_m'],
                                    spawn_yaw_offset_rad=condition['spawn_yaw_offset_rad'])
                            def policy(obs):
                                if obs.shape != (1, 45):
                                    raise ValueError('Policy observation interface changed')
                                return agent.get_action(obs, deterministic=True)
                            data, _ = rollout(env, policy, seed, config)
                            data.update({
                                'meta__experiment_identity': np.asarray(identity),
                                'meta__episode_id': np.asarray(episode_id),
                                'meta__checkpoint_sha256': np.asarray(checkpoint_hash),
                                'label__changed_factors': np.asarray(condition['changed_factors'],dtype='U64'),
                                'label__factor_values_json': np.asarray(json.dumps(condition['factor_values'],sort_keys=True)),
                                'label__spawn_offset_xy_m': np.asarray(condition['spawn_offset_m']),
                                'label__spawn_yaw_offset_rad': np.asarray(condition['spawn_yaw_offset_rad']),
                                'label__condition_id': np.asarray(condition['condition_id']),
                                'label__changed_properties': np.asarray(condition['changed_properties'], dtype='U64'),
                                'label__design_families': np.asarray(condition['design_families']),
                                'label__condition_json': np.asarray(json.dumps(condition, sort_keys=True)),
                                'label__goal_clearance_m': np.asarray(condition['goal_clearance_m']),
                            })
                            save_episode(path, data)
                        gravity = np.linalg.norm(data['label__gravity_world_m_s2'])
                        expected = np.float32(config['reported_mass_kg']) * np.float32(gravity)
                        if not np.allclose(data['sim__policy_observation'][:, 42], expected, rtol=0, atol=1e-7):
                            raise RuntimeError('Reported weight was not constant')
                        if not records:
                            schema = describe(data)
                            schema['success'] = manifest['success_definition']
                            write_json(output/'schema.json', schema)
                        grasped = bool(data['sim__is_grasped'].any())
                        pair_peaks = np.linalg.norm(data['sim__physics_object_pair_force_world_n'], axis=-1).max(axis=0)
                        record = dict(episode_id=episode_id, file=path.name, seed=seed,
                            condition_id=condition['condition_id'], design_families=condition['design_families'],
                            changed_properties=condition['changed_properties'], properties=condition['properties'],
                            changed_factors=condition['changed_factors'],factor_values=condition['factor_values'],
                            success=bool(data['label__success_final']), success_any=bool(data['label__success_any']),
                            failure_type=str(data['label__failure_type']), grasped=grasped,
                            bilateral_force_verified=bool(np.all(pair_peaks > config['contact_threshold_n'])))
                        if grasped and not record['bilateral_force_verified']:
                            raise RuntimeError('Grasp detected without nonzero force on both fingers')
                        records.append(record)
                        print(f"{len(records)}/{len(plan)*config['seed_count']} {episode_id} success={record['success']}", flush=True)
                finally:
                    if env is not None:
                        env.close()
        write_json(output/'episodes.json', records)
        summary = dict(episodes=len(records), successes=sum(r['success'] for r in records),
            failures=sum(not r['success'] for r in records),
            outcomes=dict(Counter(r['failure_type'] for r in records)),
            grasped_runs=sum(r['grasped'] for r in records),
            reported_mass_verified_kg=config['reported_mass_kg'])
        write_json(output/'summary.json', summary)
        manifest['status'] = 'complete'
        print(json.dumps(summary), flush=True)
    except BaseException:
        manifest['status'] = 'interrupted'
        raise
    finally:
        write_json(output/'manifest.json', manifest)


if __name__ == '__main__':
    main()

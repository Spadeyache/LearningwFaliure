"""Opt-in regression against two preserved current-dataset episodes."""
import os
import json
from pathlib import Path
import unittest
import numpy as np


@unittest.skipUnless(os.environ.get('RUN_MANISKILL_INTEGRATION') == '1',
                     'set RUN_MANISKILL_INTEGRATION=1 for CPU PhysX checks')
class CollectionSimulationTests(unittest.TestCase):
    def test_current_collection_still_matches_saved_trajectories(self):
        import torch
        from robot_adaptation.collection.collect import rollout
        from robot_adaptation.collection.schema import validate_episode
        from robot_adaptation.collection.varied import WeightedCollectionEnv, conditions, load_settings, load_agent, ROOT
        torch.set_num_threads(1)
        original = json.loads((Path('/home/ubuntu/faliure/runs/failure_collection/varied_fixed40g')/'manifest.json').read_text())
        config = original['config']
        base = Path('/home/ubuntu/faliure')
        agent, trained = load_agent(base/'runs/learning/20261009T045047-c852bfc9/final_ckpt.pt')
        selected = [c for c in original['conditions'] if c['changed_properties'] in ([], ['mass_kg'])][:2]
        with torch.inference_mode():
            for condition in selected:
                env = WeightedCollectionEnv(condition['properties'], reported_mass_kg=config['reported_mass_kg'],
                    goal_clearance_m=condition['goal_clearance_m'], grip_force_limits_n=trained['settings']['grip_force_limits_n'])
                try:
                    data, _ = rollout(env, lambda obs: agent.get_action(obs, deterministic=True), 2000, config)
                    validate_episode(data)
                    path=base/'runs/failure_collection/varied_fixed40g'/f"{condition['condition_id']}_seed2000.npz"
                    with np.load(path, allow_pickle=False) as saved:
                        for key in data:
                            if key.startswith('input__') or key in ('sim__policy_observation', 'label__success_final',
                                    'sim__physics_object_pair_force_world_n'):
                                np.testing.assert_array_equal(data[key], saved[key], err_msg=key)
                    self.assertTrue(np.all(np.linalg.norm(data['sim__physics_object_pair_force_world_n'],axis=-1).max(axis=0)>0))
                finally:
                    env.close()

    def test_dense_controls_read_back_and_spawn_offsets_are_applied(self):
        from robot_adaptation.collection.varied import WeightedCollectionEnv, conditions, load_settings, load_agent, ROOT
        from robot_adaptation.collection.collect import rollout
        from scipy.spatial.transform import Rotation
        import torch
        torch.set_num_threads(1)
        config=load_settings(ROOT/'configs/failure_collection_varied.json')
        plan=conditions(config)
        agent,trained=load_agent(ROOT/'runs/learning/20261009T045047-c852bfc9/final_ckpt.pt')
        requested=[{'com_x','com_y'},{'linear_damping','angular_damping'},
                   {'object_friction','dynamic_friction_ratio'},{'size','inertia_scale'},
                   {'spawn_x','spawn_y'},{'spawn_yaw'}]
        chosen=[plan[0]]
        for factors in requested:
            chosen.append(next(c for c in reversed(plan) if set(c['changed_factors'])==factors))
        snapshots=[]
        with torch.inference_mode():
            for c in chosen:
                env=WeightedCollectionEnv(c['properties'],reported_mass_kg=.04,
                    goal_clearance_m=c['goal_clearance_m'],grip_force_limits_n=trained['settings']['grip_force_limits_n'],
                    spawn_offset_m=c['spawn_offset_m'],spawn_yaw_offset_rad=c['spawn_yaw_offset_rad'])
                try:
                    data,_=rollout(env,lambda obs:agent.get_action(obs,deterministic=True),2001,
                                   dict(episode_steps=3,contact_threshold_n=.05))
                    values=c['factor_values'];physical=env.physics_readback()
                    self.assertAlmostEqual(physical['linear_damping'],values['linear_damping'],places=6)
                    self.assertAlmostEqual(physical['angular_damping'],values['angular_damping'],places=6)
                    np.testing.assert_allclose(physical['com_offset_m'],[values['com_x'],values['com_y'],values['com_z']],atol=1e-8)
                    self.assertAlmostEqual(physical['object_materials'][0]['dynamic_friction'],values['object_friction']*values['dynamic_friction_ratio'],places=6)
                    expected=values['mass']*values['size']**2*(.1 if values['shape']=='sphere' else 1/6)*values['inertia_scale']
                    np.testing.assert_allclose(physical['inertia_principal_kg_m2'],[expected]*3,rtol=1e-5)
                    self.assertTrue(np.all(data['sim__policy_observation'][:,42]==np.float32(.04)*np.float32(9.81)))
                    snapshots.append(data['label__initial_object_pose_world_m_wxyz'])
                finally:env.close()
        for c,pose in zip(chosen,snapshots):
            np.testing.assert_allclose(pose[:2]-snapshots[0][:2],c['spawn_offset_m'],atol=2e-8)
            delta=(Rotation.from_quat(pose[3:],scalar_first=True)*Rotation.from_quat(snapshots[0][3:],scalar_first=True).inv()).as_rotvec()
            np.testing.assert_allclose(delta,[0,0,c['spawn_yaw_offset_rad']],atol=1e-6)

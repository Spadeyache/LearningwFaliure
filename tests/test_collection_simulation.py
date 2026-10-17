"""Opt-in regression against two preserved current-dataset episodes."""
import os
from pathlib import Path
import unittest
import numpy as np


@unittest.skipUnless(os.environ.get('RUN_MANISKILL_INTEGRATION') == '1',
                     'set RUN_MANISKILL_INTEGRATION=1 for CPU PhysX checks')
class CollectionSimulationTests(unittest.TestCase):
    def test_current_collection_still_matches_saved_trajectories(self):
        import torch
        from failure_collection.collect import rollout
        from failure_collection.schema import validate_episode
        from failure_collection.varied import WeightedCollectionEnv, conditions, load_settings, load_agent, ROOT
        torch.set_num_threads(1)
        config = load_settings(ROOT/'configs/failure_collection_varied.json')
        base = Path('/home/ubuntu/faliure')
        agent, trained = load_agent(base/'runs/learning/20261009T045047-c852bfc9/final_ckpt.pt')
        selected = [c for c in conditions(config) if c['changed_properties'] in ([], ['mass_kg'])][:2]
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

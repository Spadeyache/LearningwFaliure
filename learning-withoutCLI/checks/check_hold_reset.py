"""Regression: failed hold preparation retries, then real contact precedes PPO.

Outputs go to run/diagnosis. No existing model or training run is overwritten.
"""
from pathlib import Path
import hashlib
import json
import sys
import torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hold_task import HoldStrengthTask
from lift_task import read_inputs
from mani_skill.utils.structs.pose import Pose
from train_ppo import main as train, load_checkpoint
from ppo import Agent

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'run/diagnosis/hold-reset-20261008'
SOURCE = ROOT / 'runs/learning/20261008T183327-ffbcabfe/ckpt_126.pt'


class MissFirstPlacement(HoldStrengthTask):
    """Simulate one heavy cube missing the fingers during initial preparation."""
    def __init__(self, *args, **kwargs):
        self.placements = []
        super().__init__(*args, **kwargs)

    def _place_cube_in_fingers(self, env_idx):
        super()._place_cube_in_fingers(env_idx)
        self.placements.append(env_idx.tolist())
        if len(self.placements) == 1:
            self._miss()

    def _miss(self):
        pose = self.cube.pose.raw_pose.clone()
        pose[4, :3] = torch.tensor([0., 0., .02], device=self.device)
        self.cube.set_pose(Pose.create(pose))
        if self.gpu_sim_enabled:
            self.scene._gpu_apply_all()
            self.scene._gpu_fetch_all()


class NeverPrepare(MissFirstPlacement):
    """Persistent failure must raise rather than fabricate a successful grasp."""
    def _place_cube_in_fingers(self, env_idx):
        super()._place_cube_in_fingers(env_idx)
        self._miss()


def check_recovery():
    env = MissFirstPlacement(num_envs=10, sim_backend='physx_cuda')
    try:
        obs, info = env.reset(seed=1000)
        assert env._hold_preparation_retries >= 2
        assert env.placements[1] == [4], env.placements
        assert info['is_grasped'].all() and (info['clearance_m'] > .06).all()
        assert not env.elapsed_steps.any() and not env._contacts_stale.any()
        _, x = read_inputs(env, obs)
        assert torch.isfinite(x).all() and (x[:, 43:] > 0).all()
        result = dict(retries=env._hold_preparation_retries, replaced_indices=env.placements,
                      genuine_contacts=True, elapsed_steps_zero=True)
    finally:
        env.close()
    env = NeverPrepare(num_envs=10, sim_backend='physx_cuda')
    try:
        try:
            env.reset(seed=1000)
        except RuntimeError as exc:
            assert 'after 50 steps' in str(exc) and 'robots=[4]' in str(exc), str(exc)
            result['persistent_failure_rejected'] = True
        else:
            raise AssertionError('A persistent preparation failure must not return an episode')
    finally:
        env.close()
    return result


def check_stress(backend, resets):
    n = 60 if backend == 'physx_cuda' else 1
    env = HoldStrengthTask(num_envs=n, sim_backend=backend)
    recovered = []
    try:
        action = torch.zeros((n, 5), device=env.device)
        action[:, 4] = -1  # Stress the next reset after a weak previous grip.
        for seed in range(1, resets + 1):
            obs, info = env.reset(seed=seed)
            assert info['is_grasped'].all() and (info['clearance_m'] > .06).all()
            _, x = read_inputs(env, obs)
            assert torch.isfinite(x).all() and not env.elapsed_steps.any()
            assert not env._contacts_stale.any()
            if env._hold_preparation_retries:
                recovered.append(dict(seed=seed, retries=env._hold_preparation_retries))
            for _ in range(3):
                env.step(action)
            if seed % 25 == 0:
                print(backend, 'validated resets:', seed, flush=True)
    finally:
        env.close()
    return dict(resets=resets, robots=n, robot_preparations=n * resets, recovered=recovered)


def check_continuation():
    before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    output = train(dict(checkpoint=str(SOURCE), total_timesteps=6000, num_envs=60,
                        num_eval_envs=10, eval_freq=2, update_epochs=1,
                        run_root=str(OUT / 'continuation')))
    initial = torch.load(output / 'initialization.pt', map_location='cpu', weights_only=True)
    agent, manifest = load_checkpoint(output / 'final_ckpt.pt')
    state = agent.state_dict()
    for name, value in initial.items():
        if name.startswith('actor_mean.') or name == 'actor_logstd':
            assert torch.equal(state[name], value), name
    old = Agent()
    old.load_state_dict(initial)
    x = torch.randn(16, 45)
    with torch.no_grad():
        assert torch.equal(old.get_action(x, True)[:, :4], agent.get_action(x, True)[:, :4])
    delta = sum((state[k] - v).square().sum().item() for k, v in initial.items() if k.startswith('strength_'))
    assert delta > 0 and all(torch.isfinite(v).all() for v in state.values())
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before
    assert manifest['initialization']['checkpoint'] == str(SOURCE)
    return dict(output=str(output), source=str(SOURCE), source_sha256=before,
                source_unchanged=True, movement_exact=True, strength_change_squared=delta)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(4)
    results = dict(recovery=check_recovery())
    print('Physical recovery and bounded failure passed', flush=True)
    results['cpu_stress'] = check_stress('physx_cpu', 25)
    results['gpu_stress'] = check_stress('physx_cuda', 400)
    results['continuation'] = check_continuation()
    (OUT / 'verification.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Reset and checkpoint continuation checks passed:', OUT, flush=True)
    return results

if __name__ == '__main__':
    main()

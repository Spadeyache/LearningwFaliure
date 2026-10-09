"""Verify the hidden, correlated mass/friction simulator challenge.

Static/dynamic materials are checked on the actual shapes. Real holds confirm
light/weak and heavy/strong success and heavy/weak failure. CPU and GPU checks
run in separate processes because GPU PhysX must initialize before CPU PhysX.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import torch
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lift_task import (LiftTask, ENV_SETTINGS, FRICTION_KEYS, cube_friction_at_mass,
                       friction_settings, read_inputs)
from hold_task import HoldStrengthTask
from inspect_policy import policy_inputs, main as inspect
from train_ppo import latest_checkpoint, main as train, load_checkpoint
from ppo import Agent
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'run/diagnosis/mass-friction-20261008'
CONFIG = {key: ENV_SETTINGS[key] for key in FRICTION_KEYS}


def check_materials(backend):
    n = 10 if backend == 'physx_cuda' else 1
    env = LiftTask(num_envs=n, sim_backend=backend)
    rows = []
    try:
        for mass in ([None] if backend == 'physx_cuda' else ENV_SETTINGS['masses_kg']):
            obs, info = env.reset(seed=1000, options={} if mass is None else {'mass_kg': mass, 'reconfigure': True})
            for body in env.cube._bodies:
                mu = cube_friction_at_mass(body.mass, CONFIG)
                for shape in body.get_collision_shapes():
                    mat = shape.physical_material
                    assert np.isclose(mat.static_friction, mu) and np.isclose(mat.dynamic_friction, mu)
                rows.append(dict(mass_kg=body.mass, cube_coefficient=mu))
            for link in (env.agent.finger1_link, env.agent.finger2_link):
                for body in link._objs:
                    for shape in body.get_collision_shapes():
                        assert np.isclose(shape.physical_material.static_friction, .2)
                        assert np.isclose(shape.physical_material.dynamic_friction, .2)
            _, vector = read_inputs(env, obs)
            assert vector.shape == (n,45) and torch.isfinite(vector).all()
            nominal = policy_inputs(vector, 'nominal', 9.81, .04)
            assert torch.equal(vector[:, :42], nominal[:, :42]) and torch.equal(vector[:, 43:], nominal[:, 43:])
            # A false reported weight does not alter physical mass or friction.
            for body in env.cube._bodies:
                assert np.isclose(body.get_collision_shapes()[0].physical_material.static_friction,
                                  cube_friction_at_mass(body.mass, CONFIG))
        assert np.isclose(cube_friction_at_mass(.01, CONFIG), 1.)
        assert np.isclose(cube_friction_at_mass(1., CONFIG), .4)
    finally:
        env.close()
    # Old checkpoints explicitly retain the original native materials.
    env = LiftTask(num_envs=n, sim_backend=backend, friction_profile='native')
    try:
        _, info = env.reset(seed=1000)
        assert np.isclose(env.friction_details()['left_finger_static_friction'], 2.)
        legacy = friction_settings({})
        assert legacy['friction_profile'] == 'native'
    finally:
        env.close()
    return dict(materials=rows, observation_count=45, hidden_from_policy=True,
                native_compatibility=True, false_weight_does_not_change_materials=True)


def check_holds(backend):
    env = HoldStrengthTask(num_envs=10 if backend == 'physx_cuda' else 1,
                          sim_backend=backend)
    results=[]
    try:
        for mass in ([None] if backend == 'physx_cuda' else [.04,.5]):
            for cap in (7.,40.):
                obs, info=env.reset(seed=1000,options={} if mass is None else {'mass_kg':mass,'reconfigure':True})
                assert info['is_grasped'].all() and (info['clearance_m']>.06).all()
                action=torch.zeros((env.num_envs,5),device=env.device)
                action[:,4]=2*(cap-.25)/39.75-1
                for _ in range(50):obs,_,_,_,info=env.step(action)
                masses=env.cube.mass.to(env.device)
                light=torch.isclose(masses,torch.tensor(.04,device=env.device))
                heavy=torch.isclose(masses,torch.tensor(.5,device=env.device))
                assert (info['clearance_m'][light]>.06).all()
                if cap==7.:assert (info['clearance_m'][heavy]<.01).all()
                else:assert (info['clearance_m'][heavy]>.06).all() and info['is_grasped'][heavy].all()
                results.append(dict(masses_kg=masses.tolist(),cap_n=cap,
                                    clearance_m=info['clearance_m'].tolist(),grasped=info['is_grasped'].tolist()))
    finally:env.close()
    return results


def check_preparations():
    env=HoldStrengthTask(num_envs=60,sim_backend='physx_cuda')
    recovered=[]
    try:
        for seed in range(1,51):
            obs,info=env.reset(seed=seed)
            assert info['is_grasped'].all() and (info['clearance_m']>.06).all()
            assert not env.elapsed_steps.any() and read_inputs(env,obs)[1].shape==(60,45)
            if env._hold_preparation_retries:recovered.append(dict(seed=seed,retries=env._hold_preparation_retries))
            # Validate complete strong-grip holds for ten randomized 60-robot starts.
            action=torch.zeros((60,5),device=env.device);action[:,4]=1. if seed%5==0 else -1.
            for _ in range(50 if seed%5==0 else 3):obs,_,_,_,info=env.step(action)
            if seed%5==0:assert info['is_grasped'].all() and (info['clearance_m']>.06).all()
            if seed%10==0:print('GPU friction preparations:',seed,flush=True)
    finally:env.close()
    return dict(resets=50,robots=60,prepared_grasps=3000,recovered=recovered,
                complete_strong_holds=600)


def check_ppo():
    source=latest_checkpoint();source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    output=train(dict(checkpoint=str(source),total_timesteps=6000,eval_freq=2,update_epochs=1,
                      run_root=str(OUT/'ppo')))
    initial=torch.load(output/'initialization.pt',map_location='cpu',weights_only=True)
    agent,manifest=load_checkpoint(output/'final_ckpt.pt');final=agent.state_dict()
    for name,value in initial.items():
        if name.startswith('actor_mean.') or name=='actor_logstd':assert torch.equal(value,final[name]),name
    delta=sum((final[k]-v).square().sum().item() for k,v in initial.items() if k.startswith('strength_'))
    assert delta>0 and all(torch.isfinite(v).all() for v in final.values())
    assert manifest['friction_experiment']['changes_with_actual_mass']
    assert manifest['settings']['grip_force_cost']==.1
    assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
    return dict(output=str(output),source=str(source),source_unchanged=True,
                movement_unchanged=True,strength_change_squared=delta,inputs=45,actions=5)


def check_inspection():
    source=latest_checkpoint()
    output=inspect(dict(checkpoint=str(source),inspection_stage='hold_strength',
                        friction_override=CONFIG,masses_kg=[.04,.5],episodes_per_mass=2,
                        record_episodes_per_mass=1,output_root=str(OUT/'baseline_inspection')))
    manifest=json.loads((output/'manifest.json').read_text())
    summary=json.loads((output/'summary.json').read_text())
    assert manifest['status']=='complete' and manifest['friction_changed_from_training']
    assert summary['friction_experiment']['changes_with_actual_mass']
    for episode in summary['episodes']:
        assert np.isclose(episode['friction']['cube_static_friction'],cube_friction_at_mass(episode['mass_kg'],CONFIG))
        p=output/f"mass_{episode['mass_kg']:.3f}"/episode['weight_input']/f"episode_{episode['seed']-1000+1:02d}"/'steps.jsonl'
        record=json.loads(p.read_text().splitlines()[0]);assert 'friction' in record['state']
    assert (output/'success_rates.png').exists() and (output/'grip_strength_by_mass.png').exists()
    return dict(output=str(output),checkpoint=str(source),baseline_before_new_friction_training=True,
                labeled_friction_change=True,groups=summary['grouped_rates'])


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if len(sys.argv)>1:
        backend=sys.argv[1];torch.set_num_threads(4)
        result=dict(materials=check_materials(backend),holds=check_holds(backend))
        if backend=='physx_cuda':result.update(preparation=check_preparations(),ppo=check_ppo())
        (OUT/(backend+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        return
    results={}
    for backend in ('physx_cpu','physx_cuda'):
        subprocess.run([sys.executable,__file__,backend],cwd=ROOT,check=True)
        results[backend]=json.loads((OUT/(backend+'.json')).read_text())
    results['baseline_inspection']=check_inspection()
    (OUT/'verification.json').write_text(json.dumps(results,indent=2)+'\n')
    print('Mass/friction physics, PPO and labeled inspection passed:',OUT,flush=True)

if __name__=='__main__':main()

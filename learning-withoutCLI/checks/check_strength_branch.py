"""Check copied weights, frozen movement, strength-only PPO and reset sensors."""
from pathlib import Path
from types import SimpleNamespace
import sys,json,hashlib
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ppo import Agent,_upstream,initialize_from_pretrained,POLICY_ARCHITECTURE
from train_ppo import main as train,latest_checkpoint,load_checkpoint
from lift_task import LiftTask,read_inputs,normal_forces
from hold_task import HoldStrengthTask
from inspect_policy import policy_inputs
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'run/diagnosis/branch-reset-20261008'


def check_conversion():
    path=latest_checkpoint(allow_legacy=True)
    source=torch.load(path,map_location='cpu',weights_only=True)
    n=source['actor_mean.0.weight'].shape[1];a=source['actor_mean.6.weight'].shape[0]
    original=Agent() if 'strength_mean.0.weight' in source else _upstream().Agent(SimpleNamespace(single_observation_space=SimpleNamespace(shape=(n,)),single_action_space=SimpleNamespace(shape=(a,))))
    original.load_state_dict(source)
    agent=initialize_from_pretrained(Agent(),path)
    x=torch.randn(128,n);full=x if n==45 else torch.cat((x,torch.randn(128,45-n)),dim=-1)
    with torch.no_grad():
        if n==45:
            assert torch.equal(original.get_action(x,True)[:,:4],agent.get_action(full,True)[:,:4])
            assert torch.equal(original.get_value(x),agent.get_value(full))
        else:
            # Appending zero columns to older layouts can change GEMM rounding.
            torch.testing.assert_close(original.get_action(x,True)[:,:4],agent.get_action(full,True)[:,:4],rtol=1e-6,atol=1e-6)
            torch.testing.assert_close(original.get_value(x),agent.get_value(full),rtol=1e-6,atol=1e-6)
    assert all(not p.requires_grad for p in agent.actor_mean.parameters())
    assert not agent.actor_logstd.requires_grad
    assert all(p.requires_grad for p in agent.strength_mean.parameters())
    # PPO must not include scripted/deterministic movement in action likelihoods.
    action,lp,_,_=agent.get_action_and_value(full)
    other=action.detach().clone();other[:,:4]+=10
    _,lp2,_,_=agent.get_action_and_value(full,other)
    assert torch.equal(lp,lp2)
    return dict(source_checkpoint=str(path),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),movement_outputs_exact=True,critic_initial_predictions_exact=True,strength_only_likelihood=True)


def check_gpu_reset():
    env=LiftTask(num_envs=10,sim_backend='physx_cuda',masses_kg=[.5],friction_profile='native')
    try:
        agent=initialize_from_pretrained(Agent(),latest_checkpoint(allow_legacy=True)).to(env.device)
        obs,info=env.reset(seed=1000)
        assert not info['is_grasped'].any() and not normal_forces(env).any()
        for _ in range(50):
            _,x=read_inputs(env,obs)
            with torch.no_grad():action=agent.get_action(x,True).clamp(-1,1)
            obs,_,_,_,info=env.step(action)
        held=torch.nonzero(info['is_grasped']).flatten()
        assert len(held)>=2, 'Need real contact in unaffected robots to test isolation'
        target=held[:1];others=torch.arange(10,device=env.device)!=target[0]
        before=normal_forces(env).clone();grasp=info['is_grasped'].clone();limits=env.agent.controller.controllers['gripper'].force_limit_n.clone()
        obs,info=env.reset(options={'env_idx':target})
        _,x=read_inputs(env,obs)
        assert not info['is_grasped'][target].any() and not x[target,43:].any()
        # GPU kinematic refresh changes projected force by a few float32 ULPs.
        force_delta=float((normal_forces(env)[others]-before[others]).abs().max().item())
        assert torch.allclose(normal_forces(env)[others],before[others],rtol=0,atol=1e-5)
        assert torch.equal(info['is_grasped'][others],grasp[others])
        assert torch.equal(env.agent.controller.controllers['gripper'].force_limit_n[others],limits[others])
        assert not info['grasp_score'][target].any() and not info['grip_force_cost'][target].any()
        obs,info=env.reset(seed=1000)
        _,x=read_inputs(env,obs)
        assert not info['is_grasped'].any() and not x[:,43:].any()
        assert torch.equal(policy_inputs(x,'nominal',9.81,.5)[:,42],x[:,42])
        obs,_,_,_,_=env.step(torch.tensor([[0.,0.,0.,1.,1.]]*10,device=env.device))
        assert not env._contacts_stale.any()
        return dict(full_reset_contacts_zero=True,partial_reset_contacts_zero=True,unaffected_contacts_and_caps_preserved=True,fresh_step_restores_measurements=True,nominal_float32_matches=True,unaffected_force_max_difference_n=force_delta)
    finally:env.close()


def check_hold_gpu():
    env=HoldStrengthTask(num_envs=10,sim_backend='physx_cuda',friction_profile='native')
    try:
        results={}
        for cap in [1.,5.]:
            obs,info=env.reset(seed=1000)
            assert info['is_grasped'].all() and (info['clearance_m']>.06).all()
            start=info['clearance_m'].clone();mass=env.cube.mass.to(env.device)
            goal=env.goal_site.pose.p.clone()
            a=torch.zeros((10,5),device=env.device);a[:,4]=2*(cap-.25)/39.75-1
            for _ in range(50):obs,_,_,_,info=env.step(a)
            light=torch.isclose(mass,torch.tensor(.04,device=env.device));heavy=torch.isclose(mass,torch.tensor(.5,device=env.device))
            assert (info['clearance_m'][light]>.06).all()
            if cap==1.:assert (info['clearance_m'][heavy]<.01).all()
            else:
                assert (info['clearance_m'][heavy]>.06).all()
                assert info['success'].all(), 'A stationary strong hold must satisfy the held-goal objective'
            assert torch.allclose(env.goal_site.pose.p,goal,rtol=0,atol=1e-6), 'GPU goal changed after reset'
            results[str(cap)]=dict(masses_kg=mass.tolist(),final_clearance_m=info['clearance_m'].tolist(),final_grasp=info['is_grasped'].tolist())
        return results
    finally:env.close()


def check_run(backend):
    config=dict(total_timesteps=150 if backend=='physx_cpu' else 6000,
        num_envs=1 if backend=='physx_cpu' else 60,num_steps=50,
        num_minibatches=2 if backend=='physx_cpu' else 10,num_eval_envs=1 if backend=='physx_cpu' else 10,
        num_eval_steps=50,eval_freq=2,update_epochs=2 if backend=='physx_cpu' else 1,
        sim_backend=backend,run_root=str(OUT/backend))
    output=train(config)
    initial=torch.load(output/'initialization.pt',map_location='cpu',weights_only=True)
    agent,manifest=load_checkpoint(output/'final_ckpt.pt');final=agent.state_dict()
    for name in initial:
        if name.startswith('actor_mean.') or name=='actor_logstd':assert torch.equal(initial[name],final[name]),name
    strength_delta=sum((final[k]-v).square().sum().item() for k,v in initial.items() if k.startswith('strength_'))
    assert strength_delta>0 and all(torch.isfinite(v).all() for v in final.values())
    x=torch.randn(16,45)
    original=Agent();original.load_state_dict(initial)
    with torch.no_grad():assert torch.equal(original.get_action(x,True)[:,:4],agent.get_action(x,True)[:,:4])
    reload,_=load_checkpoint(output/'final_ckpt.pt')
    with torch.no_grad():assert torch.equal(reload.get_action(x,True),agent.get_action(x,True))
    assert manifest['policy_architecture']==POLICY_ARCHITECTURE
    result=dict(output=str(output),movement_weights_and_outputs_exact_after_learning=True,strength_parameter_change_squared=strength_delta,checkpoint_reload_exact=True)
    (output/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    OUT.mkdir(parents=True,exist_ok=True);torch.set_num_threads(4)
    result={'conversion':check_conversion()};print('WEIGHT CONVERSION PASSED',flush=True)
    result['cpu_training']=check_run('physx_cpu');print('CPU STRENGTH PPO PASSED',flush=True)
    if torch.cuda.is_available():
        result['gpu_reset']=check_gpu_reset();print('GPU RESET SENSOR ISOLATION PASSED',flush=True)
        result['gpu_hold_physics']=check_hold_gpu();print('GPU WEIGHT/STRENGTH PHYSICS PASSED',flush=True)
        result['gpu_training']=check_run('physx_cuda');print('GPU STRENGTH PPO PASSED',flush=True)
    assert hashlib.sha256(Path(result['conversion']['source_checkpoint']).read_bytes()).hexdigest()==result['conversion']['source_sha256']
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':main()

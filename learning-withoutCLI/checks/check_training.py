"""Optional integration checks; these do not prove learned weight adaptation."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lift_task import LiftTask, read_inputs, normal_forces, WEIGHT_INPUT_INDEX
from ppo import Agent, _upstream, initialize_from_pretrained
from train_ppo import main as train, load_checkpoint, latest_checkpoint
from inspect_policy import policy_inputs

ROOT=Path(__file__).resolve().parents[2]


def check_model():
    path=latest_checkpoint(allow_legacy=True)
    source=torch.load(path,map_location="cpu",weights_only=True)
    n=source["actor_mean.0.weight"].shape[1]
    actions=source["actor_mean.6.weight"].shape[0]
    original=_upstream().Agent(SimpleNamespace(
        single_observation_space=SimpleNamespace(shape=(n,)),
        single_action_space=SimpleNamespace(shape=(actions,))))
    if 'strength_mean.0.weight' in source:
        original = Agent()
    original.load_state_dict(source)
    updated=initialize_from_pretrained(Agent(),path)
    probe=torch.randn(6,n)
    extended=probe if n==45 else torch.cat([probe,torch.rand(6,45-n)*30],-1)
    with torch.no_grad():
        assert torch.allclose(original.get_action(probe,True),updated.get_action(extended,True)[:,:actions],atol=1e-6)
        assert torch.allclose(original.get_value(probe),updated.get_value(extended),atol=1e-6)
    if n<45:
        assert not updated.actor_mean[0].weight[:,n:].count_nonzero()
        assert not updated.critic[0].weight[:,n:].count_nonzero()
        assert torch.all(updated.get_action(extended,True)[:,4]==1.)
    print("Existing learned actions/value preserved when adding force inputs and strength output.")


def check_physics():
    env=LiftTask()
    try:
        starts=[]; inertia_per_kg=None
        for mass in (.04,.064,.1,.25,.5):
            torch.manual_seed(1000)
            obs,info=env.reset(seed=1000,options={"mass_kg":mass,"reconfigure":True})
            _,vector=read_inputs(env,obs)
            assert vector.shape==(1,45)
            assert np.isclose(vector[0,WEIGHT_INPUT_INDEX].item(),mass*9.81)
            assert torch.allclose(vector[:,43:],normal_forces(env))
            body=env.cube._bodies[0]
            ratio=np.array(body.inertia)/mass
            if inertia_per_kg is not None: assert np.allclose(ratio,inertia_per_kg)
            inertia_per_kg=ratio
            starts.append(vector[:,:42])
            fed=policy_inputs(vector,"nominal",9.81,.04)
            assert torch.equal(fed[:,:42],vector[:,:42]) and torch.equal(fed[:,43:],vector[:,43:])
            assert np.isclose(fed[0,42].item(),9.81*.04) and np.isclose(body.mass,mass)
            gripper=env.agent.controller.controllers["gripper"]
            for opening,target in ((-1.,-.01),(1.,.04)):
                decoded=gripper._preprocess_action(torch.tensor([[opening,0.]]))
                assert np.isclose(decoded[0,0].item(),target)
        assert all(torch.equal(starts[0],p) for p in starts)
        widths=[]
        for strength,expected in ((-1.,.25),(1.,40.)):
            env.reset(seed=1000,options={"mass_kg":.04,"reconfigure":True})
            _,_,_,_,info=env.step(torch.tensor([[0.,0.,0.,-1.,strength]]))
            g=env.agent.controller.controllers["gripper"]
            assert np.isclose(info["grip_limit_n"].item(),expected)
            assert all(np.isclose(j.get_force_limit().item(),expected) for j in g.joints)
            widths.append(env.agent.robot.get_qpos()[:,-2:].sum().item())
        assert widths[0]>widths[1]+1e-4, widths
        print("Mass/inertia, force observations, weight-only ablation and physical strength response passed:",widths)
    finally: env.close()


def check_gpu_controller():
    env=LiftTask(num_envs=5,sim_backend="physx_cuda")
    try:
        obs,_=env.reset(seed=1000)
        actions=torch.tensor([[0.,0.,0.,-1.,v] for v in (-1.,-.5,0.,.5,1.)],device=env.device)
        obs,_,_,_,info=env.step(actions)
        expected=torch.tensor([.25,10.1875,20.125,30.0625,40.],device=env.device)
        assert torch.allclose(info["grip_limit_n"],expected)
        g=env.agent.controller.controllers["gripper"]
        assert torch.allclose(g.joints[0].get_force_limit().to(env.device),expected)
        widths=env.agent.robot.get_qpos()[:,-2:].sum(-1)
        assert widths[0]>widths[-1]+1e-4
        env.reset(options={"env_idx":torch.tensor([0],device=env.device)})
        assert np.isclose(g.force_limit_n[0].item(),40.)
        assert torch.allclose(g.force_limit_n[1:],expected[1:])
        assert torch.isfinite(read_inputs(env,obs)[1]).all()
        print("Independent GPU force limits, physical response and partial-reset isolation passed.")
    finally: env.close()


def main():
    torch.set_num_threads(4)
    check_model();check_physics()
    output=train({"total_timesteps":150,"num_envs":1,"num_steps":50,"num_minibatches":2,
                  "num_eval_envs":1,"num_eval_steps":50,"eval_freq":2,"update_epochs":2,
                  "sim_backend":"physx_cpu","run_root":str(ROOT/"runs/checks/grip_extension/cpu_training")})
    agent,saved=load_checkpoint(output/"final_ckpt.pt")
    initial=torch.load(output/"initialization.pt",map_location="cpu",weights_only=True)
    current=agent.state_dict()
    assert all(torch.isfinite(v).all() for v in current.values())
    delta=sum((current[k]-initial[k]).square().sum().item() for k in current)
    assert delta>0 and not torch.equal(current['strength_mean.6.weight'][4],initial['strength_mean.6.weight'][4])
    for name in initial:
        if name.startswith('actor_mean.') or name=='actor_logstd':
            assert torch.equal(current[name],initial[name]), name
    probe=torch.randn(2,45);reloaded,_=load_checkpoint(output/"final_ckpt.pt")
    with torch.no_grad(): assert torch.equal(agent.get_action(probe,True),reloaded.get_action(probe,True))
    (output/"verification.json").write_text(json.dumps(dict(parameter_change_squared=delta,
        force_feature_actor_norm=agent.strength_mean[0].weight[:,43:].norm().item(),
        strength_output_change=(current['strength_mean.6.weight'][4]-initial['strength_mean.6.weight'][4]).norm().item(),
        checkpoint_reload_equal=True,note="Integration verified, not learned weight adaptation."),indent=2)+"\n")
    print("Finite PPO updates, new strength learning and exact checkpoint reload passed.")
    return output


if __name__=="__main__": main()

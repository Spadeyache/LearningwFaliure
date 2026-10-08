"""Optional integration checks, not a demonstration of learned adaptation.

Check original 42-input policy preservation, real mass/inertia, paired input
ablation, native gripper endpoints, PPO updates and checkpoint loading.
"""
import json
from pathlib import Path
import sys
import numpy as np
import torch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lift_task import INPUT_FIELDS, LiftTask, read_inputs
from ppo import Agent, _upstream, initialize_from_pretrained
from train_ppo import main as train, load_checkpoint
from inspect_policy import policy_inputs

ROOT = Path(__file__).resolve().parents[2]
PUBLISHED = ROOT / "runs/maniskill_pretrained/pick_cube/models/d674485bbffdd533914e52d272fdda34c0515608/ppo_pd_ee_delta_pos_ckpt.pt"


def check_model():
    if not PUBLISHED.exists():
        sys.path.insert(0,str(ROOT/"learning-withoutCLI/examples/maniskill_pick_cube"))
        from run_pretrained import download_model
        download_model("pd_ee_delta_pos")
    original = _upstream().Agent(type("Spaces",(),{
        "single_observation_space":type("Obs",(),{"shape":(42,)}),
        "single_action_space":type("Act",(),{"shape":(4,)})})())
    original.load_state_dict(torch.load(PUBLISHED,map_location="cpu",weights_only=True))
    updated = initialize_from_pretrained(Agent(),PUBLISHED)
    probe = torch.randn(6,42)
    with torch.no_grad():
        expected = original.get_action(probe, deterministic=True)
        for weight in (.3924,.62784,.981):
            inputs = torch.cat([probe,torch.full((6,1),weight)],dim=-1)
            assert torch.allclose(expected,updated.get_action(inputs,deterministic=True),atol=1e-6)
            assert torch.allclose(original.get_value(probe),updated.get_value(inputs),atol=1e-6)
    assert not updated.actor_mean[0].weight[:,-1].count_nonzero()
    assert not updated.critic[0].weight[:,-1].count_nonzero()
    print("Published behavior preserved at initialization; new weight input initially ignored.")


def check_physics():
    env=LiftTask()
    try:
        inertia_per_kg=None
        starts=[]
        for mass in (.04,.064,.1):
            torch.manual_seed(1000)
            obs, info=env.reset(seed=1000,options={"mass_kg":mass,"reconfigure":True})
            inputs, vector=read_inputs(env,obs)
            assert list(inputs)==INPUT_FIELDS and vector.shape==(1,43)
            body=env.cube._bodies[0]
            assert np.isclose(body.mass,mass) and np.isclose(vector[0,-1].item(),mass*9.81)
            ratio=np.array(body.inertia)/mass
            if inertia_per_kg is not None:
                assert np.allclose(ratio,inertia_per_kg)
            inertia_per_kg=ratio
            starts.append(vector[:,:42])
            fed=policy_inputs(vector,"nominal",9.81,.064)
            assert torch.equal(fed[:,:42],vector[:,:42])
            assert np.isclose(fed[0,-1].item(),9.81*.064)
            assert np.isclose(body.mass,mass) # Ablation changes the input, not the physics.
            gripper=env.agent.controller.controllers["gripper"]
            for opening, expected in ((-1.,float(gripper.config.lower)),(1.,float(gripper.config.upper))):
                decoded=gripper._preprocess_action(torch.tensor([[opening]]))
                assert np.isclose(decoded[0,0].item(),expected)
            obs,reward,_,_,_=env.step(torch.tensor([[0.,0.,0.,1.]]))
            assert torch.isfinite(read_inputs(env,obs)[1]).all() and torch.isfinite(reward).all()
        assert all(torch.equal(starts[0],s) for s in starts[1:])
        print("Mass/inertia/weight, matched resets, native opening and weight-input ablation passed.")
    finally:
        env.close()


def main():
    torch.set_num_threads(4)
    check_model()
    check_physics()
    output=train({"total_timesteps":150,"num_envs":1,"num_steps":50,"num_minibatches":2,
                  "num_eval_envs":1,"num_eval_steps":50,"eval_freq":2,"update_epochs":2,
                  "sim_backend":"physx_cpu","run_root":str(ROOT/"runs/checks/training")})
    agent,saved=load_checkpoint(output/"final_ckpt.pt")
    initial=torch.load(output/"initialization.pt",map_location="cpu",weights_only=True)
    current=agent.state_dict()
    assert all(torch.isfinite(v).all() for v in current.values())
    delta=sum((current[k]-initial[k]).square().sum().item() for k in current)
    assert delta>0
    assert agent.actor_mean[0].weight[:,-1].norm()>0
    probe=torch.randn(2,43)
    reloaded,_=load_checkpoint(output/"final_ckpt.pt")
    with torch.no_grad():
        assert torch.equal(agent.get_action(probe,True),reloaded.get_action(probe,True))
    (output/"verification.json").write_text(json.dumps({"parameter_change_squared":delta,
        "weight_input_actor_column_norm":agent.actor_mean[0].weight[:,-1].norm().item(),
        "checkpoint_reload_equal":True,"note":"Connectivity and updates verified; adaptation is not proven."},indent=2)+"\n")
    print("Finite PPO updates, weight-feature gradients and exact checkpoint reload passed.")
    return output


if __name__=="__main__":
    main()

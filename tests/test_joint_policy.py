"""Policy math and gradients only: no environments, rollouts or optimizer steps."""

from io import BytesIO
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

import torch
from torch.distributions import Normal


POLICY_PATH = Path(__file__).resolve().parents[1] / "learning-withoutCLI" / "ppo.py"
SPEC = importlib.util.spec_from_file_location("joint_policy_under_test", POLICY_PATH)
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


def memory_checkpoint(state_dict):
    """Exercise the real checkpoint loader without writing a policy to disk."""
    stream = BytesIO()
    torch.save(state_dict, stream)
    stream.seek(0)
    return stream


class JointPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_threads = torch.get_num_threads()
        torch.set_num_threads(1)

    @classmethod
    def tearDownClass(cls):
        torch.set_num_threads(cls.previous_threads)

    def setUp(self):
        random_context = torch.random.fork_rng(devices=[])
        random_context.__enter__()
        self.addCleanup(random_context.__exit__, None, None, None)
        torch.manual_seed(1337)
        self.inputs = torch.randn(8, 45)

    def test_joint_log_probability_and_entropy_include_all_five_actions(self):
        agent = POLICY.Agent(optimization_mode="joint")
        with torch.no_grad():
            agent.actor_logstd.copy_(torch.tensor([[-0.7, -0.3, 0.1, 0.2, 2.0]]))
            agent.strength_logstd.fill_(-0.4)
        expected_mean = torch.cat(
            [agent.actor_mean(self.inputs)[:, :4], agent.strength_mean(self.inputs)[:, 4:5]], dim=1
        )
        standard_deviation = torch.cat(
            [agent.actor_logstd[:, :4].exp(), agent.strength_logstd.exp()], dim=1
        )
        supplied = expected_mean.detach() + torch.tensor([0.5, 0.8, -0.25, 0.6, -0.4])
        action, log_probability, entropy, value = agent.get_action_and_value(self.inputs, supplied)
        independent = Normal(expected_mean, standard_deviation)
        torch.testing.assert_close(action, supplied)
        torch.testing.assert_close(log_probability, independent.log_prob(supplied).sum(1))
        torch.testing.assert_close(entropy, independent.entropy().sum(1))
        torch.testing.assert_close(value, agent.get_value(self.inputs))
        self.assertEqual(tuple(log_probability.shape), (8,))
        self.assertEqual(tuple(entropy.shape), (8,))

    def test_joint_backward_reaches_both_branches_and_critic_without_changing_weights(self):
        agent = POLICY.Agent(optimization_mode="joint")
        before = {name: value.clone() for name, value in agent.state_dict().items()}
        supplied = agent.get_action(self.inputs, deterministic=True).detach() + torch.tensor(
            [0.5, 0.8, -0.25, 0.6, -0.4]
        )
        _, log_probability, entropy, value = agent.get_action_and_value(self.inputs, supplied)
        loss = -log_probability.mean() - 0.13 * entropy.mean() + (value - 0.5).square().mean()
        loss.backward()

        for name in ("actor_mean", "strength_mean", "critic"):
            with self.subTest(branch=name):
                parameters = list(getattr(agent, name).parameters())
                self.assertTrue(all(parameter.requires_grad for parameter in parameters))
                self.assertTrue(all(parameter.grad is not None for parameter in parameters))
                self.assertTrue(all(torch.isfinite(parameter.grad).all() for parameter in parameters))
                self.assertGreater(sum(parameter.grad.abs().sum().item() for parameter in parameters), 0)
                self.assertGreater(parameters[0].grad.abs().sum().item(), 0)
        self.assertTrue(torch.all(agent.actor_logstd.grad[:, :4] != 0))
        self.assertGreater(agent.strength_logstd.grad.abs().sum().item(), 0)
        # Movement keeps a legacy fifth row/std only for checkpoint compatibility.
        self.assertEqual(agent.actor_mean[6].weight.grad[4].count_nonzero().item(), 0)
        self.assertEqual(agent.actor_mean[6].bias.grad[4].item(), 0)
        self.assertEqual(agent.actor_logstd.grad[:, 4:].count_nonzero().item(), 0)
        # The independent strength branch contributes only its last output.
        self.assertEqual(agent.strength_mean[6].weight.grad[:4].count_nonzero().item(), 0)
        self.assertEqual(agent.strength_mean[6].bias.grad[:4].count_nonzero().item(), 0)
        for name, value in agent.state_dict().items():
            self.assertTrue(torch.equal(value, before[name]), name)

    def test_joint_sampling_explores_every_action_and_reports_matching_likelihood(self):
        agent = POLICY.Agent(optimization_mode="joint")
        first = agent.get_action(self.inputs)
        second = agent.get_action(self.inputs)
        self.assertTrue(torch.all((first - second).abs().sum(dim=0) > 0))
        sampled, probability, entropy, _ = agent.get_action_and_value(self.inputs)
        _, recomputed, recomputed_entropy, _ = agent.get_action_and_value(self.inputs, sampled)
        torch.testing.assert_close(probability, recomputed)
        torch.testing.assert_close(entropy, recomputed_entropy)

    def test_default_strength_only_freezes_movement_and_ignores_its_likelihood(self):
        agent = POLICY.Agent()
        self.assertTrue(all(not parameter.requires_grad for parameter in agent.actor_mean.parameters()))
        self.assertFalse(agent.actor_logstd.requires_grad)
        deterministic = agent.get_action(self.inputs, deterministic=True)
        first, second = agent.get_action(self.inputs), agent.get_action(self.inputs)
        self.assertTrue(torch.equal(first[:, :4], deterministic[:, :4]))
        self.assertTrue(torch.equal(second[:, :4], deterministic[:, :4]))
        self.assertFalse(torch.equal(first[:, 4:], second[:, 4:]))

        supplied = deterministic.detach().clone()
        supplied[:, :4] += 50
        supplied[:, 4:] += 0.3
        _, probability, entropy, value = agent.get_action_and_value(self.inputs, supplied)
        strength = Normal(deterministic[:, 4:5], agent.strength_logstd.exp())
        torch.testing.assert_close(probability, strength.log_prob(supplied[:, 4:5]).sum(1))
        torch.testing.assert_close(entropy, strength.entropy().sum(1))
        (-probability.mean() + (value - 0.5).square().mean()).backward()
        self.assertTrue(all(parameter.grad is None for parameter in agent.actor_mean.parameters()))
        self.assertIsNone(agent.actor_logstd.grad)
        self.assertGreater(agent.strength_mean[0].weight.grad.abs().sum().item(), 0)
        self.assertGreater(agent.strength_logstd.grad.abs().sum().item(), 0)

    def test_switching_mode_preserves_branched_checkpoint_raw_means_and_values(self):
        strength = POLICY.Agent(optimization_mode="strength_only")
        # Deliberately distinguish branches so accidentally replacing strength is detectable.
        with torch.no_grad():
            strength.strength_mean[6].bias[4] = 0.71
            strength.strength_logstd.fill_(-1.25)
        joint = POLICY.initialize_from_pretrained(
            POLICY.Agent(optimization_mode="joint"), memory_checkpoint(strength.state_dict())
        )
        self.assertEqual(set(strength.state_dict()), set(joint.state_dict()))
        self.assertTrue(torch.equal(
            strength.get_action(self.inputs, deterministic=True),
            joint.get_action(self.inputs, deterministic=True),
        ))
        self.assertTrue(torch.equal(strength.get_value(self.inputs), joint.get_value(self.inputs)))
        self.assertTrue(all(parameter.requires_grad for parameter in joint.actor_mean.parameters()))
        self.assertTrue(joint.actor_logstd.requires_grad)

    def test_legacy_checkpoints_preserve_raw_movement_and_values_in_either_mode(self):
        for observation_count, action_count in ((42, 4), (43, 4), (45, 5)):
            with self.subTest(observations=observation_count, actions=action_count):
                spaces = SimpleNamespace(
                    single_observation_space=SimpleNamespace(shape=(observation_count,)),
                    single_action_space=SimpleNamespace(shape=(action_count,)),
                )
                legacy = POLICY._upstream().Agent(spaces)
                legacy_input = self.inputs[:, :observation_count]
                expected = legacy.get_action(legacy_input, deterministic=True)
                means = []
                for mode in ("strength_only", "joint"):
                    restored = POLICY.initialize_from_pretrained(
                        POLICY.Agent(optimization_mode=mode), memory_checkpoint(legacy.state_dict())
                    )
                    actual = restored.get_action(self.inputs, deterministic=True)
                    torch.testing.assert_close(actual[:, :action_count], expected, rtol=1e-5, atol=1e-6)
                    torch.testing.assert_close(restored.get_value(self.inputs), legacy.get_value(legacy_input))
                    if action_count == 4:
                        self.assertTrue(torch.equal(actual[:, 4], torch.ones(len(self.inputs))))
                    means.append(actual)
                self.assertTrue(torch.equal(means[0], means[1]))

    def test_unknown_optimization_mode_rejected(self):
        for mode in ("all", "strength", "", None):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                POLICY.Agent(optimization_mode=mode)


if __name__ == "__main__":
    unittest.main()

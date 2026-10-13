"""Prepare training artifacts in temporary directories without launching training."""

import ast
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from io import StringIO
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import torch


TRAINING_PATH = Path(__file__).resolve().parents[1] / "learning-withoutCLI"
SPEC = importlib.util.spec_from_file_location("training_preparation_under_test", TRAINING_PATH / "train_ppo.py")
TRAIN = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(TRAINING_PATH))
try:
    SPEC.loader.exec_module(TRAIN)
finally:
    sys.path.remove(str(TRAINING_PATH))


def read_json(path):
    return json.loads(path.read_text())


def flag_value(command, name):
    return command[command.index(name) + 1]


class TrainingPreparationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.run_root = Path(self.directory.name)
        self.previous_threads = torch.get_num_threads()
        self.addCleanup(torch.set_num_threads, self.previous_threads)
        random_context = torch.random.fork_rng(devices=[])
        random_context.__enter__()
        self.addCleanup(random_context.__exit__, None, None, None)
        self.contexts = ExitStack()
        self.addCleanup(self.contexts.close)
        self.guards = []
        for target in ("gymnasium.make", "subprocess.Popen", "torch.optim.Adam.step"):
            guard = self.contexts.enter_context(patch(target, side_effect=AssertionError(f"Preparation invoked {target}")))
            self.guards.append(guard)
        self.contexts.enter_context(redirect_stdout(StringIO()))
        self.contexts.enter_context(redirect_stderr(StringIO()))

    def tearDown(self):
        for guard in self.guards:
            guard.assert_not_called()

    def settings(self, **overrides):
        return {
            "checkpoint": None,
            "initialize_from_pretrained": False,
            "training_stage": "carry_joint",
            "total_timesteps": 9000,
            "run_root": str(self.run_root),
            **overrides,
        }

    def prepare(self, **overrides):
        return TRAIN.main(self.settings(**overrides), prepare_only=True)

    def test_preparation_records_joint_full_task_and_launches_nothing(self):
        output = self.prepare()
        manifest = read_json(output / "manifest.json")
        self.assertEqual(manifest["status"], "prepared")
        self.assertEqual(manifest["training_stage"], "carry_joint")
        self.assertEqual(manifest["optimization_mode"], "joint")
        self.assertEqual(manifest["environment"], TRAIN.ENV_ID)
        self.assertEqual(manifest["evaluation_environment"], TRAIN.ENV_ID)
        self.assertNotEqual(manifest["environment"], TRAIN.HOLD_ENV_ID)
        self.assertEqual(manifest["optimized_actions"], ["x", "y", "z", "finger_opening", "grip_strength_limit"])
        self.assertEqual(manifest["frozen_actions"], [])
        self.assertEqual(manifest["ppo_likelihood"], "joint five-action Gaussian")
        self.assertEqual(manifest["initialization"]["kind"], "random")
        self.assertEqual(manifest["planned_iterations"], 3)
        self.assertEqual(manifest["initialization"]["snapshot_sha256"], TRAIN.digest(output / "initialization.pt"))
        self.assertFalse((output / "final_ckpt.pt").exists())
        self.assertFalse((output / "console.log").exists())

        runtime = (output / "ppo_runtime.py").read_text()
        compile(runtime, str(output / "ppo_runtime.py"), "exec")
        syntax = ast.parse(runtime)
        agent_calls = [node for node in ast.walk(syntax) if isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Name) and node.func.id == "Agent"]
        self.assertEqual(len(agent_calls), 1)
        self.assertEqual({item.arg: ast.literal_eval(item.value) for item in agent_calls[0].keywords},
                         {"optimization_mode": "joint"})
        self.assertIn("optim.Adam((p for p in agent.parameters() if p.requires_grad),", runtime)
        self.assertNotIn("class Agent(nn.Module):", runtime)

        launch = read_json(output / "launch_command.json")
        command = launch["command"]
        self.assertEqual(flag_value(command, "--env-id"), TRAIN.ENV_ID)
        self.assertEqual(flag_value(command, "--checkpoint"), str(output / "initialization.pt"))
        transitions = int(flag_value(command, "--total-timesteps"))
        batch = int(flag_value(command, "--num-envs")) * int(flag_value(command, "--num-steps"))
        self.assertEqual(transitions // batch, 3)
        self.assertEqual(launch["cwd"], str(TRAIN.ROOT))
        self.assertEqual(read_json(output / "settings.json"), manifest["settings"])

    def test_from_prepared_preserves_initial_weights_and_can_override_iterations(self):
        original = self.prepare()
        original_bytes = (original / "initialization.pt").read_bytes()
        prepared = TRAIN.cli(["--from-prepared", str(original), "--prepare-only", "--iterations", "7"])
        self.assertNotEqual(original, prepared)
        self.assertEqual(original_bytes, (original / "initialization.pt").read_bytes())
        manifest = read_json(prepared / "manifest.json")
        self.assertEqual(manifest["status"], "prepared")
        self.assertEqual(manifest["planned_iterations"], 7)
        self.assertEqual(manifest["optimization_mode"], "joint")
        self.assertEqual(manifest["initialization"]["checkpoint"], str(original / "initialization.pt"))
        first = torch.load(original / "initialization.pt", map_location="cpu", weights_only=True)
        second = torch.load(prepared / "initialization.pt", map_location="cpu", weights_only=True)
        self.assertEqual(first.keys(), second.keys())
        for name in first:
            self.assertTrue(torch.equal(first[name], second[name]), name)
        command = read_json(prepared / "launch_command.json")["command"]
        self.assertEqual(int(flag_value(command, "--total-timesteps")), 7 * TRAIN.SETTINGS["num_envs"] * TRAIN.SETTINGS["num_steps"])

    def test_changed_prepared_snapshot_is_rejected_before_main(self):
        output = self.prepare()
        snapshot = output / "initialization.pt"
        snapshot.write_bytes(snapshot.read_bytes() + b"tampered")
        with patch.object(TRAIN, "main") as main, self.assertRaises(SystemExit) as caught:
            TRAIN.cli(["--from-prepared", str(output), "--prepare-only"])
        self.assertEqual(caught.exception.code, 2)
        main.assert_not_called()

    def test_stage_mapping_preserves_strength_modes_and_defaults_to_3500_joint_cycles(self):
        for stage, expected_env, expected_mode in (
            ("hold_strength", TRAIN.HOLD_ENV_ID, "strength_only"),
            ("carry_strength", TRAIN.ENV_ID, "strength_only"),
            ("carry_joint", TRAIN.ENV_ID, "joint"),
        ):
            with self.subTest(stage=stage):
                settings, environment, mode = TRAIN.resolve_settings({"training_stage": stage})
                self.assertEqual(environment, expected_env)
                self.assertEqual(mode, expected_mode)
                self.assertEqual(settings["training_stage"], stage)
        settings, _, mode = TRAIN.resolve_settings()
        self.assertEqual(mode, "joint")
        self.assertEqual(settings["total_timesteps"] // (settings["num_envs"] * settings["num_steps"]), 3500)
        self.assertEqual(list(self.run_root.iterdir()), [])

    def test_invalid_iteration_counts_and_settings_rejected_without_preparation(self):
        for iterations in ("0", "-1"):
            with self.subTest(iterations=iterations), patch.object(TRAIN, "main") as main:
                with self.assertRaises(SystemExit) as caught:
                    TRAIN.cli(["--prepare-only", "--iterations", iterations])
                self.assertEqual(caught.exception.code, 2)
                main.assert_not_called()
        for overrides in (
            {"total_timesteps": 0},
            {"total_timesteps": 3001},
            {"total_timesteps": True},
            {"training_stage": "unknown"},
            {"training_stage": "hold_strength", "partial_reset": True},
            {"iterations": 10},
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                TRAIN.resolve_settings(overrides)
        self.assertEqual(list(self.run_root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

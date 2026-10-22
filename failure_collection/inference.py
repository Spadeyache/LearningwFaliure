"""Compatibility entrypoint; active implementation: robot_adaptation.policy.frozen_v1."""
import importlib
import sys

sys.modules[__name__] = importlib.import_module("robot_adaptation.policy.frozen_v1")

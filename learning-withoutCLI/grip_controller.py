"""Compatibility entrypoint; active implementation: robot_adaptation.simulation.grip_controller."""
import importlib
import sys

sys.modules[__name__] = importlib.import_module("robot_adaptation.simulation.grip_controller")

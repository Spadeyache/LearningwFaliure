"""Compatibility entrypoint; active implementation: robot_adaptation.collection.schema."""
import importlib
import sys

sys.modules[__name__] = importlib.import_module("robot_adaptation.collection.schema")

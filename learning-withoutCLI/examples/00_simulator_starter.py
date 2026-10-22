"""Compatibility entrypoint; implementation moved to robot_adaptation.policy.examples.00_simulator_starter."""
from pathlib import Path
import importlib
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
if __name__ == "__main__":
    runpy.run_module('robot_adaptation.policy.examples.00_simulator_starter', run_name="__main__")
else:
    _implementation = importlib.import_module('robot_adaptation.policy.examples.00_simulator_starter')
    globals().update({name: value for name, value in vars(_implementation).items()
                      if not name.startswith("__")})

"""Compatibility entrypoint; active implementation: robot_adaptation.collection.varied."""
import importlib
import sys

if __name__ == "__main__":
    importlib.import_module("robot_adaptation.collection.varied").main()
else:
    sys.modules[__name__] = importlib.import_module("robot_adaptation.collection.varied")

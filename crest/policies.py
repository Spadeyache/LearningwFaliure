"""Compatibility entry point; implementation lives in experiments.crest.policies."""
import importlib as _importlib
from pathlib import Path as _Path
import sys as _sys

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
_module = _importlib.import_module("experiments.crest.policies")
if __name__ == "__main__":
    raise SystemExit(_module.main())
else:
    _sys.modules[__name__] = _module
    globals().update(_module.__dict__)

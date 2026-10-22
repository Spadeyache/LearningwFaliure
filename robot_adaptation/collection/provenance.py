"""Source provenance for collection commands and their shared dependencies."""
from pathlib import Path
import hashlib
import shutil

from robot_adaptation.paths import ROOT


def source_paths(extra=()):
    """Return canonical implementations, never the legacy forwarding modules."""
    package = ROOT / "robot_adaptation"
    paths = [package / "__init__.py", package / "paths.py",
             package / "policy/__init__.py", package / "policy/frozen_v1.py"]
    for folder in (package / "collection", package / "simulation"):
        paths.extend(folder.glob("*.py"))
        paths.extend(folder.glob("*LICENSE*"))
    paths.extend(Path(path) for path in extra)
    return sorted(set(paths))


def source_hashes(extra=()):
    return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source_paths(extra)}


def snapshot_sources(output, extra=()):
    """Keep package-relative paths so shared implementation imports remain clear."""
    for path in source_paths(extra):
        target = Path(output) / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

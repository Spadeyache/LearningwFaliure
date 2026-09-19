"""Split successful episodes by identity, never by timestep."""
import argparse
import json
from pathlib import Path
import numpy as np
from pose_model import file_hash, load_episode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/pickcube100"))
    parser.add_argument("--output", type=Path, default=Path("results/splits.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to replace an existing split: {args.output}")
    records = []
    identities = set()
    for path in sorted(args.data_dir.glob("episode_*.npz")):
        load_episode(path, require_success=True)
        with np.load(path, allow_pickle=False) as data:
            identity = (str(data["source_sha256"]), int(data["source_episode_id"]))
            seed = int(data["seed"])
        if identity in identities:
            raise ValueError(f"Duplicate source episode: {path}")
        identities.add(identity)
        records.append({"file": path.name, "sha256": file_hash(path),
                        "source_sha256": identity[0], "source_episode_id": identity[1],
                        "seed": seed})
    n = len(records)
    if n < 40:
        raise ValueError("Collect at least 40 clean episodes for four separate splits")
    order = np.random.default_rng(args.seed).permutation(n)
    shuffled = [records[int(i)] for i in order]
    a, b, c = int(n*.60), int(n*.70), int(n*.85)
    splits = {"train": shuffled[:a], "validation": shuffled[a:b],
              "calibration": shuffled[b:c], "test": shuffled[c:]}
    result = {"schema_version": 1, "seed": args.seed, "data_dir": str(args.data_dir),
              "splits": splits}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print({key: len(value) for key, value in splits.items()})


if __name__ == "__main__":
    main()

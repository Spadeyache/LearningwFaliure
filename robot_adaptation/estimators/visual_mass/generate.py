"""Render initial RGB images for a controlled visual-size mass prior.

This is a new toy dataset: equally dense cubes have mass proportional to volume.
It does not turn the older independently randomized-mass episodes into a visual
mass dataset. No policy runs, robot actions, or failure labels are used here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


DENSITY_KG_M3 = 1000.0
SIDE_RANGE_M = (0.025, 0.075)
CAMERA_EYE = (0.22, 0.22, 0.20)
CAMERA_TARGET = (0.0, 0.0, 0.025)
CAMERA_FOV_RAD = 0.65


def _validate(objects: int, views: int, seed: int, image_size: int) -> None:
    for name, value in (("objects", objects), ("views", views),
                        ("seed", seed), ("image_size", image_size)):
        if type(value) is not int:
            raise ValueError(f"{name} must be an integer")
    if objects < 16 or objects % 8:
        raise ValueError("objects must be at least 16 and divisible by 8")
    if views < 1:
        raise ValueError("views must be positive")
    if not 0 <= seed < 2**31:
        raise ValueError("seed must be in [0, 2**31)")
    if not 32 <= image_size <= 1024:
        raise ValueError("image_size must be in [32, 1024]")
    if not np.isfinite([DENSITY_KG_M3, *SIDE_RANGE_M, *CAMERA_EYE,
                        *CAMERA_TARGET, CAMERA_FOV_RAD]).all():
        raise ValueError("Scene configuration must contain finite values")


def _write_manifest(output: Path, manifest: dict) -> None:
    temporary = output / ".dataset.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    temporary.replace(output / "dataset.json")


def _make_environment(properties: dict, image_size: int):
    # Import the simulator only when generating data; inspecting this module or
    # parsing its CLI does not create a graphics or physics context.
    from robot_adaptation.simulation.environment import CollectionEnv
    from mani_skill.sensors.camera import CameraConfig
    from mani_skill.utils import sapien_utils

    class InitialImageEnv(CollectionEnv):
        @property
        def _default_sensor_configs(self):
            pose = sapien_utils.look_at(eye=CAMERA_EYE, target=CAMERA_TARGET)
            return [CameraConfig("base_camera", pose, image_size, image_size,
                                 CAMERA_FOV_RAD, 0.005, 10.0)]

    return InitialImageEnv(properties, render_backend="cpu")


def generate_dataset(output: str | Path, *, objects: int = 96, views: int = 4,
                     seed: int = 42, image_size: int = 96) -> dict:
    """Render and save an object-disjoint dataset in a fresh output directory.

    Consecutive groups of eight sorted cube sizes contain six training objects,
    one validation object and one test object. A random permutation within each
    group chooses the held-out objects; every view of an object shares its split.
    Mass is read back from PhysX after building each scene, rather than inferred
    from a filename, a color, or a visible annotation.
    """
    _validate(objects, views, seed, image_size)
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new dataset directory; already exists: {output}")

    from robot_adaptation.simulation.environment import normalized_properties
    import torch

    torch.set_num_threads(1)
    sizes = np.linspace(*SIDE_RANGE_M, objects)
    split_rng = np.random.default_rng(seed)
    splits: dict[int, str] = {}
    for start in range(0, objects, 8):
        indices = split_rng.permutation(np.arange(start, start + 8))
        splits.update({int(index): "train" for index in indices[:6]})
        splits[int(indices[6])] = "val"
        splits[int(indices[7])] = "test"

    config = {
        "objects": objects, "views": views, "seed": seed,
        "image_size": image_size, "shape": "cube",
        "side_range_m": list(SIDE_RANGE_M),
        "density_kg_m3": DENSITY_KG_M3,
        "object_color_rgba": [1.0, 0.0, 0.0, 1.0],
        "static_friction": 0.3, "dynamic_friction": 0.3,
        "finger_friction": 2.0, "table_friction": 0.3,
        "camera": {"uid": "base_camera", "eye_m": list(CAMERA_EYE),
                   "target_m": list(CAMERA_TARGET), "fov_rad": CAMERA_FOV_RAD,
                   "near_m": 0.005, "far_m": 10.0},
        "pose_nuisance": {"xy_range_m": [-0.01, 0.01],
                          "yaw_range_rad": [-float(np.pi), float(np.pi)]},
        "split_rule": "per_8_sorted_sizes_random_6train_1val_1test",
        "sim_backend": "physx_cpu", "render_backend": "cpu",
        "capture": "initial_reset_before_contact_or_any_action",
        "label_source": "PhysX body mass readback in kilograms",
        "purpose": "controlled_constant_density_visual_size_mass_prior",
        "limitation": "Not general mass inference: size predicts mass by construction; "
                      "not the original independently varied mass dataset.",
    }
    manifest = {"schema_version": 1, "image_size": image_size,
                "config": config, "status": "running", "records": []}
    output.mkdir(parents=True, exist_ok=False)
    (output / "images").mkdir()
    _write_manifest(output, manifest)
    env = None
    try:
        for object_index, side in enumerate(sizes):
            object_id = f"cube_{object_index:04d}"
            expected_mass = float(DENSITY_KG_M3 * side**3)
            for view_index in range(views):
                rng = np.random.default_rng(np.random.SeedSequence(
                    [seed, object_index, view_index, 109]))
                reset_seed = int(rng.integers(0, 2**31))
                x, y = rng.uniform(-0.01, 0.01, size=2)
                yaw = float(rng.uniform(-np.pi, np.pi))
                properties = normalized_properties({
                    "shape": "cube", "size_xyz_m": [float(side)] * 3,
                    "mass_kg": expected_mass,
                    "static_friction": 0.3, "dynamic_friction": 0.3,
                    "initial_pose_world": [float(x), float(y), float(side / 2),
                                           float(np.cos(yaw / 2)), 0.0, 0.0,
                                           float(np.sin(yaw / 2))],
                })
                if env is None:
                    env = _make_environment(properties, image_size)
                    reconfigure = False  # Constructor has already built this object.
                else:
                    reconfigure = view_index == 0
                    env.properties = properties
                env.reset(seed=reset_seed, options={"reconfigure": reconfigure})
                physics = env.physics_readback()
                mass = float(physics["mass_kg"])
                if not np.isfinite(mass) or not np.isclose(mass, expected_mass, rtol=1e-5):
                    raise RuntimeError("Actual simulator mass does not match configured mass")
                rgb = env._get_obs_sensor_data()["base_camera"]["rgb"][0]
                rgb = rgb.detach().cpu().numpy()
                if (rgb.dtype != np.uint8 or rgb.shape != (image_size, image_size, 3)
                        or rgb.max() == rgb.min()):
                    raise RuntimeError("Renderer did not produce a nonconstant RGB image")
                image_path = Path("images") / f"{object_id}_view_{view_index:03d}.png"
                Image.fromarray(rgb).save(output / image_path)
                manifest["records"].append({
                    "image": image_path.as_posix(), "object_id": object_id,
                    "split": splits[object_index], "mass_kg": mass,
                    "size_m": float(side), "seed": reset_seed,
                    "initial_pose_world": properties["initial_pose_world"],
                })
            _write_manifest(output, manifest)
            print(f"Rendered {object_index + 1}/{objects} objects "
                  f"({len(manifest['records'])} images)", flush=True)
        manifest["status"] = "complete"
        _write_manifest(output, manifest)
        return manifest
    except BaseException:
        manifest["status"] = "incomplete"
        _write_manifest(output, manifest)
        raise
    finally:
        if env is not None:
            env.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--objects", type=int, default=96)
    parser.add_argument("--views", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--image-size", type=int, default=96)
    args = parser.parse_args()
    manifest = generate_dataset(args.output, objects=args.objects, views=args.views,
                                seed=args.seed, image_size=args.image_size)
    print(f"Saved {len(manifest['records'])} initial images to "
          f"{args.output.resolve() / 'dataset.json'}", flush=True)


if __name__ == "__main__":
    main()

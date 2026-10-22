"""A CPU PickCube environment with explicit, independently varied object physics.

The policy interface remains upstream PickCube's 42 state values / four actions.
Construct a new environment when geometry or physics properties change.  This
keeps properties out of episode RNG state and avoids GPU material update limits.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Callable

import numpy as np
import sapien
import sapien.physx as physx
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.utils.building import actors
from mani_skill.utils.geometry.rotation_conversions import quaternion_to_matrix
from mani_skill.utils.scene_builder.table import TableSceneBuilder
from mani_skill.utils.structs.pose import Pose


DEFAULT_PROPERTIES = {
    "shape": "cube",
    "size_xyz_m": [0.04, 0.04, 0.04],
    "mass_kg": 0.064,
    "com_offset_m": [0.0, 0.0, 0.0],
    "static_friction": 0.3,
    "dynamic_friction": 0.3,
    "restitution": 0.0,
    "linear_damping": 0.0,
    "angular_damping": 0.05,
    "finger_friction": 2.0,
    "table_friction": 0.3,
    "initial_pose_world": None,
    "goal_position_world": None,
    "inertia_principal_kg_m2": None,
}


def _vector(value, size: int, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.shape != (size,) or not np.isfinite(array).all():
        raise ValueError(f"{name} must contain {size} finite values")
    return array


def normalized_properties(properties: dict | None = None) -> dict:
    """Validate explicit physics and return a fresh, JSON-safe property mapping.

    Sizes are full geometric extents. Sphere extents must agree and denote its
    diameter. COM is in the object's geometric frame. If inertia is omitted, the
    uniform primitive's principal moments are assigned *about the supplied COM*;
    an offset COM therefore models synthetic independent mass properties, not a
    claim about a particular density distribution. Supplied moments also use the
    object axes, with the inertial-frame rotation fixed to identity.
    """
    if properties is not None and not isinstance(properties, dict):
        raise ValueError("properties must be a mapping")
    unknown = set(properties or {}) - set(DEFAULT_PROPERTIES)
    if unknown:
        raise ValueError(f"Unknown object properties: {sorted(unknown)}")
    result = deepcopy(DEFAULT_PROPERTIES)
    result.update(deepcopy(properties or {}))
    if result["shape"] not in ("cube", "box", "sphere"):
        raise ValueError("shape must be cube, box, or sphere")
    size = _vector(result["size_xyz_m"], 3, "size_xyz_m")
    if np.any(size <= 0):
        raise ValueError("size_xyz_m must be strictly positive")
    if result["shape"] in ("cube", "sphere") and not np.allclose(size, size[0], rtol=1e-7, atol=1e-10):
        raise ValueError("cube/sphere require equal size_xyz_m extents; use box otherwise")
    result["size_xyz_m"] = size.tolist()
    for name in ("mass_kg", "static_friction", "dynamic_friction", "restitution", "finger_friction", "table_friction", "linear_damping", "angular_damping"):
        value = float(result[name])
        if not np.isfinite(value) or value < 0 or (name == "mass_kg" and value == 0):
            raise ValueError(f"{name} must be finite and {'positive' if name == 'mass_kg' else 'nonnegative'}")
        result[name] = value
    if result["dynamic_friction"] > result["static_friction"]:
        raise ValueError("dynamic_friction must not exceed static_friction")
    if result["restitution"] > 1:
        raise ValueError("restitution must be between zero and one")
    com = _vector(result["com_offset_m"], 3, "com_offset_m")
    outside = np.linalg.norm(com) >= size[0] / 2 if result["shape"] == "sphere" else np.any(np.abs(com) >= size / 2)
    if outside:
        raise ValueError("com_offset_m must lie strictly inside the object geometry")
    result["com_offset_m"] = com.tolist()
    if result["inertia_principal_kg_m2"] is not None:
        inertia = _vector(result["inertia_principal_kg_m2"], 3, "inertia_principal_kg_m2")
        if np.any(inertia <= 0) or 2 * inertia.max() > inertia.sum() + 1e-12:
            raise ValueError("Principal inertia must be positive and satisfy the triangle inequality")
        result["inertia_principal_kg_m2"] = inertia.tolist()
    if result["initial_pose_world"] is not None:
        pose = _vector(result["initial_pose_world"], 7, "initial_pose_world")
        norm = np.linalg.norm(pose[3:])
        if norm < 1e-12:
            raise ValueError("initial_pose_world quaternion must be nonzero (wxyz order)")
        pose[3:] /= norm
        result["initial_pose_world"] = pose.tolist()
    if result["goal_position_world"] is not None:
        result["goal_position_world"] = _vector(result["goal_position_world"], 3, "goal_position_world").tolist()
    return result


class CollectionEnv(PickCubeEnv):
    """Stock Panda pick task, with fixed properties for a batch of episodes.

    ``physics_step_callback(env)`` is called after each completed physics step,
    while its contacts and states are fresh. Leave it None outside collection.
    Success deliberately retains the upstream definition: within 2.5 cm of the
    goal and each arm joint speed <= 0.2 rad/s (no separate grasp requirement).
    """

    def __init__(self, properties: dict | None = None, **kwargs):
        self.properties = normalized_properties(properties)
        self.physics_step_callback: Callable[[CollectionEnv], None] | None = None
        self._contacts_stale = True
        required = {"num_envs": 1, "robot_uids": "panda", "obs_mode": "state", "control_mode": "pd_ee_delta_pos", "sim_backend": "physx_cpu"}
        for key, expected in required.items():
            if key in kwargs and kwargs[key] != expected:
                raise ValueError(f"CollectionEnv requires {key}={expected!r}")
            kwargs[key] = expected
        kwargs.setdefault("render_backend", "cpu")
        kwargs.setdefault("reward_mode", "normalized_dense")
        kwargs.setdefault("enhanced_determinism", True)
        kwargs.setdefault("sensor_configs", {"shader_pack": "minimal"})
        kwargs.setdefault("human_render_camera_configs", {"shader_pack": "minimal"})
        super().__init__(**kwargs)

    @staticmethod
    def _material(body, static: float, dynamic: float, restitution: float):
        for shape in body.get_collision_shapes():
            shape.physical_material = physx.PhysxMaterial(static, dynamic, restitution)

    def _load_agent(self, options):
        super()._load_agent(options)
        coefficient = self.properties["finger_friction"]
        for link in (self.agent.finger1_link, self.agent.finger2_link):
            for body in link._bodies:
                self._material(body, coefficient, coefficient, 0.0)

    def _load_scene(self, options):
        self.table_scene = TableSceneBuilder(self, robot_init_qpos_noise=self.robot_init_qpos_noise)
        self.table_scene.build()
        table_mu = self.properties["table_friction"]
        for body in self.table_scene.table._bodies:
            self._material(body, table_mu, table_mu, 0.0)
        half_sizes = np.asarray(self.properties["size_xyz_m"]) / 2
        # Upstream reset uses this scalar for default spawn/goal height. We
        # replace object Z with its orientation-aware support height below.
        self.cube_half_size = float(half_sizes[2])
        common = dict(scene=self.scene, color=self.object_color_rgba(), name="cube", initial_pose=sapien.Pose(p=[0, 0, half_sizes[2]]))
        if self.properties["shape"] == "sphere":
            self.cube = actors.build_sphere(radius=float(half_sizes[0]), **common)
        else:
            self.cube = actors.build_box(half_sizes=half_sizes.tolist(), **common)
        mass = self.properties["mass_kg"]
        size = np.asarray(self.properties["size_xyz_m"])
        if self.properties["inertia_principal_kg_m2"] is not None:
            inertia = np.asarray(self.properties["inertia_principal_kg_m2"])
        elif self.properties["shape"] == "sphere":
            inertia = np.full(3, 2 * mass * half_sizes[0] ** 2 / 5)
        else:
            inertia = mass * (np.sum(size**2) - size**2) / 12
        for body in self.cube._bodies:
            body.set_linear_damping(self.properties["linear_damping"])
            body.set_angular_damping(self.properties["angular_damping"])
            body.set_mass(mass)
            body.set_cmass_local_pose(sapien.Pose(p=self.properties["com_offset_m"]))
            body.set_inertia(inertia)
            self._material(body, self.properties["static_friction"], self.properties["dynamic_friction"], self.properties["restitution"])
            if not np.isclose(body.mass, mass) or not np.allclose(body.inertia, inertia, rtol=1e-5, atol=1e-12):
                raise RuntimeError("PhysX mass/inertia did not match requested object properties")
            if not np.allclose(body.cmass_local_pose.p, self.properties["com_offset_m"], atol=1e-8):
                raise RuntimeError("PhysX COM did not match requested offset")
        self.goal_site = actors.build_sphere(self.scene, radius=self.goal_thresh, color=[0, 1, 0, 1], name="goal_site", body_type="kinematic", add_collision=False, initial_pose=sapien.Pose())
        self._hidden_objects.append(self.goal_site)

    def object_color_rgba(self):
        """Appearance hook; the collection default remains the original red."""
        return [1, 0, 0, 1]

    def support_height(self, quaternion=None) -> torch.Tensor:
        """Vertical distance from geometric center to its lowest point, in m.

        Accept a wxyz quaternion or a batch; omitted means current object pose.
        The return value is always a length-N torch tensor, including N=1.
        """
        q = self.cube.pose.q if quaternion is None else torch.as_tensor(quaternion, dtype=torch.float32, device=self.device)
        if q.ndim == 1:
            q = q[None]
        half_sizes = torch.tensor(self.properties["size_xyz_m"], device=self.device) / 2
        if self.properties["shape"] == "sphere":
            return torch.full((len(q),), float(half_sizes[0]), device=self.device)
        return (quaternion_to_matrix(q)[:, 2, :].abs() * half_sizes).sum(-1)

    def _initialize_episode(self, env_idx, options):
        self._contacts_stale = True
        super()._initialize_episode(env_idx, options)
        override = self.properties["initial_pose_world"]
        if override is None:
            pose = self.cube.pose.raw_pose.clone()
            pose[:, 2] = self.support_height(pose[:, 3:])
        else:
            pose = torch.tensor(override, dtype=torch.float32, device=self.device)[None]
            if (pose[:, 2] + 1e-6 < self.support_height(pose[:, 3:])).any():
                raise ValueError("initial_pose_world would put the object below the tabletop")
        self.cube.set_pose(Pose.create(pose))
        if self.properties["goal_position_world"] is not None:
            self.goal_site.set_pose(Pose.create_from_pq(self.properties["goal_position_world"], device=self.device))

    def _after_simulation_step(self):
        super()._after_simulation_step()
        self._contacts_stale = False
        if self.physics_step_callback is not None:
            self.physics_step_callback(self)

    def evaluate(self):
        info = super().evaluate()
        # Reset teleports the body without refreshing PhysX's contact cache.
        if self._contacts_stale:
            info["is_grasped"] = torch.zeros_like(info["is_grasped"])
        return info

    @staticmethod
    def _materials(body):
        return [{name: float(getattr(shape.physical_material, name)) for name in ("static_friction", "dynamic_friction", "restitution")} for shape in body.get_collision_shapes()]

    def physics_readback(self) -> dict:
        """Actual physics values from the built scene, separate from requests."""
        body = self.cube._bodies[0]
        collision = body.get_collision_shapes()[0]
        if self.properties["shape"] == "sphere":
            extents = [2 * float(collision.radius)] * 3
        else:
            extents = (2 * np.asarray(collision.half_size)).tolist()
        gravity = np.asarray(self.scene.px.get_config().gravity, dtype=float)
        com_pose = body.cmass_local_pose
        return {
            "shape": self.properties["shape"],
            "size_xyz_m": extents,
            "mass_kg": float(body.mass),
            "weight_n": float(body.mass * np.linalg.norm(gravity)),
            "gravity_world_m_s2": gravity.tolist(),
            "com_offset_m": np.asarray(com_pose.p).tolist(),
            "com_pose_object_m_wxyz": np.concatenate([com_pose.p, com_pose.q]).tolist(),
            "inertia_principal_kg_m2": np.asarray(body.inertia).tolist(),
            "inertia_model": "explicit_principal_moments_about_supplied_com" if self.properties["inertia_principal_kg_m2"] is not None else "uniform_primitive_moments_about_supplied_com_synthetic_if_offset",
            "object_materials": self._materials(body),
            "finger_materials": [self._materials(link._bodies[0]) for link in (self.agent.finger1_link, self.agent.finger2_link)],
            "table_materials": self._materials(self.table_scene.table._bodies[0]),
            "linear_damping": float(body.linear_damping),
            "angular_damping": float(body.angular_damping),
            "simulation_frequency_hz": self.sim_freq,
            "control_frequency_hz": self.control_freq,
            "goal_threshold_m": self.goal_thresh,
        }

"""Visual observation adapter for the supplied-estimate pick/lift environment.

The runtime captures the same calibrated RGB view used to train the visual-mass
estimator. Updating the reported estimate changes the policy's observation only;
the object's physical mass, task, controller and reward retain their semantics.
"""
from __future__ import annotations

import numpy as np
from mani_skill.sensors.camera import CameraConfig
from mani_skill.utils import sapien_utils

from robot_adaptation.estimators.visual_mass.generate import (
    CAMERA_EYE,
    CAMERA_FOV_RAD,
    CAMERA_TARGET,
)
from robot_adaptation.simulation.collection_lift import WeightedCollectionEnv


class VisualPolicyEnv(WeightedCollectionEnv):
    """WeightedCollectionEnv with the visual estimator's initial RGB camera."""

    def __init__(self, properties, *, reported_mass_kg, goal_clearance_m,
                 grip_force_limits_n, spawn_offset_m=None,
                 spawn_yaw_offset_rad=0.0, image_size=96):
        if type(image_size) is not int or not 32 <= image_size <= 1024:
            raise ValueError("image_size must be an integer in [32, 1024]")
        self.image_size = image_size
        self.set_mass_estimate(reported_mass_kg)
        super().__init__(
            properties, reported_mass_kg=self.reported_mass_kg,
            goal_clearance_m=goal_clearance_m,
            grip_force_limits_n=grip_force_limits_n,
            spawn_offset_m=spawn_offset_m,
            spawn_yaw_offset_rad=spawn_yaw_offset_rad,
        )

    @property
    def _default_sensor_configs(self):
        pose = sapien_utils.look_at(eye=CAMERA_EYE, target=CAMERA_TARGET)
        return [CameraConfig(
            "base_camera", pose, self.image_size, self.image_size,
            CAMERA_FOV_RAD, 0.005, 10.0,
        )]

    def capture_initial_rgb(self) -> np.ndarray:
        """Capture RGB from the current reset state without resetting or acting.

        Call immediately after the runtime's one reset. Sensor capture hides
        simulator-only goal markers, just as the estimator dataset generator does.
        The returned image owns its memory independently of the renderer.
        """
        rgb = self._get_obs_sensor_data()["base_camera"]["rgb"][0]
        rgb = rgb.detach().cpu().numpy()
        if (rgb.dtype != np.uint8
                or rgb.shape != (self.image_size, self.image_size, 3)
                or rgb.max() == rgb.min()):
            raise RuntimeError("Renderer did not produce a nonconstant RGB image")
        return rgb.copy()

    def set_mass_estimate(self, mass_kg) -> None:
        """Set the policy's assumed mass in kg without changing physical mass.

        A reset observation already returned to the caller is not mutated. Before
        its first action, the runtime must refresh that observation's weight entry
        using this estimate and ``gravity_m_s2``; subsequent observations use it
        through the inherited observation interface.
        """
        if isinstance(mass_kg, (bool, np.bool_)):
            raise ValueError("mass_kg must be positive and finite")
        try:
            value = float(mass_kg)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("mass_kg must be positive and finite") from error
        if not np.isfinite(value) or value <= 0:
            raise ValueError("mass_kg must be positive and finite")
        self.reported_mass_kg = value

    @property
    def gravity_m_s2(self) -> float:
        """Magnitude of the active simulator's gravity, in metres per second²."""
        return float(np.linalg.norm(self.scene.px.get_config().gravity))

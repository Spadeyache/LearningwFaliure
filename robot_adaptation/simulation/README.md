# Shared simulation

- `environment.py`: explicit object geometry/physics, initial poses, sensor access,
  physical readbacks and stock task support.
- `grip_controller.py`: shared grip motor-cap controller.
- `collection_lift.py`: supplied-weight task for the frozen v1 collection policy.
- `training_lift.py` and `training_hold.py`: learner task variants.

Task variants keep their existing rewards, observations and physical assumptions.
Collection and estimator generation import these modules; the simulator does not
import collection commands or experiment drivers.

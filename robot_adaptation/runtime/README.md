# Runtime integration

This package is the place for composing an estimator with the policy and running
that system. A combined estimator-to-policy episode runner is not implemented yet.

Available inference lives with its model:

- `robot_adaptation.estimators.visual_mass.predict`: initial RGB image to mass in kg.
- `robot_adaptation.policy.train.load_checkpoint`: current learner checkpoint loading.
- `robot_adaptation.policy.frozen_v1.load_agent`: historical collection checkpoint loading.
- `robot_adaptation.policy.inspect`: saved-policy rollout and inspection command.

The next integration will select the correct policy architecture, convert the
estimated mass to the policy's supplied-weight units, and pass it with the normal
observations. Training loops remain in the model packages.

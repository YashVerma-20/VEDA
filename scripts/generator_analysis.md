# Generator Equations
- `lifetime_hours` is sampled uniformly between 300 and 1200 (if <300, resampled to 300-600).
- `start_time` is strictly defined as: `lifetime_hours - 250.0 + 0.25`
- `initial_health_global` = 1.0
- `health_slope` = `(1.0 - 0.15) / lifetime_hours`
- In the loop for each observation `t_hours`:
  - `t_hours = start_time + step * 0.25`
  - `health = 1.0 - health_slope * t_hours`
  - `rul = lifetime_hours - t_hours`

Because the observation window is hardcoded to start exactly 249.75 hours before the end of life (`lifetime_hours - 250.0 + 0.25`), the RUL equation is:
`rul = lifetime_hours - (lifetime_hours - 250.0 + 0.25 + step * 0.25)`
`rul = 249.75 - step * 0.25`

This means every single vehicle has an identical initial RUL of 249.75 and an identical final RUL of 0.0. EOL always occurs exactly at the last observation.

# Proposed Correction
Instead of anchoring the 1000-step observation window to the exact end of the vehicle's life, we must select a random `start_time` somewhere in the vehicle's life such that the window does not necessarily terminate exactly at EOL.

We need to guarantee that the final observation has `RUL >= 0`. Therefore, the 250-hour window must end at or before `lifetime_hours`.
`start_time` should be uniformly sampled from `[0, lifetime_hours - 250]`.
If `lifetime_hours < 250`, we must force `lifetime_hours` to be > 250, then sample `start_time`.

By sampling a random valid `start_time`, every vehicle will cross the 250-hour observation window with a completely unique remaining useful life.

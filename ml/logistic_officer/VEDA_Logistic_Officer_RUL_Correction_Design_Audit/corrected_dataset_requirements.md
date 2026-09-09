# Corrected Dataset Requirements
- Preserve 40 vehicles (20 Logistics, 20 Officer).
- 1,000 observations per vehicle, 250 observed hours.
- 15-minute sampling interval.
- Split: Train(24), Val(8), Test(8).
- ~40% Normal, ~60% Abnormal.
- EOL threshold = 0.15.
- The RUL_hours target must NOT be generated using a disconnected random multiplier. Sensors must statistically reflect the remaining useful life.

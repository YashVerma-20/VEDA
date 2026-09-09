# Current Generator Analysis
The actual generator script is missing from the workspace, but we inferred the generation logic by reverse-engineering the dataset.
- Exact generator filename: MISSING
- Exact path: MISSING
- Generation parameters: Health_Index slopes from -0.00034 to -0.00019 per 15-min.
- Health_Index generation: Drops perfectly linearly per vehicle.
- Degradation_Index generation: Perfectly negatively correlated to Health_Index (-1.0).
- RUL_hours generation: Drops by exactly 0.25 (15 min) per timestep.
- The critical failure mechanism: `RUL_hours = Health_Index * C_v` where `C_v` is a completely random/arbitrary constant per vehicle.

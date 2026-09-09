# Causal Dependency Graph
```
Vehicle Identity
       |
       v
Vehicle-Specific Multiplier (C_v) --------> RUL_hours (Target)
       |                                       ^
       v                                       |
Health_Index (Latent) --------------------------
       |
       v
Sensor Features (e.g. Brake_Pad_Wear, Fuel_Level)
```
The sensors are strongly dependent on Health_Index, but the target RUL_hours depends on an unobservable vehicle-specific multiplier. This creates a disconnected branch.

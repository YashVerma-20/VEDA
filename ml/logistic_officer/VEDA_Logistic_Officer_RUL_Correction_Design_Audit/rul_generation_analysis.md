# RUL Generation Analysis
RUL decreases linearly by exactly 0.25 hours per 15-minute timestep.
However, the starting RUL (intercept) varies widely across vehicles.
Sensors encode `Health_Index`, but they DO NOT encode the arbitrary multiplier linking `Health_Index` to `RUL_hours`. This perfectly explains why LSTM and XGBoost fail: they can predict the shape of degradation, but not the absolute RUL intercept.

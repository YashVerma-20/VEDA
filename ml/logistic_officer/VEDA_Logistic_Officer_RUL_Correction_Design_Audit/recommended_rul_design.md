# Recommended RUL Design
**Recommendation: A. Latent-health-to-EOL formulation.**
We should generate a true latent degradation curve (with noise/excursions) that hits the EOL threshold at different times based on usage severity. The `RUL_hours` is exactly the time remaining until this threshold is reached. The sensors will be generated as a noisy function of this `Health_Index` + operating conditions. This guarantees that sensors contain enough information to predict the absolute RUL, solving the intercept problem.

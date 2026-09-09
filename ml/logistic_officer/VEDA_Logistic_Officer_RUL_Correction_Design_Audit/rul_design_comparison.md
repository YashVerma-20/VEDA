# RUL Design Comparison
A. **Latent-health-to-EOL formulation**
   - Mechanism: Define a global `Health_Index` threshold for EOL. `RUL` is the time remaining until `Health_Index` hits that global threshold. Sensors are mapped to `Health_Index`.
   - Advantages: Highly learnable, domain-realistic.
   - Disadvantages: Health must be modeled carefully to avoid zero-noise leakage.
B. **Component degradation/failure-time formulation**
   - Mechanism: Model individual component states (e.g., Engine, Brakes). EOL is when any component fails.
   - Advantages: Highly realistic, supports multi-modal failure.
   - Disadvantages: Complex to implement.
C. **Multi-component hazard/failure formulation**
   - Mechanism: Stochastic failure probability based on stress variables.
   - Advantages: Extremely realistic for reliability engineering.
   - Disadvantages: RUL becomes probabilistic rather than deterministic, harder for ML to learn exactly.

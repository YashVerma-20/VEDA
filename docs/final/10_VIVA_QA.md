# 10. VIVA QA

**Q1: Why use Random Forest?**
A: Random Forest acts as a robust, non-linear classification gate to rapidly detect threshold-based anomalies before incurring the computational cost of deep time-series regression.

**Q2: What is the role of Random Forest in VEDA?**
A: It computes an initial severity score. If the score exceeds the vehicle's specific risk threshold (e.g., 0.52 for Tank), the system flags the vehicle as abnormal.

**Q3: Why LSTM?**
A: Long Short-Term Memory networks (combined with 1D-CNN) excel at capturing complex spatial-temporal dependencies across the 30-timestep sequence data.

**Q4: Why XGBoost?**
A: Extreme Gradient Boosting provides highly accurate regression on engineered feature statistics (mean, variance, etc.) and is remarkably resilient to sensor noise.

**Q5: Why hybrid ML?**
A: No single architecture is perfect. Ensembling architectures combines the time-series memory of LSTMs with the robust statistical mapping of XGBoost.

**Q6: Why fusion?**
A: Mathematical fusion smooths out individual model variance, preventing erratic prognostic spikes.

**Q7: Why different fusion rules for Tank vs Logistic/Officer?**
A: The Tank dataset was highly noisy, causing LSTM predictions to degrade; hence, Tank relies 100% on XGBoost. Logistic/Officer telemetry is cleaner, allowing a 0.30 LSTM + 0.70 XGBoost hybrid.

**Q8: What is RUL?**
A: Remaining Useful Life. It estimates the operating hours left before the vehicle reaches a critical failure state.

**Q9: What happens with fewer than 30 timesteps?**
A: The system mathematically halts processing because the sequence models require exactly 30 timesteps. RUL becomes `null`.

**Q10: Why is UNKNOWN safer than zero?**
A: Rendering `0` implies imminent catastrophic failure, causing panic and false logistics routing. `UNKNOWN` accurately reflects a lack of data.

**Q11: How does FastAPI communicate with React?**
A: Via asynchronous, stateless JSON HTTP POST requests to the `/api/v1/inference/` endpoint.

**Q12: Why use Vite?**
A: Vite provides extremely rapid Hot Module Replacement (HMR) during development and highly optimized rollup bundling for production.

**Q13: How are vehicle classes isolated?**
A: The `VedaOrchestrator` explicitly branches logic and fusion mathematics based on the string value of the `vehicle_class` payload parameter.

**Q14: How are models loaded?**
A: The `MLInferenceService` pre-loads the `.keras` and `.pkl` artifacts into memory as singletons during FastAPI startup to avoid per-request latency.

**Q15: How is model state protected?**
A: Models are strictly loaded in inference mode (`predict`) and are computationally isolated. Training functions are entirely decoupled from the runtime server.

**Q16: How was concurrency tested?**
A: Using Pytest and FastAPI's `TestClient` to fire rapid, repeated payloads across differing vehicle classes simultaneously.

**Q17: What are the six agents?**
A: Monitoring, Diagnostics, Prognostics, Maintenance Planning, Spare Parts, and Fleet Readiness.

**Q18: What does the orchestrator do?**
A: It provides a deterministic pipeline that sequences the execution of the six agents, ensuring output from one feeds into the input of the next.

**Q19: What is the difference between inference and orchestration?**
A: Inference is mathematical (predicting numbers). Orchestration is semantic (translating numbers into logistics action).

**Q20: What data is currently used by the demo?**
A: The system leverages dataset-derived JSON fixtures extracted from canonical training sets.

**Q21: Is the system currently receiving live vehicle telemetry?**
A: No. It is an end-to-end simulation of the intelligence pipeline using historical fixtures.

**Q22: What would be required for real-time deployment?**
A: A streaming ingestion layer (Kafka/MQTT), a time-series database (InfluxDB), and WebSocket broadcasting to the frontend.

**Q23: What are the current security limitations?**
A: The application lacks an authentication layer (OAuth) and RBAC controls.

**Q24: What are the current scalability limitations?**
A: Uvicorn runs as a single process; it requires an ASGI multi-worker proxy (Gunicorn) for horizontal scaling.

**Q25: What would be the next development phase?**
A: Phase 10 would likely focus on WebSockets, MQTT integration, authentication, and persistent database storage.

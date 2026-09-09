# Phase 7D: Production Demo UI & Visualization Integration

## UI Architecture Overview
Phase 7D elevates the baseline React frontend shell into a polished, professional military/industrial technical dashboard. 
The dashboard utilizes dark, restrained tactical aesthetics focusing intensely on typography, explicit execution pipelines, and data legibility over unnecessary decorative/game-like UI elements.

## Data Source Disclosure
The application's foundational contract operates upon **Dataset-Derived Demo Fixtures** natively imported from the underlying ML dataset CSV files (e.g. `mockTankTelemetry.json`). 
The UI enforces strict truth-in-demonstration rules:
- Prominent `DATA SOURCE: DATASET-DERIVED DEMO FIXTURE` labels are permanently affixed to the Dashboard headers.
- Explanatory tooltips explicitly declare: *"Current telemetry is derived from the project's canonical datasets for demonstration. Real-time vehicle sensor ingestion is not connected."*
- Misleading terminology like "Live Telemetry" or "Streaming" has been globally eradicated.

## Dashboard Structure

### 1. The 6-Agent Execution Pipeline
The dashboard dynamically visualizes the backend VEDA Orchestrator chain chronologically:
- **[01] MONITORING:** Directly binds to `abnormal_detected` and `severity_score`.
- **[02] DIAGNOSTICS:** Renders `active_fault_codes` in high-contrast threat colors or gracefully falls back to green confirmation blocks.
- **[03] PROGNOSTICS (REMAINING USEFUL LIFE):** Features massive, high-contrast typological hierarchy declaring `fusion_rul_hours`.
- **[04] MAINTENANCE:** Explicitly surfaces the `recommended_action`.
- **[05] SPARE PARTS:** Accurately respects empty states (`NOT_AVAILABLE`) without falsifying inventory quantities.
- **[06] FLEET READINESS AGGREGATION:** Provides the unified fleet status returned by the backend.

### 2. Vehicle Isolation & Validation
The UI strictly isolates structural representations based on class bindings (`TANK`, `LOGISTIC TRUCK`, `OFFICER VEHICLE`).
- **Tank Contract:** Exposes `1.00 x XGBoost` directly next to the RUL result.
- **Logistic/Officer Contract:** Exposes `0.30 x LSTM + 0.70 x XGBoost` directly next to the RUL result.

### 3. The UNKNOWN State Boundary
A primary requirement of the system involves handling insufficient sequential telemetry (length `< 30`).
- By triggering `SIMULATE INSUFFICIENT DATA (<30 TIMESTEPS)`, the frontend truncates the payload.
- The UI explicitly captures the resulting `null` mathematical value and enforces an amber `UNKNOWN` render sequence.
- It supplies the explanation: *"Insufficient sequential telemetry for prognostic inference."*

## Testing & Integrity
The frontend suite leverages React Testing Library bound via Vitest:
- Verifies Landing Page narrative transitions.
- Verifies Fleet Dashboard isolation context mappings.
- Mocks deterministic `UNKNOWN` API response failures natively inside JS memory asserting `[x] passed` logic validation.

## Frozen ML Integrity
The backend AI pipelines, model thresholds, feature scalers, fusion formulas, and FastAPI schemas were **100% frozen** during this visual iteration. Zero alterations were committed to the data science or agentic engineering layers.

## Known Limitations
- The underlying 2.5D X-Ray GSAP animation on the Landing Page still operates using abstract colored DOM elements. The visual execution pipeline narrative has been completed, but production transparency PNG models remain unprovided.

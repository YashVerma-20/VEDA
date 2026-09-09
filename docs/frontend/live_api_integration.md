# Phase 7C: Live API Integration Architecture

## Overview
Phase 7C establishes the critical data bridge between the Vite React frontend shell and the frozen FastAPI Backend. The UI effectively simulates real-world diagnostics by pushing valid telemetry arrays over HTTP and parsing the resulting nested Agent and Machine Learning bounds into the dashboard natively.

## Architecture

### The `api.ts` Client Wrapper
The `/frontend/src/services/api.ts` file acts as the primary data exchange interface.
- It leverages standard browser `fetch` to pass the `InferenceRequest`.
- It defines typed abstractions for `OrchestrationResult`, `TelemetryRecord`, and the inner `AgentResult` trees.
- It dynamically assigns its base path utilizing Vite environmental hooks `import.meta.env.VITE_API_URL`, providing seamless local execution whilst allowing production Docker injection overrides.

### Telemetry Simulation Constraints
Because the frozen Backend ML models structurally enforce strict feature presence to derive `fusion_rul_hours` accurately, generating random Math arrays was impossible.
Instead, we constructed three localized JSON arrays containing exactly 30 real-dataset frames.
- `mockTankTelemetry.json`
- `mockLogisticTelemetry.json`
- `mockOfficerTelemetry.json`
These files are loaded lazily on demand during UI interactions to satisfy the `POST` constraints cleanly.

### Component Re-rendering Logic
`VehicleDashboard.tsx` manages three local React state flags (`loading`, `error`, `result`).
During processing:
- A user can optionally toggle short-data simulation (`truncate = true`), pushing only 15 timesteps.
- The UI handles `null` RUL explicitly rendering "UNKNOWN" dynamically preventing default value false positives ("0 hrs").
- The UI safely traverses agent namespaces using optional chaining (`vRes?.diagnostics?.active_fault_codes?.join(', ') || 'None'`).

### CORS Configuration
Cross-Origin Resource Sharing is temporarily bypassed during development purely through the built-in Vite configuration proxy map. `vite.config.ts` intercepts `/api` namespace calls natively tunneling requests down to `localhost:8000`. This prevents required alterations to the frozen FastAPI main configuration string.

## Testing Integrity
- **UI Tests:** Passed. 5 native `vitest` logic flows confirmed isolated render integrity.
- **Production Build:** Passed. Vite bundled cleanly with zero typescript interface collisions.
- **Backend Tests:** Passed. Pytest regression suite confirmed 0 breakage inside the frozen machine learning components (`7 passed`).

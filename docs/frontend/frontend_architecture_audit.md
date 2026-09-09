# Phase 7A: Frontend Architecture & API Contract Audit

## 1. Frontend Technology Audit
- **Stack**: React 18 (`react`, `react-dom`), GSAP 3.12, TypeScript 5.0.
- **Repository Structure**:
  - `/frontend`: Scaffolded basic directories (`src/components`, `src/pages`, `src/hooks`, `src/styles`, `src/services`, `src/assets`).
  - `/landing_page`: Scaffolded structure (`components`, `animation`, `styles`, `assets` with `logistic`, `officer`, `tank` subdirectories).
- **Current State**: No React components, dashboard UI, or API client files are implemented yet. 

## 2. Landing-Page & Animation Audit
- **Architecture**: A cinematic, scroll-driven technical breakdown (X-ray style).
- **Core Technology**: GSAP ScrollTrigger (synchronizing scroll-progress to explosion layers).
- **Asset Contract**: Explicitly 2D/2.5D layer manipulation (translation, scale, depth simulation). **No `.glb` / 3D models required or expected initially**. The project owner will supply Tank, Logistic Truck, and Officer Vehicle images.

## 3. UI Architecture Blueprint
The future operational UI conceptually branches off the Landing Page:
- `/` (Landing Page)
- `/dashboard` (Fleet Readiness / Aggregation)
- `/vehicle/:vehicleId` (Operational Dashboard)
  - Live Telemetry & Monitoring (RF)
  - Diagnostics (Faults)
  - Prognostics (RUL via Fusion)
  - Maintenance & Spare Parts Status

## 4. API Contract: `POST /api/v1/inference/`
### Request Schema
- `vehicle_id` (string)
- `vehicle_class` (string): Must strictly be `"TANK"`, `"LOGISTIC TRUCK"`, or `"OFFICER VEHICLE"`.
- `telemetry` (List[Dict]): Max 30 timesteps ordered sequentially.

### Response Schema (`OrchestrationResult`)
- `request_id`, `timestamp`, `status`
- `fleet_status`: `FleetReadinessStatus` dict (contains `readiness_status`, counts).
- `vehicle_results`: Nested dict keyed by `vehicle_id` containing the 6 Agent outputs:
  - `monitoring`: `abnormal_detected`, `severity_score`
  - `diagnostics`: `active_fault_codes`, `subsystem_statuses`
  - `prognostics`: `lstm_rul_hours`, `xgb_rul_hours`, `fusion_rul_hours`
  - `maintenance_planning`: `recommended_action`, `priority`
  - `spare_parts`: `parts_needed`, `inventory_status`

## 5. UI Data Mapping & Agent Contracts

### Model/Fusion Visualization
- **RF Monitoring**: Display boolean `abnormal_detected` and continuous `severity_score`.
- **RUL Prognostics**: ONLY display the mathematically explicit `fusion_rul_hours` for decision making. Under the hood:
  - Tank: `Fusion_RUL = XGB_RUL`
  - L/O: `Fusion_RUL = 0.30*LSTM + 0.70*XGB`
- **UNKNOWN Handling**: If `< 30` sequence elements are passed, `fusion_rul_hours` resolves to `None`. The UI must explicitly render `UNKNOWN` or `INDETERMINATE`. It MUST NOT render as `0` or `Healthy`.

### Specific UI Edge Cases
- **Spare Parts**: Defaults to `NOT_AVAILABLE` or `UNKNOWN` (due to missing project-wide inventory mappings). The UI must safely render a placeholder empty state without fabricating dummy quantities or supplier links.
- **Fleet Readiness**: Implements the `demo_v1` ruleset (`READY`, `ATTENTION`, `NOT_READY`, `UNKNOWN`). The UI must not invent alternative readiness percentages outside of what the API calculates (e.g., `<80% READY` implies `ATTENTION`).

### Vehicle Isolation
The UI must leverage conditional rendering bounded to the `vehicle_class` returning from the payload.
- `TANK` routes to Tank-specific feature charts.
- `LOGISTIC TRUCK` & `OFFICER VEHICLE` route to Logistic/Officer UI layouts.
The frontend state must never mix Tank RUL representations over Logistic Truck templates.

## 6. Security, State, & API Recommendations
- **API Client**: Axios or native `fetch`. Should wrap responses logically: `inferVehicle(req) -> Promise<InferenceResponse>`.
- **State Management**: Simple React Context or `zustand` is highly recommended. Redux is unnecessarily heavy for this unidirectional inference visualization flow.
- **Security**: The backend URL MUST be injected via `.env` (e.g. `VITE_API_URL` or `NEXT_PUBLIC_API_URL`). The frontend must NEVER pass arbitrary file-system paths to the backend; all class mapping is resolved safely by the FastAPI service.
- **Error Handling**: API 422s (Missing Telemetry) should trigger a UI form validation alert. API 500s should trigger a secure Fallback UI Component without parsing stack traces.

## 7. Testing Strategy
Future frontend implementation should utilize React Testing Library / Jest to mock API success/failure trajectories (`mockInferenceResponse`), enforcing that component conditional logic correctly isolates `UNKNOWN` values and `NOT_AVAILABLE` inventory outputs. GSAP scroll layers should be E2E verified via Playwright per `animation.md`.

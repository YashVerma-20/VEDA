# VEDA DEMONSTRATION RUNBOOK

This runbook provides the exact steps required to execute the final End-to-End VEDA Vehicle Intelligence System demonstration.

## Prerequisites
- Node.js 18+ installed
- Python 3.10+ installed
- `pip install -r requirements.txt` (or appropriate dependencies) installed in your Python environment
- `npm install` executed inside the `frontend/` directory

## Step 1: Start the Backend (ML Inference Service)
Open a terminal and navigate to the project root (`VEDA/`).
Execute the FastAPI backend server:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
Verify the backend is running by checking the health endpoint:
- Navigate to `http://localhost:8000/health`
- Expected response: `{"status": "healthy"}`

## Step 2: Start the Frontend (Command Center UI)
Open a separate terminal and navigate to the `frontend/` directory.
Execute the Vite development server:
```bash
npm run dev
```
Alternatively, for a production demonstration, serve the built assets:
```bash
npm run build
npm run preview
```
The application will be accessible at `http://localhost:5173`.

## Step 3: Execute the Demonstration Sequence
1. **Landing Page (`/`):** 
   - Scroll through the narrative sequence outlining the intelligence pipeline (Vehicle -> Telemetry -> AI Analysis -> Prognostics -> Agents).
   - Acknowledge the clear dataset disclosure.
   - Click **ENTER FLEET DASHBOARD**.

2. **Fleet Command (`/dashboard`):**
   - Note the isolated vehicle classes (Tank, Logistic Truck, Officer Vehicle).
   - Observe the explicit fusion contracts defined for each class.
   - Click **OPEN VEHICLE** on `TANK UNIT #2`.

3. **Tank Demonstration (`/vehicle/2?class=TANK`):**
   - Click **RUN DEMO INFERENCE (30 TIMESTEP DATASET SAMPLE)**.
   - Observe the pipeline execution:
     - RF Monitoring (Abnormal Detected: YES, Severity Score evaluated).
     - RUL Calculation (Fusion: 1.00 x XGBoost).
     - 6-Agent Execution (Monitoring -> Diagnostics -> Prognostics -> Maintenance -> Spare Parts -> Readiness).
     - Fleet Readiness aggregated totals update.

4. **Insufficient Data Demonstration (UNKNOWN State):**
   - Click **SIMULATE INSUFFICIENT DATA (<30 TIMESTEPS)**.
   - Observe the system gracefully halting RUL calculations.
   - Verify the `UNKNOWN` state triggers with the warning: `INSUFFICIENT DATA: 30 TIMESTEPS REQUIRED`.

5. **Logistic/Officer Isolation Demonstration:**
   - Return to Fleet Command.
   - Open `LOGISTIC TRUCK LOV_001`.
   - Run Demo Inference.
   - Observe the isolated Fusion contract (`0.30 x LSTM + 0.70 x XGBoost`).
   - Confirm Tank artifacts did not bleed into the Logistic domain.

## Shutdown
Terminate the Vite server (`Ctrl+C` in the frontend terminal).
Terminate the Uvicorn server (`Ctrl+C` in the backend terminal).

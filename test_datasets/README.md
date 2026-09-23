# VEDA Test Datasets

Ready-to-upload demonstration datasets for the VEDA Command Center.
Each file contains **50 timesteps** (exceeds the 30-timestep minimum required by the prognostics models).

---

## Tank Datasets (`/tank/`)

| File | Vehicle ID | Health State | Expected Outcome |
|------|-----------|-------------|-----------------|
| `tank_T-001_healthy.csv` | T-001 | Healthy | Low risk, READY |
| `tank_T-002_healthy.json` | T-002 | Healthy | Low risk, READY |
| `tank_T-003_degraded.csv` | T-003 | Degraded | High vibration, elevated temps, NOT READY |
| `tank_T-004_degraded.json` | T-004 | Degraded | High RPM, brake wear, NOT READY |
| `tank_T-005_healthy.csv` | T-005 | Healthy | Low risk, READY |

---

## Logistic / Officer Datasets (`/logistic_officer/`)

| File | Vehicle ID | Health State | Expected Outcome |
|------|-----------|-------------|-----------------|
| `lo_LOV_001_healthy.csv` | LOV_001 | Healthy | Low risk, READY |
| `lo_LOV_002_degraded.json` | LOV_002 | Degraded | High oil temp, worn brakes, NOT READY |
| `lo_LOV_003_healthy.csv` | LOV_003 | Healthy | Low risk, READY |
| `lo_LOV_021_degraded.csv` | LOV_021 | Degraded | Overheating, high vibration, NOT READY |
| `lo_LOV_022_healthy.json` | LOV_022 | Healthy | Low risk, READY |

---

## Mixed Datasets (`/mixed/`)

These datasets contain 100 timesteps total: the first 50 timesteps represent healthy operations, while the latter 50 timesteps represent degraded operations. These are perfect for demonstrating how the ML models detect state changes.

| File | Vehicle ID | Format | Description |
|------|-----------|--------|-------------|
| `tank_T-010_mixed.json` | T-010 | JSON | Tank: Healthy → Degraded |
| `tank_T-011_mixed.csv` | T-011 | CSV | Tank: Healthy → Degraded |
| `lo_LOV_010_mixed.json` | LOV_010 | JSON | Logistic/Officer: Healthy → Degraded |
| `lo_LOV_011_mixed.csv` | LOV_011 | CSV | Logistic/Officer: Healthy → Degraded |

---

## How to Use

1. Start the backend: `uvicorn main:app --reload --port 8000` (from `backend/app/`)
2. Log in to the VEDA dashboard
3. Navigate to a vehicle (e.g. Tank → vehicle `#2`)
4. Upload one of the `.json` or `.csv` files above using the **DATASET INPUT** uploader
5. The pipeline will run and results + inference history will populate

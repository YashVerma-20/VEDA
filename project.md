# VEDA — Vehicle Evaluation & Diagnostics Agent

## Project Definition
VEDA (Vehicle Evaluation & Diagnostics Agent) is an agentic-AI predictive-maintenance and diagnostics platform for military ground vehicles.

**Goal:** Maximize vehicle availability, minimize unexpected downtime, improve maintenance decisions, and support mission readiness.

## 1. HIGH-LEVEL WORKFLOW
Vehicle Data → Data Ingestion → Data Preprocessing → Random Forest abnormal detection/classification/routing → Vehicle-specific ML pipeline → LSTM + 1D-CNN + XGBoost → Prediction/Fusion → Agentic AI → Backend → Database → Frontend.

## 2. TWO MODEL FAMILIES
VEDA has two separate ML model families:
1. Tank
2. Logistic/Officer

Never mix their datasets, model weights, scalers, targets, metadata, or evaluation artifacts without explicit approval.

## 3. TANK PIPELINE
### Random Forest
**Status: TRAINED / FROZEN**

Role:
- abnormal-pattern detection
- classification
- routing

RF is NOT the final RUL predictor.

### LSTM + 1D-CNN
**Status: TRAINED / FROZEN**

Canonical input: `30 time steps × 45 features`

Architecture:
Input (30,45) → Conv1D 64 → BatchNorm → Dropout → Conv1D 64 → BatchNorm → Dropout → LSTM 64 → LSTM 32 → Dense 64 → Dropout → Dense 32 → RUL output.

Total parameters: **71,233**.

Architecture and interface must remain unchanged for the frozen tank model.

### XGBoost
**Status: PENDING**

Tank XGBoost still needs to be trained.

## 4. LOGISTIC / OFFICER PIPELINE
A separate dataset will be supplied.

Train specifically for this dataset:
1. Random Forest
2. LSTM + 1D-CNN
3. XGBoost

Never reuse tank weights for logistic/officer vehicles.

## 5. TRAINING RULES
- Maintain train/validation/test separation.
- Prevent vehicle-level leakage.
- Fit scalers on training data only.
- Do not use test data for model selection.
- Save reproducible configurations and artifacts.
- Verify model reload and prediction consistency.

## 6. MODEL ARTIFACTS
Every trained model must have an inference package containing the appropriate:
- model file
- preprocessing/scaler
- configuration
- feature ordering
- metrics
- predictions where useful
- metadata
- reload verification

## 7. FUSION
Fusion combines validated downstream outputs such as LSTM + 1D-CNN RUL and XGBoost RUL. Do not invent a fusion formula without justification and validation.

## 8. AGENTIC AI
Six agents:
- Monitoring
- Diagnostics
- Prognostics
- Maintenance Planning
- Spare Parts
- Fleet Readiness

Agents interpret validated system information and must not fabricate vehicle state, predictions, inventory, or sensor values.

## 9. BACKEND / DATABASE / FRONTEND
Backend: FastAPI + Python.
Database: PostgreSQL, with TimescaleDB where appropriate; SQLAlchemy; Alembic.
Frontend: React.js / TypeScript.

## 10. LANDING PAGE
Three vehicle images will be supplied:
- Tank
- Military logistic truck
- Officer vehicle

The initial animation must be image-based and must NOT require `.glb` assets.

Intended experience:
- technical/X-ray vehicle appearance
- vehicle selection changes on refresh/new landing session
- scrolling progressively explodes the vehicle
- full exploded technical presentation
- scrolling backward reverses it
- same reusable system for all three vehicles

See `animation.md`.

## 11. DEVELOPMENT CONTROL
Authoritative documents:
- project.md
- rules.md
- development_log.md
- agent_knowledge_base.md
- database.md
- tools_and_tech.md
- animation.md

If documents conflict: STOP, identify the conflict, and ask for approval.

Every meaningful change must be recorded in `development_log.md`.

## 12. DEVELOPMENT ORDER
1. Audit specifications
2. Establish project structure
3. Verify supplied ML artifacts
4. Train missing models
5. Build inference pipeline
6. Build fusion
7. Build agentic layer
8. Build database/backend
9. Build frontend
10. Build landing animation
11. Integrate
12. Test
13. Document

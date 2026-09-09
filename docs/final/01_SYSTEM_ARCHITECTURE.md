# 01. SYSTEM ARCHITECTURE

## Overview
VEDA (Vehicle Equipment Diagnostics & Analytics) is an end-to-end military vehicle intelligence system designed to process telemetry, predict Remaining Useful Life (RUL), and orchestrate maintenance actions via a multi-agent system.

## High-Level Architecture
1. **Frontend (Client Layer)**: Built with React, TypeScript, and Vite. Serves as the Command Center interface for operators. It visualizes data strictly via backend API consumption without executing local intelligence logic.
2. **Backend (API Layer)**: Built with FastAPI. Provides a highly concurrent HTTP API (`/api/v1/inference/`) for telemetry ingestion and orchestrates the backend intelligence flow.
3. **ML Inference Layer (`MLInferenceService`)**: Wraps and executes pre-trained `.pkl` (Random Forest, XGBoost) and `.keras` (LSTM, 1D-CNN) models. It classifies the risk and predicts RUL based on deterministic mathematical fusion formulas.
4. **Agent Orchestration Layer (`VedaOrchestrator`)**: A deterministic pipeline of 6 discrete agents (Monitoring, Diagnostics, Prognostics, Maintenance Planning, Spare Parts, Fleet Readiness) that translates raw ML outputs into actionable military logistics commands.

## Constraints & Security
- **Data Source**: Currently uses dataset-derived demonstration fixtures.
- **Stateless Execution**: The backend is functionally stateless, scaling horizontally per request.
- **Vehicle Isolation**: Tank algorithms (`1.00 x XGBoost`) are strictly isolated from Logistic/Officer algorithms (`0.30 x LSTM + 0.70 x XGBoost`).

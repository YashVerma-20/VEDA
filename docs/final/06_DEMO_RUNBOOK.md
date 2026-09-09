# 06. DEMO RUNBOOK

**Target Duration**: ~7 Minutes

## 00:00 - 00:30 | Landing Page Narrative
1. Start at `/`. Explain the VEDA objective (Predictive intelligence for mission-critical vehicles).
2. Scroll through the GSAP pipeline to introduce the architecture.

## 00:30 - 01:00 | Fleet Command
1. Proceed to `/dashboard`.
2. Highlight the 3 demonstration units.
3. Point out the distinct inference pipelines (`1.00 x XGBoost` vs hybrid).
4. Point out the Dataset Fixture disclosure.

## 01:00 - 02:00 | Tank Inference
1. Open `TANK UNIT #2`.
2. Click **RUN DEMO INFERENCE**.
3. Walk through the results chronologically: RF Monitoring → XGBoost Fusion → 6 Agent Orchestration.

## 02:00 - 03:00 | Logistic Truck Inference
1. Return to Fleet Command, open `LOGISTIC TRUCK LOV_001`.
2. Click **RUN DEMO INFERENCE**.
3. Highlight the differing `0.30 x LSTM + 0.70 x XGBoost` pipeline.

## 03:00 - 04:00 | Officer Vehicle Inference
1. Open `OFFICER VEHICLE LOV_021`.
2. Verify pipeline execution matches Logistic architecture.

## 04:00 - 05:00 | UNKNOWN Demonstration
1. On any vehicle, click **SIMULATE INSUFFICIENT DATA**.
2. Explain that sending `<30` timesteps mathematically triggers the `UNKNOWN` state.
3. Highlight the UI warning: `INSUFFICIENT DATA: 30 TIMESTEPS REQUIRED`.

## 05:00 - 07:00 | Technical Q&A
1. Conclude the demonstration.
2. Field questions regarding Model Architecture, React Frontend, and Agentic AI flows.

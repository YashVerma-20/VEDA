# VEDA — AGENT KNOWLEDGE BASE

## 1. PURPOSE
The agentic layer converts validated ML outputs and vehicle information into actionable maintenance intelligence. Agents must support humans and must not fabricate information.

## 2. SIX AGENTS
1. Monitoring Agent
2. Diagnostics Agent
3. Prognostics Agent
4. Maintenance Planning Agent
5. Spare Parts Agent
6. Fleet Readiness Agent

## 3. MONITORING AGENT
Purpose: Monitor vehicle health.

Inputs may include sensor readings, vehicle status, RF abnormal classification, health indicators and alerts.

Responsibilities:
- monitor vehicle state
- detect abnormal behavior
- compute health indicators
- trigger alerts
- forward important events

Must not invent sensor readings or failures.

## 4. DIAGNOSTICS AGENT
Purpose: Determine probable causes of abnormal behavior.

Inputs:
- sensor patterns
- fault codes
- vehicle health
- RF classification
- model outputs
- historical information

Outputs should contain:
- problem
- evidence
- probable cause
- confidence
- next diagnostic action

## 5. PROGNOSTICS AGENT
Purpose: Interpret predictive-maintenance results.

Inputs:
- LSTM + 1D-CNN RUL
- XGBoost RUL
- fused RUL
- degradation history
- health indicators

Responsibilities:
- interpret RUL
- analyze degradation
- estimate risk
- identify trends
- support what-if analysis where available

It does not replace ML models.

## 6. MAINTENANCE PLANNING AGENT
Purpose: Translate diagnostics/prognostics into maintenance actions.

Responsibilities:
- recommend maintenance
- prioritize tasks
- recommend scheduling
- explain recommendations

Recommendations must be traceable to evidence.

## 7. SPARE PARTS AGENT
Purpose: Support spare-parts planning.

Responsibilities:
- forecast demand
- check inventory
- detect shortages
- support procurement recommendations

Never invent inventory.

## 8. FLEET READINESS AGENT
Purpose: Provide fleet-level readiness information.

Responsibilities:
- calculate readiness indicators
- summarize fleet condition
- identify high-risk vehicles
- support mission-readiness assessment

## 9. AGENT COMMUNICATION
Possible mechanisms:
- message passing
- shared state / blackboard
- event-driven triggers

Implementation must be controlled and observable.

## 10. AGENT EVENT
Conceptual fields:
event_id, timestamp, vehicle_id, vehicle_type, source_agent, event_type, severity, payload, confidence, status.

## 11. AGENT MEMORY
May contain:
- recent observations
- previous diagnostics
- maintenance recommendations
- historical events
- previous predictions

Store only relevant information.

## 12. REASONING PATTERN
Observation → Evidence → Interpretation → Recommendation → Confidence → Action/Human Review.

## 13. CONFIDENCE
Distinguish facts, model predictions, inferences, and unknowns. Never present uncertain predictions as facts.

## 14. HUMAN OVERSIGHT
Maintenance recommendations should remain reviewable by authorized users.

## 15. FAILURE HANDLING
If an ML model is unavailable:
Prediction unavailable → explain missing dependency → use available evidence → recommend next step.

Never fabricate.

## 16. VEHICLE MODEL FAMILY
Every prediction should identify its family:
- TANK
- LOGISTIC
- OFFICER

## 17. MODEL ROLE KNOWLEDGE
Random Forest: abnormal detection, classification, routing.

LSTM + 1D-CNN: temporal sequence modeling, RUL prediction.

XGBoost: nonlinear/tabular modeling, RUL prediction/refinement, feature importance.

Fusion: combines downstream model outputs.

Agents: interpret, diagnose, recommend, coordinate.

## 18. SAFETY
Agents support diagnostics, predictive maintenance, logistics, and fleet readiness only. Do not use them for weapon targeting/control or offensive action planning.

## 19. TRACEABILITY
Agent outputs should be traceable to input observations, ML outputs, database records, reasoning, and recommendation logic.

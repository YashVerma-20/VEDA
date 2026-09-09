# VEDA — ANTIGRAVITY DEVELOPMENT RULES

## 1. DO NOT CHANGE ARCHITECTURE AUTONOMOUSLY
Never replace models, change model roles, alter the core data flow, replace frameworks, or introduce major technologies without approval.

## 2. READ DOCUMENTATION FIRST
Before major work, read all seven project documents. If they conflict, STOP and report the conflict.

## 3. DO NOT INVENT INFORMATION
Never invent dataset columns, feature names, vehicle IDs, thresholds, model outputs, database fields, API contracts, training results, or assets. Inspect actual supplied files first.

## 4. FROZEN TANK MODELS
Tank RF and tank LSTM + 1D-CNN are frozen unless explicitly approved. Do not retrain or change their interface, preprocessing, scaler, or architecture.

## 5. RANDOM FOREST ROLE
RF is the initial abnormal detector/classifier/router. It is NOT the final RUL predictor.

## 6. TWO MODEL FAMILIES
Keep Tank and Logistic/Officer datasets, models, scalers, targets, metadata and evaluation results separate.

## 7. LOGISTIC/OFFICER TRAINING
When its dataset is supplied:
1. inspect schema
2. identify vehicles/features/target
3. check quality and leakage
4. establish splits
5. determine preprocessing
6. train RF
7. train LSTM + 1D-CNN
8. train XGBoost
9. evaluate
10. save complete artifacts
11. reload-test
12. document

Do not train blindly.

## 8. TEST DATA
Never use test data for model selection, hyperparameter selection, threshold selection, or architecture selection.

## 9. PREPROCESSING
Fit scalers on training data only and save them for inference.

## 10. MODEL COMPLETENESS
A model is incomplete until its required inference artifacts, configuration, feature order, metrics and verification information are saved.

## 11. RELOAD VERIFICATION
Every production model must be loaded again and tested for prediction consistency.

## 12. HYPERPARAMETER SEARCH
Use controlled experiments. Record candidate, parameters, validation result, reason, and decision.

## 13. DEVELOPMENT LOG
Every meaningful change must record what changed, why, previous behavior, new behavior, files changed, expected benefit, validation, result, and decision.

## 14. DEPENDENCIES
Do not add dependencies without checking necessity and compatibility. Record significant decisions.

## 15. MCP
Available MCPs:
- Playwright
- Sequential Thinking

Use Playwright for browser verification and Sequential Thinking for complex planning/reasoning when useful.

## 16. ANIMATION
Initial vehicle assets are 2D images. Do not make `.glb` mandatory. Do not introduce Three.js/React Three Fiber/Blender unless explicitly approved.

Preferred animation:
- React
- GSAP
- ScrollTrigger
- CSS transforms
- layered image assets
- 2D/2.5D techniques

## 17. NO UNNECESSARY REFACTORING
Do not rewrite working code without a justified requirement.

## 18. BACKEND
Production API endpoints load trained artifacts. They do not train models during normal inference requests.

## 19. DATABASE
Do not add fields without documenting their purpose. Use migrations for schema changes.

## 20. AGENTS
Agents consume validated information. They must never fabricate RUL, health, failures, inventory, sensor values, or probabilities.

## 21. SAFETY
VEDA is for diagnostics, predictive maintenance, logistics/support, and fleet readiness. Do not expand it into weapon targeting, weapon control, or offensive decision-making.

## 22. BEFORE MAJOR IMPLEMENTATION
Read relevant documentation → inspect existing files → identify interfaces → identify risks → plan → implement → test → update development_log.md.

## 23. BEFORE DECLARING COMPLETE
The component must work, be tested, have verified interfaces, required artifacts, documentation, and a development-log entry.

## 24. WHEN UNCERTAIN
STOP AND ASK. Do not guess.

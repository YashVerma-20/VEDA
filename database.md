# VEDA — DATABASE SPECIFICATION

## 1. PURPOSE
Store operational, predictive-maintenance and agent-related information.

Target:
- PostgreSQL
- TimescaleDB where appropriate
- SQLAlchemy
- Alembic

## 2. PRINCIPLES
Database must preserve integrity, support time-series data, vehicle-level queries, model predictions, agent events, maintenance, fleet analysis, and auditability.

## 3. VEHICLES
Conceptual entity: `vehicles`

Possible fields:
- vehicle_id
- vehicle_type
- model_family
- status
- commission_date
- created_at
- updated_at

Vehicle types may include: TANK, LOGISTIC, OFFICER.

## 4. SENSOR DATA
Conceptual: `sensor_readings`

Possible fields:
- reading_id
- vehicle_id
- timestamp
- sensor_name
- sensor_value
- unit
- quality_flag

High-volume time-series data may use TimescaleDB.

## 5. VEHICLE HEALTH
Conceptual: `vehicle_health`

Possible:
- vehicle_id
- timestamp
- health_score
- health_status
- abnormal_probability
- abnormal_class

## 6. MODEL PREDICTIONS
Conceptual: `model_predictions`

Possible:
- prediction_id
- vehicle_id
- vehicle_type
- model_family
- model_name
- model_version
- prediction_timestamp
- predicted_rul
- confidence

## 7. MODEL OUTPUTS
Keep individual outputs distinct:
- RF output
- LSTM + 1D-CNN output
- XGBoost output
- Fusion output

Do not overwrite individual model outputs with fused results.

## 8. FUSION RESULTS
Conceptual: `fusion_predictions`

Possible:
- fusion_id
- vehicle_id
- timestamp
- lstm_rul
- xgb_rul
- fused_rul
- confidence
- fusion_method

## 9. FAULTS
Conceptual: `faults`

Possible:
- fault_id
- vehicle_id
- timestamp
- fault_code
- severity
- description
- status

## 10. MAINTENANCE
Conceptual: `maintenance_records`

Possible:
- maintenance_id
- vehicle_id
- component
- maintenance_type
- start_time
- end_time
- description
- technician
- status

## 11. MAINTENANCE RECOMMENDATIONS
Conceptual: `maintenance_recommendations`

Possible:
- recommendation_id
- vehicle_id
- timestamp
- priority
- recommended_action
- reason
- confidence
- status

## 12. SPARE PARTS
Conceptual entities:
- spare_parts
- inventory
- spare_part_demand

Never invent inventory quantities.

## 13. ALERTS
Conceptual: `alerts`

Possible:
- alert_id
- vehicle_id
- timestamp
- severity
- alert_type
- message
- status
- acknowledged_at

## 14. AGENT EVENTS
Conceptual: `agent_events`

Possible:
- event_id
- timestamp
- vehicle_id
- agent_name
- event_type
- severity
- payload
- confidence
- status

## 15. FLEET
Possible entities:
- fleet
- fleet_vehicles
- fleet_readiness

## 16. MODEL REGISTRY
Conceptual: `model_registry`

Possible:
- model_id
- model_name
- vehicle_type
- model_version
- artifact_location
- feature_schema
- training_date
- validation_metrics
- status

## 17. AUDIT LOG
Conceptual: `audit_log`

Possible:
- timestamp
- actor
- action
- entity
- entity_id
- details

## 18. TIME-SERIES
TimescaleDB may be used for sensor readings, health observations, prediction history and time-based events where useful.

## 19. SECURITY
Credentials must not be hardcoded. Use environment variables such as DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB.

Never commit real credentials.

## 20. MIGRATIONS
Use Alembic for schema changes.

## 21. DATABASE RULE
Database stores system state and history. Avoid putting arbitrary business logic into the database.

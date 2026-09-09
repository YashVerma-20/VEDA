# 04. API DOCUMENTATION

## `POST /api/v1/inference/`

### Request Payload
```json
{
  "vehicle_id": "string",
  "vehicle_class": "TANK | LOGISTIC TRUCK | OFFICER VEHICLE",
  "telemetry": [
    {
      "engine_rpm": 0.0,
      "coolant_temp": 0.0,
      "...": "..."
    }
  ]
}
```

### Response Schema (`OrchestrationResult`)
```json
{
  "request_id": "uuid",
  "timestamp": "iso8601",
  "status": "SUCCESS | ERROR",
  "fleet_status": {
    "readiness_status": "READY | ATTENTION | NOT_READY | UNKNOWN",
    "ready_count": 0,
    "attention_count": 0,
    "not_ready_count": 0,
    "unknown_count": 0,
    "ready_percentage": 0.0
  },
  "vehicle_results": {
    "vehicle_id": {
      "monitoring": { "abnormal_detected": false, "severity_score": 0.0 },
      "diagnostics": { "active_fault_codes": [] },
      "prognostics": { "fusion_rul_hours": 120.5, "xgb_rul_hours": 120.5, "lstm_rul_hours": null },
      "maintenance_planning": { "recommended_action": "None", "priority": "LOW" },
      "spare_parts": { "inventory_status": "AVAILABLE" }
    }
  }
}
```

### Error Handling
If an error occurs internally, FastAPI returns a 500 status code with a sanitized `detail` message protecting Python tracebacks.

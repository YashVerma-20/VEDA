# VEDA Phase 10 Database Architecture

## Overview
The VEDA Database layer provides historical tracking and audit logging for all inference runs, telemetry payloads, agent orchestration results, and fleet readiness outcomes. It is built strictly as a **persistence layer**. The ML models, feature engineering pipelines, and orchestration rules are completely isolated from this database to remain fully stateless during inference calculation.

## Architecture
- **Engine**: PostgreSQL (accessed via SQLAlchemy in synchronous mode).
- **Migrations**: Managed by Alembic.
- **Service Layer**: `PersistenceService` captures the `OrchestrationResult` strictly after the `VedaOrchestrator` completes execution.

## Flow
1. API receives inference payload.
2. FastAPI validates request.
3. `MLInferenceService` evaluates telemetry against models (stateless).
4. `VedaOrchestrator` generates agent decisions (stateless).
5. `PersistenceService` stores the inputs and outputs (transactional).
6. Result is returned to the user.

## Critical Constraint: ML Integrity
The persistence layer **never** calculates RUL, never applies fusion formulas, and never dictates the agent responses. It acts solely as an audit log.

## Transaction Safety
All persistence operations for a single inference are wrapped in a single database transaction. A failure to persist rolls back the database state and returns a `500 Internal Server Error`, ensuring no partial records or false successes are exposed.

# VEDA Fleet Readiness Policy (DUMMY / DEMONSTRATION)

## 1. Purpose
This document defines the Fleet Readiness Policy and Fleet Aggregation Policy for the VEDA prototype.

## 2. Disclaimer
**This policy is a project-level demonstration policy developed for the VEDA prototype because an approved organization-specific fleet readiness policy was not available during development. The thresholds and rules are configurable and must not be interpreted as official military, defence, BISAG-N, or operational readiness standards.**

## 3. Vehicle Readiness States
Vehicles are classified into four deterministic states:
1. **READY**
2. **ATTENTION**
3. **NOT_READY**
4. **UNKNOWN**

### 3.1 RUL Thresholds
- **> 300 hours**: READY candidate
- **100 - 300 hours**: ATTENTION candidate
- **< 100 hours**: NOT_READY

### 3.2 Diagnostic Rules
- **CRITICAL**: NOT_READY
- **NON_CRITICAL / WARNING**: ATTENTION
- **NORMAL**: No block
- **UNKNOWN**: Propagated as UNKNOWN

### 3.3 Maintenance Rules
- **IMMEDIATE / URGENT**: NOT_READY
- **PLANNED / RECOMMENDED**: ATTENTION
- **NO_ACTION**: No block

### 3.4 Precedence Rules
Precedence is applied as follows:
`NOT_READY` > `UNKNOWN` (when missing required info) > `ATTENTION` > `READY`

## 4. Fleet Aggregation Rules
Fleet readiness aggregates vehicle states deterministically. UNKNOWN vehicles remain explicitly visible and impact the overall score.

### 4.1 Fleet Thresholds
- **NOT_READY**: If NOT_READY >= 30% OR count >= 3
- **ATTENTION**: If READY < 80% OR ATTENTION >= 20% OR UNKNOWN >= 10%
- **READY**: If READY >= 80% AND NOT_READY < 30% AND UNKNOWN < 10%
- **UNKNOWN**: Empty fleet or no valid vehicle inputs.

## 5. Configuration & Tank/Logistic-Officer Isolation
- Configuration is located in `backend/app/agents/fleet_readiness/config.py`.
- The policy version is reported as `demo_v1`.
- Tank and Logistic/Officer fleets must be aggregated independently. Mixing namespaces is forbidden.

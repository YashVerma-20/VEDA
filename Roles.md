# VEDA — Role-Based Access Control (RBAC)

## 1. Purpose

VEDA (Vehicle Evaluation and Diagnostic Agent) uses role-based access control to control which users can enter the system and which operational functions they can access.

The frontend must visually enforce the distinction between:

- **ADMIN**
- **MAINTAINER**

Authentication is currently a frontend/mock authentication layer unless and until backend authentication is implemented. Do not represent mock authentication as production-grade identity verification.

---

## 2. User Roles

| Role | Purpose | Access Level |
|---|---|---|
| **Admin** | Complete system supervision, vehicle monitoring, diagnostics, dataset/inference operations and administrative controls | Full access |
| **Maintainer** | Operational vehicle evaluation and maintenance-oriented diagnostics | Restricted operational access |

---

## 3. Admin

### Working

The Admin has complete access to the VEDA command center and can work with both supported vehicle categories:

1. Tank
2. Logistic / Officer Vehicle

### Functions

- Access the complete VEDA system.
- Select either vehicle category.
- Upload the appropriate vehicle dataset.
- Start the dataset evaluation/inference workflow.
- View preprocessing status.
- View Random Forest classification results.
- View XGBoost results.
- View LSTM + 1D CNN results.
- View the fusion result.
- View final RUL prediction.
- View diagnostics and agent outputs.
- View inference history.
- View vehicle-level information.
- View fleet-level information.
- Access administrative/system views.
- Review system status and errors.
- Access both Tank and Logistic/Officer workflows.

### Admin UI

The UI should clearly display an **ADMIN** role badge.

Admin navigation may include:

```text
Dashboard
Vehicles
Fleet
History
Agents / Diagnostics
Administration
Profile
```

---

## 4. Maintainer

### Working

The Maintainer is an operational user focused on evaluating vehicles and interpreting their condition.

The Maintainer can enter the vehicle workflow but does not receive administrative privileges.

### Functions

- Access the vehicle selection page.
- Select:
  - Tank
  - Logistic / Officer Vehicle
- Upload permitted vehicle datasets.
- Start the evaluation/inference workflow.
- Monitor preprocessing.
- View classification results.
- View XGBoost output.
- View LSTM + 1D CNN output.
- View fused prediction.
- View final RUL.
- View diagnostics relevant to the selected vehicle.
- View permitted inference/history information.
- Review vehicle health and readiness information.

### Maintainer Restrictions

A Maintainer must not receive access to:

- User administration.
- Role management.
- System administration.
- Administrative configuration.
- Other restricted admin-only controls.

The UI should hide unauthorized navigation items rather than displaying them as usable controls.

---

## 5. Authentication Flow

```text
Landing Page
     |
     | ENTER VEDA
     v
Login / Signup
     |
     v
Authentication
     |
     +------------------+
     |                  |
   ADMIN            MAINTAINER
     |                  |
     +--------+---------+
              |
              v
      Vehicle Selection
              |
       +------+------+
       |             |
      TANK      LOGISTIC /
                OFFICER
       |             |
       +------+------+
              |
              v
       Command Center
```

---

## 6. Vehicle Access

### Tank

The Tank workflow is available to both Admin and Maintainer.

The UI should present the Tank as a selectable vehicle category and then open the Tank-specific command center.

### Logistic / Officer Vehicle

The Logistic / Officer Vehicle workflow is available to both Admin and Maintainer.

The UI should present this as a single selectable category:

**LOGISTIC / OFFICER VEHICLE**

---

## 7. Command Center Access

After selecting a vehicle category, the user enters the corresponding VEDA Command Center.

The command center should present the evaluation workflow without changing the underlying ML implementation.

```text
Dataset Upload
      |
      v
Preprocessing
      |
      v
Random Forest
Classification
      |
      +----------------------+
      |                      |
      v                      v
   XGBoost              LSTM + 1D CNN
      |                      |
      +----------+-----------+
                 |
                 v
               Fusion
                 |
                 v
             Final RUL
                 |
                 v
        Diagnostics / History
```

The frontend must visualize this existing project workflow; it must not invent a different ML pipeline.

---

## 8. Authorization Rules

Use a centralized role definition.

Example conceptual model:

```text
ADMIN
  canAccessAll = true

MAINTAINER
  canAccessVehicleEvaluation = true
  canAccessAdmin = false
```

Do not scatter role checks throughout unrelated components.

Use a reusable authorization/route-guard mechanism.

---

## 9. Important Constraints

- Do not implement real credential storage in the frontend.
- Do not expose passwords or secrets in source code.
- Do not claim frontend mock authentication is secure production authentication.
- Do not modify frozen ML models or model artifacts.
- Do not change preprocessing, classification, fusion, thresholds or RUL logic merely to support RBAC.
- RBAC controls presentation and access to frontend functionality only until backend authentication/authorization exists.

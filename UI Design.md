# VEDA — UI Design Specification

## 1. Design Objective
The Landing Page must feel like the entrance to a sophisticated defense engineering / vehicle intelligence system.

**Design direction:** DEFENSE-TECH MINIMALISM + SELECTIVE GLASSMORPHISM + CINEMATIC VEHICLE PRESENTATION

It must NOT look like Generic SaaS, Generic AI landing page, Cryptocurrency dashboard, Gaming interface, Marketing-heavy startup website, or an overly futuristic neon interface.

## 2. Core User Journey
The exact navigation flow is:
LANDING PAGE → ENTER VEDA → LOGIN / SIGNUP → ROLE AUTHENTICATION → VEHICLE SELECTION → TANK OR LOGISTIC / OFFICER → COMMAND CENTER → DATASET UPLOAD → PREPROCESSING → RANDOM FOREST CLASSIFICATION → XGBOOST + LSTM + 1D CNN → FUSION → FINAL RUL → DIAGNOSTICS / HISTORY

The landing page must NOT directly open the Command Center.

## 3. Landing Page Composition & Technical Environment
The vehicle visualization should be the dominant visual element. The artwork should visually integrate into the page.

**Recommended Composition:**
- **LEFT / UPPER AREA:** VEDA Logo, "Vehicle Evaluation and Diagnostic Agent", Mission statement, Supporting text, "ENTER VEDA" CTA.
- **RIGHT / CENTER:** LARGE CINEMATIC VEHICLE VISUALIZATION.

The background may include subtle engineering visualization elements (e.g., fine technical grid, coordinate markers, sensor indicators, measurement lines, scanning line, small HUD labels, engineering metadata, restrained radial illumination). These must remain secondary, as the vehicle remains the focal point.

**Avoid:** Large black rectangular image boxes, generic image cards, obvious image borders/containers, generic dashboard widgets, or heavy UI surrounding the vehicle. The vehicle should NOT be trapped inside an ordinary rectangular card.

## 4. Source Asset Rule & Compositing
**DO NOT GENERATE VEHICLE ARTWORK.** 

The user will provide the actual vehicle images (Normal Image + X-ray/Exploded Image) for the Tank and Logistic/Officer vehicles. 

The supplied vehicle artwork is authoritative **source material**. The frontend may transform, composite, mask, layer, and animate the supplied artwork to create the cinematic 2.5D/3D/X-ray exploded presentation, but must not replace it with unrelated or generated vehicle artwork.
- Do NOT generate stock images, unrelated vehicles, AI-generated vehicles, generic 3D models, or unrelated illustrations.
- Do NOT arbitrarily cut flattened imagery into fake components. Create depth simulation from the supplied artwork.
- If an asset does not exist, SHOW AN ASSET PLACEHOLDER. Do NOT generate a replacement.

## 5. Vehicle Randomization
If random vehicle selection is enabled on the Landing Page, select ONE vehicle on page load. Do NOT continuously randomize vehicles. The selected vehicle remains active while the user interacts.

## 6. Vehicle Selection Page
Display exactly TWO primary vehicle choices:
1. TANK
2. LOGISTIC / OFFICER VEHICLE

Cards should feel like operational gateways rather than generic dashboard cards.
- **Default:** Glass surface, subtle border, vehicle artwork, clear title, short technical description, entry CTA.
- **Hover:** Slight elevation, subtle border highlight, soft glow, vehicle scale approximately 1.02–1.05.
- **Click:** Small press feedback, smooth transition, navigate to Command Center. Avoid large rotations, 3D card flipping, excessive scaling, neon effects.

## 7. Command Center
The Command Center is an operational diagnostic interface. It must NOT look like a generic analytics dashboard.
**Primary hierarchy:**
HEADER → VEHICLE IDENTITY / STATUS → DATASET STATUS → RUL → DIAGNOSTIC STATUS → ML PIPELINE → HISTORY / DETAILS

Use information density intelligently. The vehicle, diagnostic state, pipeline and RUL are the visual priorities.

## 8. ML Pipeline — Exact Structure
The UI must represent the EXISTING project workflow:
DATASET UPLOAD → PREPROCESSING → RANDOM FOREST CLASSIFICATION → [ XGBoost | LSTM + 1D CNN ] → FUSION → FINAL RUL

Random Forest is the classification/router stage. XGBoost and LSTM + 1D CNN are parallel prediction branches. Do NOT represent them as sequential models. Do NOT invent another architecture, coefficients, or formulas. Do NOT change backend ML behavior.

## 9. Dataset Upload
The upload UI should clearly communicate:
IDLE → FILE SELECTED → VALIDATING → UPLOADING → PROCESSING → READY

Only show a state when the application actually knows that state. Do not claim successful preprocessing or inference prematurely.

## 10. RUL Presentation
RUL must be visually prominent.
When valid backend data exists: Show the actual value.
When insufficient data exists: `RUL UNKNOWN` (Insufficient data available for reliable prediction).
Never display: 0.0, random values, fake estimates, placeholder numerical predictions.

## 11. History
History should use actual backend/API information where available (Timestamp, Vehicle, Inference ID, Dataset ID, Classification, RUL, Readiness, Diagnostic result). Do not fabricate historical entries.

## 12. Data Integrity
The frontend must NEVER fabricate: Telemetry, Sensor values, RUL, Classification, Readiness, Diagnostic results, Processing completion, Live system status.
If demo fixtures are used, clearly label them: `DATA SOURCE: DATASET-DERIVED DEMO FIXTURE`

## 13. RBAC (Admin & Maintainer)
Supported roles: ADMIN, MAINTAINER. The UI must NOT imply that mock authentication is production-grade security.
- **ADMIN:** Full system access, Tank, Logistic / Officer Vehicle, Dataset operations, Inference, Diagnostics, History, Fleet, Administration.
- **MAINTAINER:** Vehicle selection, Vehicle evaluation, Dataset upload, Inference, Diagnostics, Permitted history. Maintainer must NOT see usable: User administration, Role management, System administration, Administrative configuration.
Unauthorized navigation should be HIDDEN, not merely disabled.

## 14. Theme System
Support DARK and LIGHT themes. Dark is the primary defense-tech theme.
- **Dark:** Deep neutral background, Dark glass, High contrast text, Restrained accent lighting, Subtle borders, Minimal glow.
- **Light:** Light neutral background, Light translucent surfaces, Dark readable typography, Subtle borders/shadows.
Theme toggle: SUN ↔ MOON. Transition should be short and subtle. Persist selected theme using local storage. Respect OS preference.

## 15. Glassmorphism
Glassmorphism must be SELECTIVE. Use primarily for Navigation, Hero overlays, Vehicle cards, KPI cards, Pipeline stages, RUL, Upload panels, Modals.
Each glass surface should generally use: Semi-transparent surface, Backdrop blur, Subtle border, Soft shadow, Controlled highlight. Do not turn the entire interface into floating glass cards.

## 16. Typography
Use a modern technical sans-serif.
Hierarchy: VEDA → PAGE TITLE → SECTION TITLE → METRIC → SUPPORTING INFORMATION → TECHNICAL METADATA
Technical labels may use uppercase selectively: RUL, VEHICLE STATUS, CLASSIFICATION, INFERENCE, DATASET, SYSTEM STATUS. Avoid excessive uppercase body text.

## 17. Responsive Design
Support Desktop, Laptop, Tablet. Desktop/laptop are primary. On smaller screens: Preserve hierarchy, Keep vehicle visual prominent, Stack pipeline branches logically, Maintain readability, Do not simply shrink everything.

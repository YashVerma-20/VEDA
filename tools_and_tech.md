# VEDA — TOOLS AND TECHNOLOGY STACK

Technology changes require justification and documentation.

## 1. LANGUAGES
Python: ML, inference, backend, agents, data processing.
JavaScript/TypeScript: frontend, React, landing page, browser interaction.

## 2. MACHINE LEARNING
Scikit-learn: Random Forest, preprocessing, evaluation, classical ML.
TensorFlow/Keras: LSTM, 1D-CNN, model training/loading/inference.
XGBoost: nonlinear/tabular RUL prediction/refinement and feature importance.

## 3. DATA
NumPy and Pandas for dataset loading, transformations, feature preparation, evaluation and export.

## 4. MODEL SERIALIZATION
Use framework-appropriate formats such as `.keras`, `.pkl`, `.json`.

## 5. BACKEND
FastAPI + Python.
Pydantic for validation and API schemas.

## 6. DATABASE
PostgreSQL.
TimescaleDB where appropriate.
SQLAlchemy ORM.
Alembic migrations.

## 7. FRONTEND
React.js.
TypeScript preferred.

## 8. LANDING PAGE ANIMATION
Preferred:
- GSAP
- GSAP ScrollTrigger
- React
- CSS transforms
- layered images
- 2D/2.5D techniques

## 9. ANIMATION RESTRICTION
Initial assets are 2D images.
Do NOT make `.glb` mandatory.
Do NOT introduce Three.js, React Three Fiber, GLTF loaders, or Blender unless explicitly approved.

## 10. BROWSER TESTING
Playwright MCP for page loading, navigation, scroll interaction, animation behavior, responsive behavior and dashboard testing.

## 11. REASONING SUPPORT
Sequential Thinking MCP for complex planning/reasoning when useful.

## 12. CONTAINERIZATION
Docker may be used for reproducible deployment.
Potential services: frontend, backend, database.
Training does not need to run inside production API containers.

## 13. VERSION CONTROL
Git. Use meaningful commits.

## 14. ENVIRONMENTS
Python: virtual environment + requirements.txt or pyproject.toml.
Node: package.json + lockfile.

## 15. TESTING
Backend: pytest.
Frontend: Playwright.
ML: dataset validation, shape tests, reload tests, prediction consistency.

## 16. DEPENDENCY PRINCIPLE
Before adding a dependency:
1. explain why
2. verify compatibility
3. check existing dependencies
4. document significant decisions

## 17. TECHNOLOGY PRIORITY
1. integration compatibility
2. reliability
3. maintainability
4. performance
5. developer productivity
6. visual quality where applicable

## 18. PRODUCTION
Training and production inference are separate. Production backend loads trained artifacts.

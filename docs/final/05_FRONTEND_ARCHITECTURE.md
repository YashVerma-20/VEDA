# 05. FRONTEND ARCHITECTURE

## Technology Stack
- **React 18**
- **TypeScript**
- **Vite** (Dev Server & Bundler)
- **GSAP** (ScrollTrigger Animations)
- **React Router DOM** (Client-side routing)

## Core Components
1. `LandingPage.tsx`: Implements the 6-scene ScrollTrigger narrative. Does not require the backend to render.
2. `FleetDashboard.tsx`: Hardcoded list of demonstration vehicles. Displays pipeline summaries and routes to individual vehicle dashboards.
3. `VehicleDashboard.tsx`: The primary interaction surface. Submits dataset-derived JSON fixtures via the API client to the FastAPI backend. Displays the 6-agent orchestration pipeline.

## Principles
1. **Strict Client/Server Separation**: The frontend computes zero intelligence locally. It is merely a visualizer for `OrchestrationResult`.
2. **Dataset Disclosure**: Every screen strictly displays `DATA SOURCE: DATASET-DERIVED DEMO FIXTURE` to maintain transparency.
3. **UNKNOWN State Enforcement**: If `fusion_rul_hours === null`, the frontend is hard-coded to trigger a visual `UNKNOWN` boundary preventing arbitrary `0.0` renders.

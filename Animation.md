# VEDA — Animation & Interaction Specification

## 1. Animation Objective
VEDA animations must communicate vehicle intelligence, mechanical depth, diagnostic processing, technical precision, and controlled defense-grade motion. The final implementation should feel Defense-grade, Engineering-oriented, Cinematic, Technical, Precise, Calm, Premium, and Operational. 

It should NOT feel like a generic SaaS, generic AI dashboard, gaming UI, neon cyberpunk, over-animated, marketing-heavy, or cartoon-like application.

The goal is to make the Landing Page vehicle look like a professional defense-engineering visualization ("vehicle technical inspection / digital engineering visualization").

## 2. Source Asset Rule & Compositing
The user will provide the actual vehicle artwork. For every supported vehicle category (Tank, Logistic / Officer Vehicle), the system may have:
```
NORMAL VEHICLE IMAGE + X-RAY / EXPLODED VEHICLE IMAGE
```
The supplied vehicle artwork is authoritative **source material**.
- The frontend may transform, composite, mask, layer, and animate the supplied artwork to create the cinematic 2.5D/3D/X-ray exploded presentation.
- The frontend must NOT replace it with unrelated or generated vehicle artwork.
- **NEVER** generate stock images, unrelated vehicles, AI-generated vehicles, generic 3D models, or unrelated illustrations.
- If actual separate component assets are provided later, they may be independently animated. Otherwise, use layered compositing, opacity, masking, perspective, displacement, parallax, controlled scaling, depth simulation, or shader effects to simulate depth from the provided flattened imagery without arbitrarily inventing mechanical geometry.
- If an asset does not exist, SHOW AN ASSET PLACEHOLDER. Do NOT generate a replacement.

## 3. Cinematic 2.5D / Depth Presentation
The visualization should create the impression that the vehicle has physical depth, transitioning from:
`NORMAL VEHICLE` → `DEPTH REVEAL` → `X-RAY / INTERNAL STRUCTURE` → `EXPLODED 3D INSPECTION VIEW`

Use an appropriate web graphics/animation technology (e.g., GSAP, Three.js, React Three Fiber, WebGL, Canvas, or CSS 3D transforms) that produces the most convincing result while remaining performant. Use existing project dependencies if suitable before blindly adding new libraries. A convincing 2.5D technical visualization is preferable to a fake/generated 3D vehicle.

## 4. X-Ray Visual Treatment
The exploded visualization should retain the characteristic X-ray appearance of the supplied artwork, communicating internal structure, mechanical components, and technical analysis.
- Do NOT turn the exploded state into a normal-colored vehicle or generic exploded diagram.
- The X-ray image should feel integrated into the normal vehicle.
- Visual sequence: `NORMAL` → `subtle transparency` → `internal X-ray begins appearing` → `depth separation increases` → `exploded X-ray inspection state`
- Use restrained glow, transparency, edge highlights, internal visibility, depth shadows, and technical illumination. The X-ray must remain the visual focus.

## 5. Vehicle Cursor Interaction
The cursor controls the visualization to create the impression of physical depth.
- **MOUSE X:** horizontal viewing/parallax/depth
- **MOUSE Y:** vertical viewing/parallax/depth
- **DISTANCE FROM CENTER:** exploded-view intensity
- **Near center:** NORMAL VEHICLE dominates. Minimal movement.
- **Cursor moves away from center:** Depth increases, X-ray visibility increases, exploded separation becomes more pronounced, perspective changes subtly, internal structure becomes more visible. The visualization resembles a technical exploded/X-ray inspection.
- **Cursor returns toward center / leaves:** Vehicle smoothly returns toward the normal integrated state and settles.
- **Avoid:** Violent movement, shaking, excessive rotation, spinning, elastic cartoon effects, constant animation.

## 6. Entry Animation
The landing page entry sequence should be short and cinematic (approximately 1–2 seconds total).
**Order:**
1. Background
2. VEDA branding
3. Hero heading
4. Supporting text
5. Vehicle visualization (must enter as a dimensional object, not a simple `<img>` fade-in)
6. Supporting technical metadata
7. ENTER VEDA CTA
8. Cursor interaction becomes active

Do not create a long loading sequence. The user should be able to interact almost immediately.

## 7. Vehicle Selection Animations
Cards should feel like operational gateways rather than generic dashboard cards.
- **Hover:** Slight elevation, subtle border highlight, soft glow, vehicle scale approximately 1.02–1.05.
- **Click:** Small press feedback, smooth transition, navigate to Command Center.
- **Avoid:** Large rotations, 3D card flipping, excessive scaling, neon effects.

## 8. Pipeline States
Every stage must support PENDING, PROCESSING, COMPLETE, ERROR, and UNKNOWN.
- **PROCESSING:** Subtle pulse, progress indicator, moving line, controlled glow.
- **COMPLETE:** ✓ COMPLETE. Use subtle reveal.
- **ERROR:** ERROR. Use restrained visual alert.
- **UNKNOWN:** UNKNOWN. Remain visually calm.
Never show a stage as completed unless the backend actually reports completion.

## 9. RUL Reveal
When a valid RUL first appears: Small fade, small scale reveal, then settle. Do NOT continuously animate the value.

## 10. Theme & Navigation Transitions
- **Theme:** Transition should be short and subtle (SUN ↔ MOON).
- **Navigation:** Use fade and small vertical translation. Avoid full-screen wipes, long transitions, excessive zoom, or dramatic page rotations.

## 11. Accessibility & Performance
Respect `prefers-reduced-motion`. When enabled: Disable large vehicle movement, minimize parallax, reduce route transitions, avoid unnecessary animation, and keep state changes clear.
- Animations should prefer transform, opacity, and GPU-friendly properties. Avoid expensive continuous layout calculations. Cursor animation must use smooth interpolation.

## 12. Asset Loading
Vehicle loading sequence: `IMAGE REQUEST` → `PLACEHOLDER / SKELETON` → `IMAGE LOADED` → `FADE INTO POSITION`.
If loading fails, display `VEHICLE VISUAL UNAVAILABLE`. Do NOT generate a replacement.

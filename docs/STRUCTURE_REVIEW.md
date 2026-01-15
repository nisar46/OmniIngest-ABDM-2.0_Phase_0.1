# 📂 Project Structure Review & Launch Readiness

## Current State Analysis
The project currently resides in a flat directory structure (`d:\Omnigest_ABDM_2.0`). While functional for Phase 0.1 rapid prototyping, a professional "Launch Ready" state requires better separation of concerns.

## Recommended Cleanup Actions

### 1. Source Code Organization
Move the core logic files into a `src` package to declutter the root.
- `app.py` -> Root (Keep here as entry point)
- `ingress.py`, `compliance_engine.py`, `universal_adapter.py`, `database_manager.py` -> `src/core/`
- `abdm_api_client.py` -> `src/api/`

### 2. Documentation
Centralize all documentation.
- `PHASE_0.1_DEEP_DIVE.md`, `TECHNICAL_FACT_SHEET.md`, `LINKEDIN_POST.md` -> `/docs/`
- Keep `README.md` and `LICENSE` in Root.

### 3. Data Management
Don't mix code with data.
- `*.csv`, `*.json`, `*.xml`, `*.db` -> `/data/` or `/data/samples/`
- `raw_data.*` files -> `/data/raw/`

### 4. Utilities & Scripts
Separate operational scripts from application logic.
- `gen_demo_data.py`, `record_demo.py`, `generate_carousel.py` -> `/scripts/`

## Launch Checklist
- [x] **README.md**: Updated with Architect-grade content.
- [x] **License**: MIT 2026 present.
- [x] **Compliance Doc**: Explains Rule 8.3 & FHIR R5.
- [ ] **Clean Root**: Remove `__pycache__` and temp `*.webm` / `*.mp4` files before zipping/committing (add to `.gitignore`).
- [ ] **Requirements**: Ensure `requirements.txt` is minimal and accurate.

## "Vibe" Score
Current Vibe: **Hi-Tech / Prototyping**. 
Target Vibe: **Enterprise / Architect**.
*Actioning the directory moves above will achieve the Target Vibe.*

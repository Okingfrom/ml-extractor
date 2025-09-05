# ML Extractor Reboot – Roadmap

Status: Baseline minimal mapping + enrichment + minimal React UI (monolith, no API yet)

Guiding Principle:
Do the smallest NEXT valuable slice. No future scaffolding until a phase needs it.

## Phase Overview (High Level)

| Phase | Goal | Core Deliverable | MUST NOT ADD |
|-------|------|------------------|--------------|
| 0 | Baseline verify | Tests for enrichment + CLI confidence | API, DB, Auth |
| 1 | Deterministic API | Simple FastAPI app with /health, /map | AI calls, persistence |
| 2 | UI → API wiring | React form calls /map | Styling frameworks, routing complexity |
| 3 | Validation & metadata | Validation + enrichment trace metadata | AI fallback |
| 4 | AI fallback (optional) | One guarded AI path (feature flag) | Multiple models, caching layer |
| 5 | Quality harness | Golden dataset + accuracy metrics | Over-optimizing infra |
| 6 | Logging & metrics | Structured logs + basic perf timing | External APM vendors |
| 7 | Packaging & separation | Optional split frontend/backend OR container image | Full microservices |
| 8 | Scaling extras (future) | Queue or batch worker if needed | Premature sharding |

---

## PHASE 0 – Baseline Stabilization (Now)

Objective:
Confidence that current core + enrichment works and will not regress.

Scope:
- Add unit tests (one per enrichment).
- Add test for CLI mapping end‑to‑end.
- Introduce simple validation (optional warning only).

Non‑Scope: API, AI, deployment.

Acceptance:
- pytest passes < 5s locally.
- At least 80% lines of enrichment modules executed.

Tasks:
1. Create tests/test_enrich_*.py (brand, sku, color, weight, ean).
2. Add tests/test_cli_map.py.
3. Add simple validation stub (Phase 3 if you prefer later).

---

## PHASE 1 – Add Minimal API (Monolith)

Objective:
Expose mapping via HTTP without DB or auth.

Tech:
FastAPI (light), uvicorn (dev only).

Endpoints:
- GET /health → {status:"ok", version}
- POST /map {records:[{...}]} → {records:[mapped]}
- POST /map/single {record:{...}} → {record:mapped}

Directory (added):
src/api/__init__.py  
src/api/app.py

Acceptance:
- curl POST /map returns enriched fields.
- No new dependencies except fastapi + uvicorn.

Non‑Scope:
AI, sessions, users, persistence.

---

## PHASE 2 – Wire UI to API

Objective:
React UI sends request to /map; shows enriched output.

Scope:
- Add fetch call in App.js.
- Support multiple rows (optional).
- Loading + error states.

Non‑Scope:
Auth, routing, styling frameworks (keep plain CSS).

Acceptance:
- User enters title/category → sees enriched JSON from backend.
- No build artifacts committed (dist/ ignored).

---

## PHASE 3 – Validation + Metadata Trace

Objective:
Return mapping record plus metadata (method, warnings, trace).

Add:
- src/validation.py
- Each enrichment returns (record, info?) OR store decisions in record["_meta"].

Decision:
Use record["_meta"] = {"enrich_chain":[{"field":"brand","method":"rule"}], "warnings":[...]}

Acceptance:
- /map returns records with _meta.
- Warnings appear if title missing.

Non‑Scope:
External logging, AI inference.

---

## PHASE 4 – Single AI Fallback (Optional)

Objective:
Introduce one AI-assisted field (e.g., brand normalization) behind a flag.

Add:
- src/ai/brand_normalizer.py (interface: normalize_brand(brand:str, enable_ai:bool)->(value, meta))
- Feature flag: env var ENABLE_AI=1 or function param.

Safety:
If AI fails/timeouts returns original brand & meta.method="ai_failed".

Acceptance:
- When flag off → no AI call.
- When flag on → code path test simulated with stub (no real model first iteration).

---

## PHASE 5 – Golden Dataset & Metrics

Objective:
Create a small curated dataset to evaluate mapping correctness.

Add:
- data/golden/input.csv
- data/golden/expected.csv
- tests/test_golden_consistency.py (compares mapped output to expected with tolerance rules)

Add script:
tools/eval_golden.py → prints pass/fail & mismatches.

Acceptance:
- Running evaluation passes.
- Document how to update golden set.

---

## PHASE 6 – Observability (Local)

Objective:
Structured JSON logging + simple timing metrics.

Add:
- src/observability/logging.py
- Middleware for FastAPI logging request time.
- Enrichment steps log decisions to debug-level (toggle via env).

Acceptance:
- Logs show JSON lines.
- /map latency printed.

Non‑Scope:
External SaaS ingestion.

---

## PHASE 7 – Packaging / Optional Split

Option 1:
Remain monolith; produce Dockerfile.

Option 2:
Split:
- backend/
- frontend/
(Do only if truly needed—UI complexity or separate deploy cadence.)

Acceptance:
- Running docker build & docker run exposes API + UI (if served separately maybe Nginx static).

---

## PHASE 8 – Scaling (Only If Real Load)

Potential:
- Async batch jobs
- Rate limiting
- Caching repeated AI lookups

---

## DEFINITION OF DONE (Per Task)

A task is DONE when:
1. Code added with minimal surface (no unused helpers).
2. Tests updated or added (no reduction in coverage).
3. README or relevant doc updated if behavior externally visible.
4. No console.print debug left (use logging).
5. Lint passes (if/when linter added).
6. AI Guardrails checklist satisfied (see AI_GUARDRAILS.md).

---

## RISK REGISTER (Common)

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bloat reintroduced from legacy | High | Keep KEEP list canonical + guardrails |
| AI code drift (unnecessary files) | Medium | Enforce prompt template & review |
| Silent enrichment regressions | High | Golden dataset + per-field tests |
| Over-engineering early | Medium | Roadmap gating; refuse features ahead of phase |
| Large dependency creep | High | Dependency justification rule |

---

## PROMPTING PHASE INSTRUCTIONS (Summary For AI)

At start of each phase:
"State: phase <n>. Show: allowed scope, proposed files (list only), ask confirm."

For each change:
- Provide diff preview BEFORE writing.
- Ask: "Approve? (yes/no)"
- If adding > 3 files in one step, require justification.

If user request outside phase scope → respond with reminder and small safe alternative.

---

## BACKLOG STARTER

| ID | Title | Phase | Status |
|----|-------|-------|--------|
| T1 | Add enrichment tests | 0 | TODO |
| T2 | Add CLI test | 0 | TODO |
| T3 | Introduce FastAPI app | 1 | TODO |
| T4 | Wire React fetch | 2 | TODO |
| T5 | Add _meta enrichment trace | 3 | TODO |
| T6 | Add validation warnings | 3 | TODO |
| T7 | AI brand normalization flag | 4 | TODO |
| T8 | Golden dataset harness | 5 | TODO |
| T9 | Structured logging | 6 | TODO |

(Manage this manually or create issues later.)

---

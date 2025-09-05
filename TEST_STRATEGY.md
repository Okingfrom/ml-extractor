# Test Strategy

Goal:
Fast, focused feedback. Keep suite under 10s locally.

## Pyramid

1. Unit (70–80%):
   - Enrichment modules
   - Validation logic
   - AI fallback stub

2. Functional (15–20%):
   - CLI mapping end‑to‑end
   - API /map returns expected shape

3. Golden / Regression (5–10%):
   - Golden dataset consistency (Phase 5+)

## Naming

tests/test_<area>.py

## Unit Test Patterns

For enrichment:
- Test default path (no change)
- Test enrichment path (field added)
- Test edge (empty input)

## CLI Test

Simulate invocation with temporary CSV; assert outputs have enriched fields.

## API Tests (Phase 1+)

Use FastAPI TestClient (no external server).
- test_health_ok
- test_map_single
- test_map_batch_length

## Golden Dataset (Phase 5)

Compare mapped output to expected row by row; print diff summary.

## Performance Sentinel (Optional Phase 6+)

Add a test that maps N=1000 sample rows under threshold (e.g. <0.5s). Skip if environment too slow.

## Running

Standard:
pytest -q

Focused:
pytest tests/test_enrich_brand.py::test_brand_from_title -q

## Future AI Tests

Mock AI provider:
- Simulate success → method="ai"
- Simulate failure → method="ai_failed"

Ensure deterministic fallback.

---

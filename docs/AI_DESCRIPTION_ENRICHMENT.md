# AI Description & Attribute Enrichment (Phase 4 Spec)

Status: Planned – do NOT implement before Phase 4 gate.

## Purpose
Enhance MercadoLibre bulk listing templates by generating or refining optional textual fields while never compromising required integrity fields.

## Design Goals
- Deterministic core stays stable if AI flag disabled.
- Transparent provenance: each AI-enriched field recorded in `_meta.enrich_chain`.
- Reversible: disabling AI yields same baseline deterministic output as before.

## In-Scope (Phase 4)
- Descriptions (short + optional extended bullets)
- Attribute suggestion (color, material, brand normalization if missing)
- Title style normalization (optional)
- Multilingual adaptation (es-AR, es-MX, pt-BR)

## Out of Scope (Phase 4)
- Image generation
- Category prediction
- Price optimization
- Multi-model ensemble

## Data Contract
Input record (subset):
```
{
  "title": "...",
  "category_id": "...",
  "brand": "...",
  "attributes": { "color": "...", "material": "" },
  "_meta": { ... }
}
```
Output modifications (if AI enabled):
- `description` (if requested)
- `attributes` sub-keys added only with confidence ≥ threshold (default 0.6)
- `_meta.ai = { "fields_modified": [...], "model":"stub-v1", "locale":"es-AR" }`

## Function Signature (planned)
```
def enrich_ai(record: dict, locale: str, modes: set[str], enable_ai: bool) -> dict:
    """
    modes may include: {"description","attributes","title_normalization"}
    """
```

## Confidence Handling
- Each generated attribute appended to `_meta.enrich_chain`:
```
{
  "field": "attributes.color",
  "method": "ai",
  "confidence": 0.82,
  "source": "title_inference"
}
```
- If confidence < 0.5 → discard (do not mutate field).

## Failure Modes
| Failure | Handling | Meta |
|---------|----------|------|
| Model timeout | Skip AI, return baseline | method=ai_failed |
| Empty model output | Leave field unchanged | method=ai_failed |
| Hallucinated forbidden token | Strip & log warning | warning entry |

## Prompt Assembly (Internal)
Base System Prompt (template):
```
You enrich MercadoLibre product row data.
NEVER invent: category_id, price, SKU, regulatory codes.
Locale target: {{locale}}
Modes active: {{modes}}
Return ONLY enriched text values (UTF-8).
If a field should remain unchanged, do not output it.
```
User Content Template:
```
Existing fields:
{{json_compact_record}}
Requested enrichments:
{{modes_list}}
Constraints:
- Keep tone professional & concise.
- For description: 1 sentence intro + up to 5 bullets (if description mode).
- Do not guess warranty or certifications.
```
Parsing Strategy:
- Model output parsed line-by-line: `field_name: value`
- Reject lines with unknown fields.

## Testing Strategy
1. Unit: mock model returns deterministic string → assert insertion.
2. Failure: raise exception → assert record unchanged + meta.ai_failed.
3. Locale test: input es-AR vs pt-BR → ensure locale marker or language differences appear.
4. Regression: baseline snapshot with AI disabled identical to pre-AI snapshot.

## Implementation Order
1. Add scaffolding + flag (no model call).
2. Add mock provider for tests.
3. Insert AI step after deterministic enrichment but before validation (or after? decide; default: after deterministic so it can leverage enriched brand/sku).
4. Add CLI flag `--enable-ai` (Phase 4 optional).
5. Add API query parameter `enable_ai=true`.

---

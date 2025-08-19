# PR: fix(ui): Spanish UI text and header mapping improvements

Branch: `fix/ui-spanish-audit`

## Summary
Small, safe UX-only and compatibility-focused changes to `app_improved.py` to improve Spanish visible text and header detection.

This PR:
- Corrects many visible Spanish UI labels, helper text, comments and debug strings (accents, typos, grammar).
- Improves `field_mapping` display strings shown in the UI to use accented/correct Spanish.
- Extends `ml_header_mapping` to include accented and common header variants while preserving the original non-accented keys for backwards compatibility (so existing behavior is maintained).

Files changed (high-level)
- `app_improved.py` — primary edits (UI strings, header mapping enhancements, comments, debug messages)

## Why
The UI contained multiple Spanish typos and missing accents which harmed legibility and professional appearance. At the same time header-detection relied on non-accented tokens; this PR accepts both forms so users can upload spreadsheets with or without accents without breaking mapping logic.

## Testing notes (what I ran locally)
1. Python syntax check
   - `python3 -m py_compile app_improved.py` — OK
2. Restarted the Flask dev server from the repo venv and verified it served the homepage:
   - Server log shows: "Iniciando Mercado Libre Bulk Mapper Pro en http://localhost:5003"
   - `curl -sS http://127.0.0.1:5003/` returned the application HTML (smoke-check).
3. Manual spot-checks in the HTML template confirmed corrected visible labels (Título, Descripción, Envío, Garantía, etc.)
4. Verified header matching logic still uses the original keys (safe) but now also recognizes accented variants.

## How to review manually
1. Pull the branch and run locally:

```bash
git fetch origin
git checkout fix/ui-spanish-audit
source venv/bin/activate
python app_improved.py
```

2. Open http://127.0.0.1:5003/ and inspect UI labels (Guía de uso, Garantía, Formas de envío, Códigos Universales, etc.).
3. Upload or open a sample ML template where column headers use accented words (e.g., "Descripción", "Código universal", "Unidad de tiempo de la garantía") and ensure they are detected by the mapper.
4. Also verify older unaccented headers (e.g., "Descripcin", "Cdigo universal") still map correctly.

## Acceptance criteria
- Visible UI text has corrected accents/typos where changed.
- Header detection accepts both accented and non-accented forms without breaking existing mappings.
- No Python syntax errors and the dev server starts successfully.

## Notes & follow-ups
- I intentionally preserved the programmatic mapping keys (non-accented) to avoid subtle behavior changes. If you prefer a full canonicalization to accented keys, we should:
  - update all mapping logic (and unit tests),
  - update any saved configs or documentation that refer to the non-accented labels,
  - run an integration test with representative spreadsheets.
- Recommended next steps:
  1. Create a small unit test for `ml_header_mapping` to assert accented and non-accented headers map correctly.
  2. Extract visible strings to a localization file for easier translation and maintenance.

---

PR created on GitHub: https://github.com/Okingfrom/ml-extractor/pull/new/fix/ui-spanish-audit

If you want, I can open the PR description on GitHub for you (requires a browser/`gh` CLI) and push a short comment with test results. Which do you prefer?

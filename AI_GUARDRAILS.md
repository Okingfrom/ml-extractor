# AI Guardrails & Change Checklist

Purpose:
Prevent the AI (or any contributor) from adding bloat or deviating from roadmap.

## ALWAYS ASK BEFORE CODE (Checklist)

Before proposing changes, the AI must answer internally:
1. Which phase am I in?
2. Is the request in-scope for this phase? (yes/no)
3. What is the smallest change set (files + functions)?
4. Do I reuse existing modules instead of creating new ones?
5. Will I add a new dependency? Justify or reject.

If any answer indicates scope drift → ask user for confirmation.

## ALLOWED FILES BY CATEGORY

Core Logic:
- src/mapper.py
- src/enrichment/*

API (Phase >=1):
- src/api/app.py
- src/api/routes/*.py (only if >3 route files needed; otherwise keep single file)

UI (Phase >=2):
- frontend/src/App.js (expand gradually)
- No new folders until justified.

Validation & Metadata (Phase >=3):
- src/validation.py
- _meta usage inside mapper/enrichment

AI (Phase >=4):
- src/ai/<feature>.py
- No more than ONE AI module per step.

Testing:
- tests/test_<area>.py (one module per concern)
- Avoid giant catch‑all test files.

Tooling (only if needed):
- tools/<purpose>.py (script must be <150 lines; else split with justification)

## HARD "DO NOT ADD" (Until Explicitly Approved)

- databases (postgres, mongo, redis)
- message queues
- docker-compose with multiple services
- ORMs
- authentication logic
- feature toggling frameworks (use simple env)
- CSS frameworks (Tailwind, etc.) early
- complex state libraries in React (Redux, etc.)

## DEPENDENCY POLICY

Add a dependency only if:
1. Standard library insufficient AND
2. Introduces ≥50 lines saved AND
3. Low transitive risk.

Describe justification with:
- Name
- Purpose
- Alternatives considered

## MODIFICATION RULES

- Prefer editing existing file over creating a sibling unless file >250 lines.
- If file >300 lines → propose refactor plan first.
- Delete dead code instead of leaving commented blocks.

## ENRICHMENT RULE

Each enrichment function:
- Input: record (dict)
- Output: record (same dict)
- Must NOT raise for missing keys.
- Side-effect limited to enriched fields + _meta updates.

## METADATA (_meta) FORMAT (Phase 3+)

record["_meta"] = {
  "enrich_chain": [
    {"field":"brand","method":"rule","confidence":1.0}
  ],
  "warnings": ["missing title"]
}

Confidence: 1.0 for deterministic; AI fallback <1.0.

## AI FALLBACK RULE (Phase 4+)

- Must be behind enable_ai flag.
- On failure: method becomes "ai_failed".
- No infinite retries (1 attempt).
- Must have a stub test using a fake provider.

## TEST COVERAGE MINIMUM

- New function → at least one test.
- Bug fix → regression test referencing issue ID.
- Golden dataset only after Phase 5.

## PROMPT TEMPLATE (FOR ANY CHANGE)

User asks → AI responds with:

CHANGE PLAN:
Phase: <n>
In-Scope: <yes/no>
Files Affected:
- <file1>: reason
Diff Preview (pseudo or real):
<…>
Questions / Confirmation Needed:
- <question>

Await user "yes" before producing final patch.

## REJECTION PHRASES

If out-of-scope: "This request is not in scope for phase <n>. Options: (a) queue for later, (b) narrow scope."

## DEFINITION OF DONE (Per PR)

- All tests pass.
- Only in-scope files touched.
- Docs updated if public behavior changes.
- No new TODO left untracked.

---

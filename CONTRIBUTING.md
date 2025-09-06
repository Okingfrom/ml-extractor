# Contributing

## 1. Core Rules
- Stay within current roadmap phase.
- Every new function must have at least one test.
- No new dependencies without justification.
- No large refactors sneaked in with feature changes.
- Keep PRs ≤ 300 added lines (tests included).

## 2. Branch Naming
feature/<short-topic>  
fix/<issue-id-or-bug>  
chore/<maintenance>

## 3. Commit Style
<type>: <concise summary>  
Types: feat, fix, chore, docs, test, refactor

## 4. Workflow
1. Open small plan (what + files + test(s)).
2. Get approval (even self-check).
3. Implement.
4. Run tests locally (pytest -q).
5. Submit PR with summary + risk note.

## 5. Anti-Bloat Policy
Reject if:
- Adds > 1 new top-level directory
- Adds dependency not justified
- Creates code not used this phase

## 6. Definition of Done
- Tests pass
- In-scope only
- Docs updated if API/CLI changes
- No debug prints
- Lint (when added) passes

---

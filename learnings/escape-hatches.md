# Escape Hatches (when governance blocks you)

- **Fix-attempt cap (2 consecutive edits):** Run tests via Bash (pytest, npm test, etc.) to reset.
- **Compound budget exhausted (10 mutations):** Run `echo budget-reset` via Bash after operator approval.
- **Circuit breaker (edit-test spiral or drift):** Same — `echo budget-reset` resets all state.
- **Risk-classifier blocking (high-risk, no plan):** Create a plan file at `.claude/plans/{task-id}.md`, or ask operator to set `risk: medium` on the task.
- **Blast-radius blocking (out-of-scope file):** Update the task's `section` field, or file a separate task for the out-of-scope change.
- **Reference-check warning:** Advisory only — warns when an Edit replaces a string found in evals/ or hooks/. Proceed, but update consumers.
- **Build-integrity warning:** Acknowledge and proceed — it's a warning, not a block.
- **All state files** are in `.claude/hooks/fix-attempt-tracker.state` (gitignored). Deleting it resets everything.
- **Test isolation:** An autouse conftest fixture resets hook state files (fix-attempt-tracker.state) between every test. If tests seem flaky due to accumulated state, the fixture handles it — no manual reset needed.

# v3 Migration Proposal

Derived from: `~/Downloads/THE_FACTORY_v3_migration_plan.md`
Created: 2026-03-26

---

## Summary

The v3 migration plan audits THE FACTORY against current Claude Code standards and identifies six phases of work. After reviewing the actual codebase, here's what's already done, what's actionable, and what should be deferred or dropped.

---

## Phase 1: Hook Migration — ALREADY DONE (mostly)

**Current state:** `.claude/settings.json` already wires all hooks via native `PreToolUse`, `Stop` events with proper matchers. The scripts already parse `$TOOL_INPUT` JSON from stdin. There is no custom hook dispatch infrastructure to delete.

**Remaining gaps:**

| # | Item | Effort | Notes |
|---|---|---|---|
| 1.1 | Add `PostToolUse` reset for fix-attempt-tracker | Small | The v3 plan recommends splitting into pre (gate) + post (reset). Currently, reset logic lives inside `git-guard.sh` AND `fix-attempt-tracker.sh` redundantly. Moving the Bash test-detection reset to a PostToolUse hook is cleaner but not urgent — current approach works. |
| 1.2 | Wire `state-snapshot.py` on `SessionEnd` instead of `Stop` | Small | `SessionEnd` is more semantically correct (fires once per session exit, not on every agent stop). Low risk, easy swap. |
| 1.3 | Add eval: `test_native_hooks_settings_valid` | Small | Validate that `settings.json` parses correctly, all referenced scripts exist and are executable. |
| 1.4 | Evaluate Langfuse hook for deletion | Audit | If Langfuse SDK + OpenTelemetry auto-instrumentation covers the same data, delete `langfuse-trace.py`. Otherwise keep as-is. |

**Recommendation:** Do 1.2 and 1.3 now. Defer 1.1 (works fine as-is). Audit 1.4 next time Langfuse is touched.

---

## Phase 2: Skill Format Standardization — PARTIALLY DONE

**Current state:** Flow skills (`.claude/skills/debug-flow/`, `feature-flow/`, `refactor-flow/`) already have YAML frontmatter with `name` and `description`. Portfolio-level skills (`skills/section-review/`, `skills/brainstorm/`, `skills/handoff/`, `skills/project-scaffold/`, `skills/protocol-review/`) do NOT have frontmatter.

**Action items:**

| # | Item | Effort |
|---|---|---|
| 2.1 | Add YAML frontmatter to all 5 portfolio-level skill files | Small |
| 2.2 | Add eval: `test_all_skills_have_frontmatter` | Small |
| 2.3 | Verify `description` covers trigger keywords from the trigger table in CLAUDE.md | Small |

**Recommendation:** Do all three. Straightforward, no behavioral change.

---

## Phase 3: Terminology Alignment — DOCUMENTATION ONLY

**Current state:** THE FACTORY uses custom vocabulary (flow routing, constitution, progressive disclosure, etc.) that maps cleanly to standard terms.

**Action items:**

| # | Item | Effort |
|---|---|---|
| 3.1 | Add terminology mapping table to README.md | Small |
| 3.2 | Update INIT.md (if it exists) to use standard terms when explaining the system | Small |
| 3.3 | Leave CLAUDE.md internal terminology as-is (it works, it's already the system prompt) | None |

**Recommendation:** Do 3.1. Low-priority. Helpful for onboarding/discoverability but zero operational impact.

---

## Phase 4: Observability Consolidation — REQUIRES AUDIT

**Current state:** `scripts/token-dashboard.py` and `scripts/experiment.py` exist.

**Action items:**

| # | Item | Effort |
|---|---|---|
| 4.1 | Audit token-dashboard.py vs Langfuse dashboards | Medium |
| 4.2 | Audit experiment.py vs Promptfoo/Braintrust | Medium |
| 4.3 | Delete or refactor based on audit findings | Varies |

**Recommendation:** Defer until Langfuse usage is more mature. The v2.2 memory note already flags this as planned work. Don't duplicate effort.

---

## Phase 5: State Management — SCHEMA FORMALIZATION

**Current state:** JSONL files exist in `.agent/` but lack formal schemas in `.agent/schemas/`.

**Action items:**

| # | Item | Effort |
|---|---|---|
| 5.1 | Create JSON schemas for `tasks.jsonl`, `runs.jsonl`, `incidents.jsonl` | Medium |
| 5.2 | Add eval: `test_all_jsonl_entries_valid` | Medium |
| 5.3 | Document state model using standard terminology | Small |

**Recommendation:** Do 5.1 and 5.2 — they catch real bugs (malformed JSONL entries). Skip the LangGraph migration; JSONL is fine at current scale.

---

## Phase 6: Formalize Novel Contributions — DOCUMENTATION

**Current state:** Section contracts, fix-attempt tracker, and SYNTROPY are well-implemented but not documented as standalone adoptable patterns.

**Action items:**

| # | Item | Effort |
|---|---|---|
| 6.1 | Write standalone doc: `skills/section-review/BOUNDED_CONTEXT_CONTRACTS.md` | Medium |
| 6.2 | Make fix-attempt tracker threshold configurable (env var or config) | Small |
| 6.3 | Add cross-references to standard terms in SYNTROPY.md | Small |
| 6.4 | Publish fix-attempt-tracker as a standalone adoptable hook | Medium |

**Recommendation:** Defer. This is packaging/publishing work with no operational payoff for THE FACTORY itself.

---

## Prioritized Task Queue

Ordered by value/effort ratio, ready to be added to `.agent/tasks.jsonl`:

### Batch 1 — Quick wins (single session)

1. **Add YAML frontmatter to 5 portfolio-level skills** (Phase 2.1)
2. **Add eval: `test_all_skills_have_frontmatter`** (Phase 2.2)
3. **Add eval: `test_native_hooks_settings_valid`** (Phase 1.3)
4. **Switch state-snapshot from `Stop` to `SessionEnd`** (Phase 1.2)

### Batch 2 — Schema formalization (single session)

5. **Create JSON schemas for JSONL files** (Phase 5.1)
6. **Add eval: `test_all_jsonl_entries_valid`** (Phase 5.2)

### Batch 3 — Documentation (when time allows)

7. **Add terminology mapping to README.md** (Phase 3.1)
8. **Make fix-attempt tracker threshold configurable** (Phase 6.2)

### Deferred — Requires audit or has low ROI

- Langfuse hook audit (Phase 1.4) — do when Langfuse is next touched
- Token dashboard / experiment.py audit (Phase 4) — already tracked in v2.2 plan
- Standalone documentation for novel contributions (Phase 6.1, 6.3, 6.4) — packaging work
- PostToolUse split for fix-attempt-tracker (Phase 1.1) — current dual-path reset works

---

## What the v3 Plan Got Wrong (or is already done)

1. **"Delete custom hook dispatch infrastructure"** — There is none. Hooks are already wired natively via `settings.json`. The v3 plan assumed a custom dispatch layer that doesn't exist.
2. **"Rewrite hooks to read from `$TOOL_INPUT`"** — They already read JSON from stdin, which IS the native hook input mechanism.
3. **"Plan-gate hook"** — The v3 plan doesn't mention `plan-gate.sh`, which is a novel hook not covered by the migration. It should stay.
4. **"SessionEnd for state-snapshot"** — The v3 plan is correct that SessionEnd is more appropriate than Stop, but the difference is minor (Stop fires more often, which means more frequent snapshots — arguably a feature, not a bug).

---

## Decision Required

Should I convert Batch 1 into tasks in `.agent/tasks.jsonl` and start executing, or do you want to review/adjust priorities first?

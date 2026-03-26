# Deep Research Findings → Actionable Improvements

Source: `~/Downloads/deep-research-report TFv2 review.md` (external audit of THE_FACTORY)
Created: 2026-03-26
Cross-references: `v3-migration-proposal.md`, memory `project_v22_improvement_plan.md`

---

## Triage

The deep research report covers architecture, alternatives, and migration paths. Many findings confirm decisions already made or overlap with v2.2/v3 plans. This proposal extracts **net-new actionable items** — things the report surfaced that aren't already tracked.

### Already covered (no new action needed)

| Finding | Covered by |
|---|---|
| Hook migration to native events | v3 proposal Phase 1 |
| CI-gate eval suite | v2.2 Priority 2 |
| Drop experiment framework for Promptfoo | v2.2 Priority 4 |
| Drop token dashboard for Langfuse | v2.2 Priority 5 |
| Skill frontmatter standardization | v3 proposal Phase 2 |
| JSONL → SQLite when needed | v2.2 Priority 7 |

### Net-new items from the report

---

## Item 1: Declare all dependencies explicitly

**Finding:** `inspect-ai` is required for experiment mode but only discoverable via runtime error. `pyproject.toml` lists only optional deps. YAML parsing libraries may also be missing.

**Action:** Audit `scripts/` imports. Add install profiles to `pyproject.toml`:
- `[project.optional-dependencies.experiments]` — inspect-ai, pyyaml
- `[project.optional-dependencies.observability]` — langfuse
- `[project.optional-dependencies.evals]` — deepeval, pytest

**Effort:** Small
**Priority:** Do when next touching `pyproject.toml`

---

## Item 2: Add a LICENSE file

**Finding:** No LICENSE file in repo root. Blocks reuse/adoption if the repo goes public.

**Action:** Add `LICENSE` (MIT or Apache-2.0 — operator decision). If staying private, add a `LICENSE` with "All rights reserved" to make the status explicit.

**Effort:** Trivial
**Priority:** Before any public sharing

---

## Item 3: Document the portfolio workspace assumption

**Finding:** Variant configs reference `projects/DjTools/scue/skills/...` etc. A user cloning only THE_FACTORY can't run experiments without the right project repos at the right paths. This is noted but never documented.

**Action:** Add a `SETUP.md` or section in README covering:
1. THE_FACTORY is a pipeline repo; project repos are separate
2. Expected workspace layout (`projects/<name>/` with own git, own CLAUDE.md)
3. Which scripts/experiments require project repos present
4. How to scaffold a new project into the workspace (`skills/project-scaffold/`)

**Effort:** Medium
**Priority:** Before any external contributor or second operator

---

## Item 4: Portable guardrails layer

**Finding:** Hook wiring assumes Claude Code env (`PreToolUse`/`Stop` events, `$CLAUDE_PROJECT_DIR`, `.venv/bin/python`). These don't execute in other agent runtimes.

**Action:** This is a design constraint, not a bug — THE_FACTORY is purpose-built for Claude Code. But two small hardening steps:
1. **Eval:** Add `test_hook_scripts_portable_prereqs` — verify each hook script checks for its runtime assumptions (e.g., python exists, env vars present) and fails gracefully with a message, not a silent crash.
2. **Document:** Add a "Runtime Requirements" section noting Claude Code dependency explicitly, so evaluators/adopters don't wonder.

**Effort:** Small
**Priority:** Low — only matters if considering other runtimes

---

## Item 5: Retrieval-augmented skill loading (research item)

**Finding:** Domain skills use static file paths. The report suggests vector-store retrieval as an alternative to path-based loading.

**Assessment:** This is the wrong direction for THE_FACTORY's architecture. Static paths are deterministic, auditable, and version-controlled — exactly the properties we optimize for. Retrieval adds stochasticity and failure modes. The trigger table + LLM fallback (v2.2 Priority 6) is the right solution for skill discovery.

**Action:** None. Log this as a rejected alternative.

---

## Item 6: Experiment reproducibility without project repos

**Finding:** Inspect tasks reference project-specific files. Experiments aren't self-contained.

**Action:** Create a `tasks/standalone/` directory with 2-3 experiment tasks that use inline fixtures (no external project dependency). These serve as:
- Smoke tests for the experiment framework itself
- Examples for new operators setting up their own tasks
- CI-runnable experiment validation

**Effort:** Medium
**Priority:** Alongside v2.2 Priority 4 (Promptfoo migration) — if we're touching experiments anyway

---

## Item 7: Maintenance signals for public repos

**Finding:** No Issues, no PRs, no Actions — limits external confidence in project health.

**Action:** If/when going public:
1. Enable GitHub Actions with `pytest evals/ -v` on push (overlaps v2.2 Priority 2)
2. Create 3-5 tracking issues for the v2.2 roadmap items (makes roadmap visible)
3. Add a simple `CONTRIBUTING.md`

**Effort:** Small per item
**Priority:** Gate on decision to make repo public

---

## Summary: What to do now vs. later

### Do now (next session batch)
- **Item 1** — dependency profiles in pyproject.toml (small, prevents friction)
- **Item 6** — standalone experiment tasks (do alongside Promptfoo migration)

### Do before going public
- **Item 2** — LICENSE file
- **Item 3** — workspace setup docs
- **Item 7** — GitHub maintenance signals

### Parked
- **Item 4** — portable guardrails (low priority, design constraint)
- **Item 5** — rejected (retrieval-based skills)

### Already in flight (no new work)
- Hook migration, CI-gating, Promptfoo, Langfuse consolidation, SQLite, skill frontmatter

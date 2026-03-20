# Meta-Infrastructure Version History

## v1.9.2 (2026-03-20) — Observability, Intent Capture, Dispatch Quality

- **Architecture:** Unchanged (one operator agent + skills + flow routing)
- **Root docs:** Canonicalized. README, INIT, OPERATOR_PROTOCOL, IMPLEMENTATION_PROMPT, PROTOCOL_REVIEW_PROMPT all rewritten to describe one system (v1.9.1 model)
- **Intent capture:** Project Definition Record template (frozen core + mutable clarifications). Evidence Review Packet template (event-driven learning). Spec template with frozen/mutable split and traceability.
- **Dispatch quality:** Dispatch readiness gate requires explicit user/problem/outcome/non-goals/constraints. Feature-flow Phase 0 intent check with structured questioning protocol. Dispatch status field on handoffs.
- **Observability:** Run ledger (`.agent/runs.jsonl`), incident log (`.agent/incidents.jsonl`), review scorecards (`.agent/reviews/scorecards.jsonl`). JSON schemas for all three.
- **Handoff upgrades:** Replan triggers, verification procedure, evidence required, assumptions in force, dispatch status. Handoff envelope schema v1.1.0.
- **Flow skills:** All three flows (debug, feature, refactor) upgraded with negative constraints, separate-context verification, incident logging, run records.
- **Metrics:** Four families (outcome, efficiency, cost, qualitative) + intent-quality metrics. Expanded from token profiling to full pipeline observability.
- **Review:** Three distinct review layers (task validation, experiential review, pipeline review). Protocol review requires evidence, root-cause classification, scaffold-first bias.
- **Iteration caps:** Doer/verifier max 3, review/refinement max 2. Cap breach → incident log + escalation.
- **Eval manifest:** Version lineage tracking for prompts, skills, flows, templates.
- **Builds on:** v1.9.1 (flow skills + routing)

### v1.9.2 Scores (post-migration)
| Dimension | Score | Weight | Rationale |
|---|---|---|---|
| Context Efficiency | 4 | 3x | Unchanged — skills load on demand. CLAUDE.md still ≤200 lines. |
| Session Bootstrap | 4 | 2x | Unchanged. |
| Anti-Drift | 5 | 3x | Run records, incident logs, root-cause classification, eval manifest, iteration caps, scaffold-first bias in protocol review. |
| Doc Freshness | 5 | 2x | All root docs describe one system. No architectural drift. |
| Session Hygiene | 5 | 2x | Structured telemetry (runs, incidents, scorecards). Flow phases with checkpoints. |
| Handoff Reliability | 5 | 2x | Replan triggers, verification procedure, evidence required, assumptions, dispatch status. |
| Scalability | 4 | 1x | New projects inherit all templates, schemas, and flow skills. |
| **Weighted Score** | **4.6/5.0** | | (4×3+4×2+5×3+5×2+5×2+5×2+4×1)/15 = 4.6 |

### v1.9.1 → v1.9.2 Improvement
| Dimension | v1.9.1 | v1.9.2 | Delta |
|---|---|---|---|
| Context Efficiency | 4 | 4 | — |
| Session Bootstrap | 4 | 4 | — |
| Anti-Drift | 4 | 5 | +1 |
| Doc Freshness | 4 | 5 | +1 |
| Session Hygiene | 5 | 5 | — |
| Handoff Reliability | 5 | 5 | — |
| Scalability | 4 | 4 | — |
| **Weighted Score** | **4.2** | **4.6** | **+0.4** |

---

## v1.9.1 (2026-03-20) — Task-Type Routing & Flow Skills
- **Architecture:** Task classification → flow skill routing → predefined step sequences
- **Flow skills:** debug-flow, feature-flow, refactor-flow (3 of 8 planned)
- **Routing:** Trigger table in CLAUDE.md, zero-cost classification (no separate model call)
- **Task tracking:** taskType and gateStatus fields added to structured task state
- **Metrics:** Token profiling protocol established, infrastructure/flow/gate metrics defined
- **Evals:** Flow routing and gate compliance evals added (4 eval cases)
- **Handoff schema:** taskType field added to handoff envelope (required)
- **Builds on:** v1.9 (tiered memory, progressive disclosure, structured state)
- **Migration doc:** `support/v1.9/meta-infra-v1.9.1-flow-skills.md`

### v1.9.1 Scores (post-migration)
| Dimension | Score | Weight | Rationale |
|---|---|---|---|
| Context Efficiency | 4 | 3x | Flow skills load on demand; no re-planning overhead. CLAUDE.md is 123 lines. |
| Session Bootstrap | 4 | 2x | Unchanged from v1.9 (already fast) |
| Anti-Drift | 4 | 3x | Flow gate evals + routing evals added (11 eval cases total). Gates enforce phase discipline. |
| Doc Freshness | 4 | 2x | Unchanged (keep/delete filter already applied) |
| Session Hygiene | 5 | 2x | gateStatus in tracker eliminates all session artifacts. Flow phases are the session log. |
| Handoff Reliability | 5 | 2x | taskType field + flow skill = unambiguous handoff. Receiving agent knows exact flow to load. |
| Scalability | 4 | 1x | New projects inherit flow skills automatically from portfolio level. |
| **Weighted Score** | **4.2/5.0** | | (4×3+4×2+4×3+4×2+5×2+5×2+4×1)/15 = 4.2 |

---

## v1.9 (2026-03-20) — Tiered Memory + Skills Migration
- **Architecture:** One operator agent + progressive-disclosure skills
- **Memory:** Hot/warm/cold tiering. CLAUDE.md ≤200 lines.
- **Task state:** Structured (JSONL), not markdown
- **Handoffs:** Single JSON Schema envelope, validated at runtime
- **Quality:** Eval-first anti-drift. Rules require corresponding eval cases.
- **Agent count:** ~5-7 skills (down from 8 roles × 3 projects)
- **Doc footprint:** 183 markdown files, ~2MB (down from 397 files; domain research is ~1.5MB of this)
- **Git ref:** tag v1.9, branch v1.9 after migration
- **Migration prompt:** meta-review-v1.9-migration.md

### v1.9 Scores (post-migration)
| Dimension | Score | Weight | Rationale |
|---|---|---|---|
| Context Efficiency | 4 | 3x | CLAUDE.md is 105 lines. Skills loaded on demand via trigger table. Cold-tier docs never auto-loaded. |
| Session Bootstrap | 4 | 2x | Agent reads CLAUDE.md only (105 lines), triggers skills as needed. No preamble loading. |
| Anti-Drift | 3 | 3x | Eval scaffold with 7 eval cases across conventions/handoffs/skills. JSON Schema validation for handoffs. Not yet CI-enforced. |
| Doc Freshness | 4 | 2x | Keep/delete filter applied. 214 files deleted. All remaining docs justify their existence. |
| Session Hygiene | 4 | 2x | Structured task tracker (JSONL). "Land the plane" protocol. No session file creation policy. |
| Handoff Reliability | 4 | 2x | JSON Schema envelope with validation script. Reject malformed handoffs. |
| Scalability | 4 | 1x | New project needs only project CLAUDE.md + .agent/tasks.jsonl. Inherits meta skills and schema. |
| **Weighted Score** | **3.7/5.0** | | (4×3+4×2+3×3+4×2+4×2+4×2+4×1)/15 = 3.73 |

---

## v1.8 (prior) — Role-Based Multi-Agent Architecture
- **Architecture:** 8 named agent roles with preambles and roster, duplicated across 3 projects
- **Memory:** Flat markdown, no tiering
- **Task state:** Session artifact markdown files
- **Handoffs:** Markdown templates, no validation
- **Quality:** Convention rules in preambles and CLAUDE.md, no evals
- **Agent count:** 8 roles × 3 projects (32 preamble files)
- **Doc footprint:** ~397 markdown files
- **Git ref:** tag v1.8-final, branch archive/meta-infra-v1.8

### v1.8 Scores (baseline)
| Dimension | Score | Weight | Rationale |
|---|---|---|---|
| Context Efficiency | 1 | 3x | ~20% context consumed loading infrastructure |
| Session Bootstrap | 1 | 2x | 7-line preambles × 8 roles, copy-pasted per session |
| Anti-Drift | 1 | 3x | Rules in prose only, no validation or evals |
| Doc Freshness | 2 | 2x | Large volume, much duplication, some active use |
| Session Hygiene | 1 | 2x | 11 session files for a 6-task feature |
| Handoff Reliability | 2 | 2x | Templates exist but no validation |
| Scalability | 2 | 1x | Infrastructure exists but is heavyweight to replicate |
| **Weighted Score** | **1.4/5.0** | | (1×3+1×2+1×3+2×2+1×2+2×2+2×1)/15 = 1.4 |

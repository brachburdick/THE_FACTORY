# Analysis → Action: Turning THE_FACTORY Technical Analysis Into Improvements

**Date:** 2026-03-26
**Source:** `THE_FACTORY_analysis.md` (external landscape mapping & feature breakdown)
**Status:** Proposal — awaiting operator review

---

## Purpose

The analysis document maps every THE_FACTORY feature to its AI/LLM framework equivalents, identifies what's genuinely novel, what has robust alternatives, and where unsolved problems remain. This proposal distills those findings into concrete next steps, grouped by action type.

---

## 1. Validate & Double Down (Novel Differentiators)

These are features the analysis confirmed have **no real equivalent** in the ecosystem. They deserve investment, not replacement.

### 1a. Fix-Attempt Tracker → Productize
- **Finding:** "No equivalent in any framework." The quality gate blocking edits after 2 mutations without tests addresses a real agent failure mode.
- **Action:** Migrate from custom hook to Claude Code native `PreToolUse` hook (already Priority 1 in v2.2 roadmap). Once native, write it up as a standalone pattern other Claude Code users can adopt.
- **Status:** Already tracked in v2.2 Priority 1. No new work needed — just execute.

### 1b. Section Contracts → Publish as Standalone Spec
- **Finding:** "No AI coding tool formalizes project decomposition into typed contracts with coverage enforcement." Closest analogue is formal architecture documentation, not anything in AI tooling.
- **Action:** Extract section contract format + coverage enforcement evals into a self-contained spec document. This is THE_FACTORY's most exportable idea.
- **Status:** Already tracked in v2.2 Priority 3. Add: publish the spec outside this repo (blog post, gist, or standalone repo).

### 1c. Protocol Evals → Expand Coverage
- **Finding:** "Testing that the agent follows the protocol, not just that the code is correct" is unique. No mainstream framework tests behavioral compliance.
- **Action:** Current suite is 73 tests. Add evals for:
  - Skill load correctness (did the trigger table route to the right skill?)
  - Session protocol compliance (did the agent claim a task before starting?)
  - Hook enforcement bypass attempts (does the agent try to circumvent hooks?)
- **Ties to:** v2.2 Priority 2 (CI-gate the eval suite) and Priority 8 (skill load audit).

### 1d. Single-Agent Skill Switching → Document the Bet
- **Finding:** "Opposite of the multi-agent trend; supported by Google/MIT 2024 finding that single agent + verification beats naive multi-agent."
- **Action:** No code change. Write a concise rationale document (why single-agent, what evidence, when to reconsider) for `support/`. This anchors the architectural decision so future sessions don't second-guess it.

---

## 2. Replace with Better Alternatives (Redundant Custom Tooling)

These features have mature open-source alternatives that do the job better. The analysis confirms the v2.2 roadmap's instincts.

### 2a. Experiment Framework → Promptfoo
- **Finding:** `scripts/experiment.py` and `scripts/assess.py` compete against Promptfoo (matrix testing, red teaming, CI integration).
- **Action:** Already v2.2 Priority 4. Port experiment configs to Promptfoo YAML, delete custom scripts.
- **Risk:** Promptfoo may not natively support the "run Claude Code session as a test case" pattern. May need a thin adapter.

### 2b. Token Dashboard → Langfuse
- **Finding:** Custom `scripts/token-dashboard.py` is redundant with existing Langfuse integration.
- **Action:** Already v2.2 Priority 5. Ensure Langfuse trace hook captures session-level burn rate and context fill metrics before deleting.

### 2c. Custom Hook Infrastructure → Native Hooks
- **Finding:** Claude Code's 21 native lifecycle events now cover all THE_FACTORY hook use cases.
- **Action:** Already v2.2 Priority 1. This is the highest-priority migration.

---

## 3. New Actions Surfaced by the Analysis (Not in v2.2 Roadmap)

These are findings from the analysis that **aren't already tracked**.

### 3a. Context Checkpointing Research
- **Finding:** "The context checkpointing problem is unsolved across the entire ecosystem." LangGraph checkpoints graph state, not what the agent learned by reading files. THE_FACTORY's own PROTOCOL_IMPROVEMENTS.md flags this.
- **Action:** Open a research track. Prototype a lightweight "session knowledge" capture — not full reasoning state, but a structured summary of: files read, decisions made, hypotheses formed, dead ends hit. Write to `.agent/session-knowledge/` at session end. This is exploratory, not production.
- **Priority:** Low urgency, high value. Worth a brainstorm session.

### 3b. Trigger Table Failure Logging
- **Finding:** The analysis notes the trigger table is "dead simple and requires zero infrastructure" but "doesn't scale to hundreds of knowledge sources and requires manual curation." The v2.2 roadmap has LLM fallback (Priority 6) but not the prerequisite: **logging unmatched inputs**.
- **Action:** Before building LLM fallback, instrument the trigger table to log every input that fails to match. Accumulate a dataset of misses to inform whether LLM fallback is worth the complexity or if the table just needs more keywords.
- **Priority:** Quick win. Add a hook or skill annotation that logs unmatched trigger attempts to `.agent/trigger-misses.jsonl`.

### 3c. Build System Integration for API Verification
- **Finding:** "Specs reference APIs from web documentation, but no step confirms they compile against the actual dependency version on disk."
- **Action:** For projects with typed languages or typed Python (SCUE uses Python with type hints), add an eval that checks: do the APIs referenced in spec/contract files actually exist in the installed dependencies? This prevents specs from drifting from reality.
- **Priority:** Medium. Only relevant for projects with specs that reference external APIs.

### 3d. Architecture Decision Record for File-Based Coordination
- **Finding:** "The entire industry moved away from [file-based coordination] toward runtime orchestration; THE_FACTORY bets the opposite direction."
- **Action:** Write an ADR documenting *why* file-based coordination was chosen, what its limits are, and what would trigger a move to runtime orchestration. Store in `support/adrs/`.
- **Priority:** Low. Documentation, not code.

---

## 4. Explicitly Decline (Not Worth Pursuing)

### 4a. Multi-Agent Orchestration
- **Finding:** Analysis confirms the single-agent bet is sound. Multi-agent adds complexity without proven benefit at THE_FACTORY's scale.
- **Decision:** Do not adopt LangGraph/CrewAI multi-agent patterns. Revisit only if task complexity exceeds single-agent capacity with measurable evidence.

### 4b. Vector DB / Embedding-Based Retrieval
- **Finding:** Trigger table's keyword matching is "much simpler, much more predictable, and zero infrastructure."
- **Decision:** Do not add embedding-based skill retrieval. The portfolio has <20 skills — keyword matching is sufficient. Log misses (3b) to validate this assumption.

### 4c. Managed Memory Services (Mem0, AWS Memory)
- **Finding:** `.agent/` state files work at current scale.
- **Decision:** Stay with file-based state. Move to SQLite (v2.2 Priority 7) only when corruption or concurrency issues appear.

---

## Summary: What's New vs. Already Tracked

| Action | New? | v2.2 Priority |
|---|---|---|
| Fix-attempt tracker → native hook | No | P1 |
| Section contracts → standalone spec | Partially (add: publish externally) | P3 |
| Protocol evals → expand coverage | Partially (add: 3 new eval categories) | P2, P8 |
| Single-agent rationale doc | **Yes** | — |
| Experiment → Promptfoo | No | P4 |
| Dashboard → Langfuse | No | P5 |
| Hooks → native | No | P1 |
| Context checkpointing research | **Yes** | — |
| Trigger table miss logging | **Yes** (prerequisite for P6) | — |
| API verification eval | **Yes** | — |
| File-based coordination ADR | **Yes** | — |

**Net new items: 5.** The analysis largely validates the existing v2.2 roadmap and adds a research track (context checkpointing), an instrumentation prerequisite (trigger miss logging), a verification eval (API references), and two documentation items (single-agent rationale, file-coordination ADR).

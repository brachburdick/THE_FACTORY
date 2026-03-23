# THE_FACTORY v2.0 — Unified Migration Plan

**Last updated:** 2026-03-23
**Status:** Phase 0 (Conversation Mining) complete. Ready for execution.
**Inputs synthesized:** v1.10 plans, conversation mining (20 sessions × 3 lenses), second opinion on existing tools, SYNTROPY findings, PROTOCOL_IMPROVEMENTS.md (30+ observations)

---

## What v2 Is

THE_FACTORY is simultaneously a coding-agent runtime, a workflow/state system, a skill/prompt system, an observability/eval layer, and a self-improvement protocol. v2 stops reinventing the layers that mature ecosystems already cover, and doubles down on the parts that are actually ours.

**Keep custom:** Project-definition artifacts, operator decision boundaries, flow routing, skills system, portfolio scaffolding, improvement rubrics specific to how we work.

**Stop owning:** Tracing/evals (→ Langfuse + DeepEval/Promptfoo), enforcement (→ Claude Code hooks), orchestration semantics (→ Claude Code subagents, optionally LangGraph later), trace format (→ OpenTelemetry GenAI spans).

The end state is an **agent experimentation platform**: define tasks, run agent variants, score results, compare, improve. CRUCIBLE provides sandboxed execution. Inspect provides the experiment framework. Langfuse provides observability. Claude Code provides the daily-driver shell.

---

## Evidence Base (Phase 0 Results)

Before designing the migration, we mined 20 sessions (148 extracted total) with three parallel lens agents. Full results: `support/v2/conversation-mining-results.md`.

### Baselines to beat

| Metric | Current | Target |
|---|---|---|
| Overall waste (tokens/tool calls) | ~25% | <10% |
| Bug catch rate (in-session) | 75% (12/16) | >90% |
| Reads before first Edit (ramp-up) | 15-30 | <5 |
| Pre-existing test failures carried | 2+ across 3+ sessions | 0 |
| API misuse bugs per 20 sessions | 7 | <2 |

### Top 5 empirical problems (cross-lens)

1. **No persistent state between sessions** — 10% ramp-up tax + 1500 wasted tool calls re-exploring SCUE
2. **API misuse from missing reference docs** — #1 bug type (7 instances), beat-link API repeatedly researched
3. **Normalized test failures** — broken tests carried across sessions, layer1 tests skipped entirely
4. **Redundant subagent exploration** — up to 29 subagents reading overlapping files, 8% token waste
5. **Cold-tier docs don't prevent bugs** — ADR-018 anti-pattern re-introduced despite being documented

### Efficiency wins to preserve

- Parallel subagent research for independent domains (2x throughput when scopes don't overlap)
- Feature-flow skill structure (5-12% waste vs 15-25% unstructured)
- Greenfield generative sessions (~5% waste — spec in, code out)

---

## Architecture: Three Layers

```
┌─────────────────────────────────────────────────────────┐
│                   EXPERIMENT LAYER                       │
│  Inspect tasks + solvers + scorers                      │
│  "What to test and how to score it"                     │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐               │
│  │  Tasks   │  │ Variants │  │ Scorers │               │
│  │ (specs)  │  │ (configs)│  │ (evals) │               │
│  └─────────┘  └──────────┘  └─────────┘               │
├─────────────────────────────────────────────────────────┤
│                   EXECUTION LAYER                        │
│  CRUCIBLE sandbox + Claude Code + hooks                 │
│  "Run the agent safely and observe it"                  │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐               │
│  │CRUCIBLE  │  │  Claude   │  │  Hooks  │               │
│  │(sandbox) │  │  Code     │  │ (guard) │               │
│  └─────────┘  └──────────┘  └─────────┘               │
├─────────────────────────────────────────────────────────┤
│                 OBSERVABILITY LAYER                      │
│  Langfuse traces + DeepEval scores                      │
│  "What happened and how good was it"                    │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐               │
│  │Langfuse  │  │ DeepEval │  │ Inspect │               │
│  │(traces)  │  │ (scores) │  │  View   │               │
│  └─────────┘  └──────────┘  └─────────┘               │
└─────────────────────────────────────────────────────────┘
```

**How they connect:**
- **Inspect** defines what to test (task) and how to score (scorer). It calls into the execution layer.
- **CRUCIBLE** runs agents in E2B sandboxes for automated experiments. Claude Code runs agents interactively for daily work. Both are execution environments.
- **Langfuse** captures traces from both CRUCIBLE and Claude Code (via Stop hook). DeepEval scores those traces.
- **Inspect View** shows experiment comparisons. Langfuse dashboards show ongoing telemetry.

---

## Migration Phases

### Phase 0: Conversation Mining ✅ COMPLETE

Mined 20 most substantive sessions with three parallel lens agents (Process Efficiency, Quality & Correctness, Learning & Knowledge). Produced ranked improvement list and baselines.

**Output:** `support/v2/conversation-mining-results.md`

### Phase 1: Observability Foundation + Quick Wins
> Get real telemetry flowing. Fix the highest-impact problems from mining.

**1a. Langfuse setup**
- Stand up locally (Docker) or use cloud free tier
- Feed the 20 mined sessions as a historical baseline dataset

**1b. Claude Code hooks**
- **Stop hook → Langfuse trace:** Auto-trace every session
- **Stop hook → state snapshot:** Write `.agent/state-snapshot.json` (branch, last commit, active tasks, flow phase, key files modified, blockers) — addresses mining finding #1
- **Stop hook → land-the-plane:** Enforce task state update, feature-completion status update
- **PreToolUse hook → git guard:** Enforce branch/commit/push rules
- **PreToolUse hook → zero-failures gate:** Block `git commit` if `pytest` exit code ≠ 0 — addresses mining finding #3

**1c. Quick knowledge wins (from mining)**
- Create `scue/skills/codebase-orientation.md` — file-to-responsibility map, data flow chains, feature status, key gotchas — addresses mining finding #1 (1500 wasted tool calls)
- Augment `skills/beat-link-bridge.md` and `skills/pioneer-hardware.md` with API reference details (CdjStatus return types/units, Finder start order, XDJ-AZ quirks, pyrekordbox gotchas) — addresses mining finding #2 (7 API misuse bugs)
- Fix layer1 test env (numpy) so analysis pipeline tests actually run — addresses mining finding #3
- Fix or skip the 2 TestBatchJobLifecycle failures with tracked issue

**1d. Subagent guidance**
- Add to flow skills: when launching parallel Explore subagents, give each a specific file scope. No overlapping directories. — addresses mining finding #4

**Exit criteria:**
- Every Claude Code session appears in Langfuse automatically
- Git violations blocked by hook
- `pytest` must exit 0 before commit
- Session-start reads before first Edit < 5 (currently 15-30)
- State snapshot written at every session end

**Effort:** 3-4 sessions.

### Phase 2: Eval Infrastructure
> Replace markdown aspirations with real tests.

1. **DeepEval setup**: `pip install deepeval`, create `evals/` directory
2. **Migrate convention evals** (6 cases): BaseMetric, grep-based, deterministic
3. **Migrate flow evals** (4 cases): GEval with Claude-as-judge
4. **Migrate handoff/skill evals** (3 cases): mix of BaseMetric and GEval
5. **Create eval cases for top 5 mining findings:**
   - API misuse regression check (does the agent use documented APIs correctly?)
   - Ramp-up efficiency (reads before first edit)
   - Test suite health (zero pre-existing failures)
   - Subagent scope overlap detection
   - Feature-completion status accuracy
6. **Wire to Langfuse**: Pull real session traces as test inputs

**Exit criteria:** `deepeval test run evals/` passes all ~18 cases. Top failure patterns have regression tests.

**Effort:** 2-3 sessions.

### Phase 3: Slim the Constitution
> Delete everything now enforced by hooks or scored by DeepEval.

1. **Rewrite CLAUDE.md** → ~50 lines (trigger table, flow routing, pointers)
2. **Delete** governance docs now enforced by hooks/evals
3. **Extract PROTOCOL_IMPROVEMENTS.md proposals** to `support/proposals/` — trim to just observation log
4. **Archive `forge/`** → `support/forge-v1-archive/`
5. **Add subagent dedup guidance** to flow skills (from mining finding #4)

**Exit criteria:** Constitution is lean. Nothing in CLAUDE.md that a hook or eval already enforces.

**Effort:** 1 session.

### Phase 4: Experiment Framework
> The new capability. Build the variant comparison system.

1. **Install Inspect**: `pip install inspect-ai`
2. **Define task format**: YAML task definitions with description, acceptance criteria, test commands, scoring rubric
3. **Create first scorers**:
   - Test pass rate (deterministic)
   - Code quality (GEval with Claude-as-judge)
   - Token efficiency (tokens per completed task)
   - Ramp-up efficiency (reads before first edit — from mining baseline)
   - Wall time
4. **Write CRUCIBLE solver**: Inspect solver wrapping sandbox runner
5. **Write Claude Code solver**: Inspect solver that runs Claude Code headless or via API with SKILL.md as system prompt
6. **Define 3 starter variants**: baseline (current skills), minimal (bare prompt), one alternative (swarm or different model)
7. **Run first experiment**: Pick a real task. Run all 3 variants. Compare in Inspect View.
8. **Build `scripts/experiment.py`**: Batch runner for variant comparison

**Exit criteria:** You can answer: "does the skill system produce better results than a bare prompt? By how much? At what cost?"

**Effort:** 3-4 sessions.

### Phase 5: Improvement Loop
> Close the optimization flywheel. Merges v1.10 improvement-flywheel concept with experiment framework.

1. **Build `scripts/assess.py`**: Pull Langfuse traces → score with DeepEval → identify low scorers → generate improvement candidates → present [ACCEPT/DEFER/REJECT]
2. **Create Langfuse datasets**: Tag traces by project, task type, outcome for ongoing evaluation
3. **Validate**: Run on 10 real sessions, verify it catches known issues from mining
4. **Wire to experiments**: Accepted SKILL.md changes become new variants tested against baseline
5. **Re-measure baselines**: Compare post-migration metrics against Phase 0 baselines (25% waste, 75% catch rate, etc.)

**Exit criteria:** `python scripts/assess.py --last 20` produces actionable candidates. Accepted changes are validated by re-running experiments. Improvement loop is closed.

**Effort:** 2-3 sessions.

### Phase 6: Cleanup
> Remove dead infrastructure only after new system is proven.

1. Archive `runs.jsonl`, `incidents.jsonl`, `conversations/`
2. Remove old schemas (keep handoff envelope)
3. Remove `scripts/extract-conversations.py`
4. Update VERSION.md, workspace layout
5. Write v2.0 CLAUDE.md

**Effort:** 1 session.

---

## Three Intensity Options

The phases above are the **medium path**. Here's how conservative and aggressive differ:

### Conservative (Phases 0-3 only) — 7-10 sessions

Do the mining, get observability + hooks + evals, slim the constitution. Skip the experiment framework.

**You get:** Real telemetry, deterministic enforcement, the quick wins from mining (codebase orientation, API docs, zero-failures gate). You stop flying blind.

**You don't get:** Quantified skill value, automated improvement loop, variant comparison.

**Best if:** You mainly want to stop reinventing enforcement and fix the top 5 problems.

### Medium (All 6 phases) — 12-16 sessions

Everything above plus the experiment framework and improvement loop.

**You get:** An experimentation platform. Evidence-based improvement. Closed optimization loop.

**Best if:** You want to quantify skill value and automate the assess→improve→verify cycle.

### Aggressive (Medium + replatform orchestration) — 18-24 sessions

After Phase 5, add:
- Phase 7A: Rewrite flow skills as LangGraph graphs with checkpoints and interrupts
- Phase 7B: Move task state from JSONL to LangGraph persisted state
- Phase 7C: Human approval gates become LangGraph interrupts

THE_FACTORY becomes a thin methodology layer on LangGraph + Inspect + Langfuse.

**You get:** Durable execution, pause/resume, real orchestration runtime.

**You don't get:** Your weekends back. Highest rewrite cost. Risk of two control planes during migration.

**Best if:** You want THE_FACTORY to stop being a runtime entirely and become a methodology layer.

---

## What the Migrated System Looks Like Day-to-Day

### Building software (non-experiment mode)

```
You open Claude Code in a project directory.

What happens automatically (via hooks):
  → State snapshot loaded from previous session (< 5 reads to context)
  → Langfuse traces every session
  → Git protocol enforced
  → pytest must pass before commit

What you do:
  → Work normally with Claude Code
  → Skills load on-demand via trigger table (unchanged)
  → Flow routing classifies your task (unchanged)
  → Codebase orientation skill loads for SCUE work (new)

What you get:
  → Real telemetry in Langfuse (not self-reported JSON)
  → 75% less ramp-up time per session
  → Zero normalized test failures
  → API misuse prevented by reference docs in skills
```

### Assessing pipeline performance

```
$ python scripts/assess.py --last 20

  1. Pulls last 20 session traces from Langfuse
  2. Scores with DeepEval (flow compliance, conventions, efficiency, ramp-up)
  3. Compares against Phase 0 baselines
  4. Identifies low scorers, generates improvement candidates
  5. Presents [ACCEPT] [DEFER] [REJECT] for each
  6. Accepted changes → new eval case + SKILL.md diff
  7. Re-runs evals to verify
```

### Running experiments

```
$ python scripts/experiment.py \
    --task tasks/build-rest-api.yaml \
    --variants variants/*.yaml \
    --runs-per-variant 3

  → Runs each variant in CRUCIBLE sandboxes
  → Scores with Inspect scorers
  → Comparison table: pass rate, tokens, cost, time
  → Answer: "skills improve pass rate by X% at Y cost premium"
```

---

## CRUCIBLE in v2

CRUCIBLE's unique value — E2B sandboxing, semantic loop detection, token budget middleware, convergent teardown — stays. It gains a new role as an Inspect solver:

```python
# solvers/crucible_solver.py
from inspect_ai.solver import solver, TaskState
from crucible import run_in_sandbox

@solver
def crucible(variant: str, budget: int = 100000, ttl: int = 300):
    async def solve(state: TaskState) -> TaskState:
        result = await run_in_sandbox(
            task=state.input_text, variant=variant,
            budget=budget, ttl=ttl
        )
        state.output = result.artifacts
        state.metadata["crucible_result"] = result
        return state
    return solve
```

---

## Variant System

A "variant" is everything that makes one agent run different from another:

```yaml
# variants/baseline.yaml
name: baseline
model: claude-sonnet-4-20250514
system_prompt: skills/debug-flow/SKILL.md
tools: [bash, file_editor, web_search]
orchestration: single-agent
budget: 100000
ttl: 300

# variants/minimal.yaml
name: minimal
model: claude-sonnet-4-20250514
system_prompt: "You are a software engineer. Complete the task."
tools: [bash, file_editor]
orchestration: single-agent
budget: 100000
ttl: 300

# variants/swarm.yaml
name: swarm
model: claude-sonnet-4-20250514
system_prompt: skills/debug-flow/SKILL.md
tools: [bash, file_editor]
orchestration: agent-teams
team_size: 3
budget: 300000
ttl: 600
```

---

## Tool Stack

| Tool | Role | Cost |
|---|---|---|
| **Inspect** | Experiment framework (tasks, solvers, scorers, comparison UI) | Free (OSS) |
| **Langfuse** | Observability (traces, costs, dashboards) | Free (OSS/cloud free tier) |
| **DeepEval** | Eval framework (convention checks, LLM-as-judge) | Free (OSS core) |
| **CRUCIBLE** | Sandboxed execution (E2B, kill switches) | E2B usage fees |
| **Claude Code** | Daily-driver shell (hooks, skills, subagents, MCP) | Subscription |

All open source or free tier. No vendor lock-in. Self-hostable.

---

## Post-Migration Workspace

```
THE_FACTORY/
├── CLAUDE.md                  ← ~50 lines (trigger table, flow routing)
├── .claude/
│   ├── hooks/                 ← deterministic enforcement
│   │   ├── git-guard.sh
│   │   ├── land-the-plane.sh
│   │   ├── zero-failures.sh
│   │   └── langfuse_hook.py
│   ├── settings.json
│   └── skills/
│       ├── debug-flow/
│       ├── feature-flow/
│       └── refactor-flow/
├── .agent/
│   ├── tasks.jsonl            ← work queue
│   ├── state-snapshot.json    ← session-to-session continuity (NEW)
│   └── schemas/
│       └── handoff-envelope.schema.json
├── tasks/                     ← Inspect task definitions
├── variants/                  ← agent configurations to compare
├── scorers/                   ← Inspect/DeepEval scoring functions
├── solvers/                   ← Inspect solver wrappers
├── evals/                     ← DeepEval test suite
├── scripts/
│   ├── tasks.sh
│   ├── experiment.py          ← batch variant comparison
│   └── assess.py              ← improvement loop
├── skills/                    ← portfolio-level skills
├── projects/                  ← CRUCIBLE, SCUE, Tinyshop
├── templates/                 ← 4 templates
└── support/
    ├── v2/
    │   └── conversation-mining-results.md  ← Phase 0 output
    └── ...                    ← archives
```

---

## Deferred Items

### SYNTROPY Integration
The decomposition framework has a 15:1 theory-to-experiment ratio. The actionable takeaway — "decompose by decisions, not steps; verify externally" — is already reflected in how flow skills work. If we later want to formalize decomposition quality as a scorer, SYNTROPY's Phases 0-2 (Classify, Identify Decisions, Define Interfaces) become scorer dimensions in the experiment framework. That's the natural integration point, but it's not blocking.

### DrawDown (Visual Diagram Editor)
Separate app, not a migration dependency. Build when visualization is needed, not as part of restructuring.

### LangGraph Orchestration (Aggressive Path)
Only pursue if orchestration/state complexity remains painful after Phases 1-5. The conservative and medium paths may be sufficient.

### v1.10 Multi-Model Assessment with Bias Mitigation
The elaborate position-swap, independent-scoring rubric system from `support/v1.10/` is absorbed into `scripts/assess.py` in a simpler form. The bias mitigation machinery (position-swap tiebreaker, preserved disagreements) is deferred until there's evidence that single-model assessment produces unreliable results.

---

## Estimated Total Effort

| Phase | Sessions | Blocking? | Key Deliverable |
|---|---|---|---|
| 0: Conversation Mining | ✅ done | — | Baselines + ranked improvements |
| 1: Observability + Quick Wins | 3-4 | Yes | Hooks, Langfuse, codebase orientation, API docs, zero-failures |
| 2: Eval Infrastructure | 2-3 | No | 18 eval cases wired to Langfuse traces |
| 3: Slim Constitution | 1 | No | ~50-line CLAUDE.md |
| 4: Experiment Framework | 3-4 | No (highest value) | Variant comparison system |
| 5: Improvement Loop | 2-3 | No | assess.py + closed flywheel |
| 6: Cleanup | 1 | No | Archive dead infra |
| **Total** | **12-16** | | |

Start with Phase 1 because everything else depends on having real telemetry and the quick wins address 75% of the waste identified in mining.

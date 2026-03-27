# THE_FACTORY v3.0 — System Diagram

## Level 0: The Big Picture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           YOU (The Operator)                                │
│                                                                             │
│  "Fix this bug"    "Build X feature"    "Refactor Y"    "How's the pipeline?"│
└──────────┬──────────────────┬─────────────────┬──────────────────┬──────────┘
           │                  │                 │                  │
           ▼                  ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLAUDE CODE SESSION                                  │
│                        (The Agent / Operator)                               │
│                                                                             │
│  ┌─────────┐  ┌──────────────┐  ┌─────────────┐  ┌───────────────────────┐ │
│  │CLAUDE.md│  │ Flow Skills  │  │   Hooks      │  │  .agent/ State        │ │
│  │(Const.) │  │ (Behavior)   │  │ (Guardrails) │  │  (Memory + Records)   │ │
│  └─────────┘  └──────────────┘  └─────────────┘  └───────────────────────┘ │
└──────────┬──────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROJECT REPOS                                       │
│     SCUE/        Tinyshop/       PABProject/        CRUCIBLE/              │
│  (own git)      (own git)        (own git)          (own git)              │
│  own CLAUDE.md  own CLAUDE.md    own CLAUDE.md      own CLAUDE.md          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key insight:** THE_FACTORY is the *process* repo. It never contains project source code.
Projects live under `projects/`, each with their own git repo. THE_FACTORY defines
*how* work happens. Projects define *what* gets built.

---

## Level 1: Session Lifecycle (How a Single Work Session Flows)

```
┌──────────────────────── SESSION START ────────────────────────┐
│                                                               │
│  1. Load CLAUDE.md (constitution)                             │
│  2. Read .agent/state-snapshot.json (prior session context)   │
│  3. Read .agent/tasks.jsonl (find pending work)               │
│  4. Read LEARNINGS.md (env constraints)                       │
│  5. Claim a task (set status: "in_progress")                  │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   CLASSIFY THE TASK   │
                │                       │
                │  fix/bug → debug-flow │
                │  add/new → feature-flow│
                │  refactor → refactor-flow│
                └───────────┬───────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │         FLOW EXECUTION               │
         │                                      │
         │  Pre-flight checks ──────────────┐   │
         │  ↓                               │   │
         │  Phase work (varies by flow)     │   │
         │  ↓                               │   │
         │  ◄── Hooks fire on every Edit ──►│   │
         │  ↓                               │   │
         │  Close: run record + commit      │   │
         └──────────────┬───────────────────┘
                        │
                        ▼
┌──────────────────────── SESSION END ─────────────────────────┐
│                                                              │
│  (Automatic via hooks:)                                      │
│  • state-snapshot.py → writes state-snapshot.json            │
│  • audit-run-record.sh → warns if no run record written      │
│  • langfuse-trace.py → sends metrics (if configured)         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Level 2: The Hook System (Automated Guardrails)

Hooks are shell scripts that fire **automatically** before/after tool use.
You don't call them. They intercept the agent's actions and enforce constraints.

```
  Agent tries to Edit a file
         │
         ▼
┌─────────────────────────── PreToolUse: Edit ─────────────────────────────┐
│                                                                          │
│  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────────┐ │
│  │ risk-classifier  │   │   blast-radius   │   │ fix-attempt-tracker  │ │
│  │                  │   │                  │   │                      │ │
│  │ Is this task     │   │ Is this file     │   │ Has the agent made   │ │
│  │ high-risk?       │   │ inside the       │   │ >2 edits without     │ │
│  │ Need a plan?     │   │ task's owned     │   │ running tests?       │ │
│  │                  │   │ paths?           │   │ Hit 10 total?        │ │
│  │ BLOCK if high    │   │                  │   │ 4 cycles? 10 files?  │ │
│  │ + no plan        │   │ BLOCK if out     │   │                      │ │
│  └──────────────────┘   │ of scope         │   │ BLOCK if exceeded    │ │
│                         └──────────────────┘   └──────────────────────┘ │
│                                                                          │
│  ┌──────────────────┐   ┌──────────────────┐                            │
│  │    plan-gate     │   │ build-integrity  │                            │
│  │                  │   │                  │                            │
│  │ High-risk task   │   │ Editing hooks,   │                            │
│  │ editing source?  │   │ CI, settings?    │                            │
│  │ Plan approved?   │   │                  │                            │
│  │                  │   │ WARN (not block) │                            │
│  │ BLOCK if no plan │   └──────────────────┘                            │
│  └──────────────────┘                                                    │
│                                                                          │
│  All pass? ──► Edit proceeds                                             │
│  Any BLOCK? ──► Edit rejected, agent must adjust                         │
└──────────────────────────────────────────────────────────────────────────┘


  Agent tries to use Bash
         │
         ▼
┌──────────── PreToolUse: Bash ─────────────┐
│  ┌──────────────────┐  ┌────────────────┐ │
│  │    git-guard     │  │ fix-attempt-   │ │
│  │                  │  │ tracker        │ │
│  │ No commits to    │  │                │ │
│  │ main, no force   │  │ (same budget   │ │
│  │ push, no reset   │  │  checks)       │ │
│  │ --hard           │  │                │ │
│  └──────────────────┘  └────────────────┘ │
└───────────────────────────────────────────┘


  Session ends
         │
         ▼
┌────────────── SessionEnd ─────────────────┐
│  state-snapshot.py → persists context     │
└───────────────────────────────────────────┘

  Agent stops (or user stops it)
         │
         ▼
┌────────────────── Stop ───────────────────┐
│  langfuse-trace.py → metrics to Langfuse  │
│  audit-run-record.sh → warn if no record  │
└───────────────────────────────────────────┘
```

---

## Level 3: The Three Control Loops

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  OUTER LOOP (Days/Weeks) — You drive this                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  python scripts/assess.py --last 20                              │  │
│  │       │                                                           │  │
│  │       ▼                                                           │  │
│  │  Review trends: waste%, success rate, interventions               │  │
│  │       │                                                           │  │
│  │       ▼                                                           │  │
│  │  Tune thresholds: bump hook budgets, adjust baselines             │  │
│  │       │                                                           │  │
│  │       ▼                                                           │  │
│  │  File new tasks in .agent/tasks.jsonl for pipeline improvements   │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  MIDDLE LOOP (Minutes) — Agent + You at checkpoints                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │  ┌────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐     │  │
│  │  │ Spec / │───►│   Plan   │───►│ Implement │───►│ Verify  │     │  │
│  │  │ Intent │    │ (if high │    │           │    │         │     │  │
│  │  │        │    │  risk)   │    │           │    │         │     │  │
│  │  └────┬───┘    └────┬─────┘    └───────────┘    └─────────┘     │  │
│  │       │             │                                            │  │
│  │    YOU CONFIRM   YOU APPROVE                                     │  │
│  │    intent        plan                                            │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  INNER LOOP (Seconds) — Fully automated, hooks enforce                 │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │       ┌──────┐                                                    │  │
│  │       │ Edit │◄─────────────────────────┐                        │  │
│  │       └──┬───┘                          │                        │  │
│  │          │ hooks fire                   │                        │  │
│  │          ▼                              │                        │  │
│  │       ┌──────┐    pass ──► continue     │                        │  │
│  │       │ Test │                          │                        │  │
│  │       └──┬───┘    fail ──► fix ─────────┘                        │  │
│  │          │                                                        │  │
│  │       Budget exceeded? ──► STOP. Run tests or escalate.          │  │
│  │       4 cycles? ──► STOP. Something is wrong.                    │  │
│  │       10 files? ──► STOP. Scope creep.                           │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Level 4: Your Interaction Points (Where You Plug In)

### At THE_FACTORY Level (Pipeline / Process)

```
┌─────────────────────────────────────────────────────────────────┐
│                   THINGS YOU DO                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CREATE WORK                                                    │
│  ├── Add tasks to .agent/tasks.jsonl                           │
│  ├── Set risk level (low/medium/high)                          │
│  └── Set priority, project, and description                    │
│                                                                 │
│  REVIEW PIPELINE HEALTH                                         │
│  ├── python scripts/assess.py --last 20                        │
│  ├── python scripts/token-dashboard.py --last 30               │
│  ├── Read .agent/runs.jsonl for session outcomes                │
│  └── Read .agent/incidents.jsonl for problems                  │
│                                                                 │
│  TUNE THE SYSTEM                                                │
│  ├── Edit hook thresholds (budgets, cycle limits)              │
│  ├── Update CLAUDE.md (constitution changes)                   │
│  ├── Add/modify skills in .claude/skills/                      │
│  └── Add evals in evals/ to encode repeated failures           │
│                                                                 │
│  RESPOND TO AGENT                                               │
│  ├── Approve/reject specs (feature-flow Phase 0)               │
│  ├── Approve/reject plans (high-risk tasks)                    │
│  ├── Answer escalation questions (2-attempt cap hit)           │
│  └── Unblock tasks (provide missing info)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### At the Project Level (Building Software)

```
┌─────────────────────────────────────────────────────────────────┐
│          HOW A PROJECT SESSION WORKS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. You open Claude Code in THE_FACTORY directory               │
│  2. CLAUDE.md loads → agent knows all rules                     │
│  3. Agent reads tasks.jsonl → picks a task for your project     │
│  4. Agent cd's into projects/YourProject/                       │
│  5. Agent loads project's own CLAUDE.md for project context     │
│  6. Agent classifies task → loads appropriate flow skill        │
│                                                                 │
│  DURING THE SESSION:                                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Agent works autonomously                │       │
│  │                                                      │       │
│  │  • Reads code, runs tests, makes edits              │       │
│  │  • Hooks silently enforce guardrails                │       │
│  │  • Agent stays within owned_paths (blast radius)    │       │
│  │  • Budget tracker counts mutations                  │       │
│  │                                                      │       │
│  │         ┌─────────────────────────┐                 │       │
│  │         │  AGENT PAUSES WHEN:    │                 │       │
│  │         │                        │                 │       │
│  │         │  • Spec needs approval │ ◄── You confirm │       │
│  │         │  • Plan needs approval │ ◄── You confirm │       │
│  │         │  • 2 attempts failed   │ ◄── You guide   │       │
│  │         │  • Missing info        │ ◄── You provide │       │
│  │         │  • Ambiguous request   │ ◄── You clarify │       │
│  │         └─────────────────────────┘                 │       │
│  │                                                      │       │
│  │  Agent closes: run record, commit, update task      │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                 │
│  SESSION ENDS → state snapshot auto-saved → next session        │
│  can resume exactly where this one left off                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Level 5: The Automation Spectrum

```
FULLY AUTOMATIC ◄──────────────────────────────────────► FULLY MANUAL

  Hooks fire           Flow skills          You approve        You drive
  on every             guide phases         specs & plans      assess.py
  Edit/Write/Bash      and close            at checkpoints     and tuning

  ┌────────────────┬──────────────────┬───────────────────┬──────────────┐
  │                │                  │                   │              │
  │  git-guard     │  Pre-flight      │  Feature spec     │  Pipeline    │
  │  fix-tracker   │  checks          │  confirmation     │  assessment  │
  │  blast-radius  │  Context gate    │                   │              │
  │  risk-class.   │  Close protocol  │  High-risk plan   │  Threshold   │
  │  build-integ.  │  Run records     │  approval         │  tuning      │
  │  state-snapshot│  Subagent policy │                   │              │
  │  audit-record  │                  │  Escalation       │  New evals   │
  │  langfuse      │                  │  response         │              │
  │                │                  │                   │  Task queue   │
  │  HOOKS         │  SKILLS          │  YOUR CHECKPOINTS │  YOUR TOOLS  │
  └────────────────┴──────────────────┴───────────────────┴──────────────┘

  Zero effort from you                                    This is your job
  (set-and-forget)                                        (the human loop)
```

---

## Level 6: Data Flow Between Sessions

```
  Session N                          Session N+1
  ┌───────────┐                      ┌───────────┐
  │           │                      │           │
  │  Work     │                      │  Reads:   │
  │  happens  │──── persists ───────►│           │
  │           │                      │  state-   │
  │           │  state-snapshot.json  │  snapshot  │
  │  Writes:  │  tasks.jsonl         │  tasks     │
  │  run      │  runs.jsonl          │  runs      │
  │  record   │  incidents.jsonl     │  LEARNINGS │
  │           │  LEARNINGS.md        │           │
  │           │  session-knowledge   │  Picks up  │
  └───────────┘                      │  where N   │
                                     │  left off  │
       ┌──────────────────┐          └───────────┘
       │                  │
       │  assess.py reads │
       │  runs.jsonl and  │◄──── You run this periodically
       │  scores trends   │      to see how the pipeline
       │                  │      is performing
       └──────────────────┘
```

---

## Quick Reference: What To Do When

| You want to... | Do this |
|---|---|
| **Add work** | Append to `.agent/tasks.jsonl` with id, summary, risk, project |
| **Start a session** | Open Claude Code in THE_FACTORY. Agent picks up from state-snapshot |
| **Guide mid-session** | Respond when agent asks (spec approval, plan approval, escalation) |
| **Check progress** | Read `.agent/runs.jsonl` or `python scripts/assess.py --last 20` |
| **See token costs** | `python scripts/token-dashboard.py --last 30` then open the HTML |
| **Tighten guardrails** | Edit hook scripts in `.claude/hooks/` (thresholds, budgets) |
| **Add a new rule** | If deterministic → hook. If behavioral → skill. If test → eval |
| **Fix recurring failure** | Write an eval in `evals/` so it never regresses |
| **Change process** | Edit `CLAUDE.md` (it's the constitution — agent reads it first) |
| **Add project** | `mkdir projects/NewProject && cd projects/NewProject && git init` |
| **Review pipeline** | `python scripts/assess.py --last 20` → look at waste%, success rate |

# Task Execution Flowchart

What happens from the moment a task is picked up to completion.

```
                    ┌──────────────────────┐
                    │   YOU: "Execute this  │
                    │   task" / Agent picks │
                    │   from ready.py      │
                    └──────────┬───────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │  1. CLAIM TASK               │
                │                              │
                │  Set status → "in_progress"  │
                │  in .agent/tasks.jsonl       │
                │                              │
                │  Check task fields:          │
                │    risk: low/medium/high      │
                │    project: which repo?       │
                │    section: blast radius scope│
                │    blocked_by: all complete?  │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │  2. LOAD CONTEXT             │
                │                              │
                │  state-snapshot.json          │
                │    └─ decisions, dead ends    │
                │  questions.jsonl              │
                │    └─ answered Qs for task    │
                │  check-read-state.py          │
                │    └─ skip fresh files        │
                │  skills/index.json            │
                │    └─ available skills        │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │  3. CLASSIFY → LOAD FLOW     │
                │                              │
                │  Signal word:                │
                │    fix/bug    → debug-flow   │
                │    add/new    → feature-flow │
                │    refactor   → refactor-flow│
                │                              │
                │  Also loads:                 │
                │    Project CLAUDE.md         │
                │    Section contract (if set) │
                └──────────────┬───────────────┘
                               │
                               ▼
          ┌────────────────────────────────────────────┐
          │  4. RISK CHECK                             │
          │                                            │
          │  ┌───────┐    ┌──────────┐    ┌─────────┐ │
          │  │  LOW  │    │  MEDIUM  │    │  HIGH   │ │
          │  │       │    │          │    │         │ │
          │  │ Auto  │    │ 2-cap +  │    │ STOP.   │ │
          │  │ run   │    │ plan-gate│    │ Need    │ │
          │  │       │    │ at phase │    │ approved│ │
          │  │       │    │ gates    │    │ plan    │ │
          │  └───┬───┘    └────┬─────┘    └────┬────┘ │
          └──────┼─────────────┼───────────────┼──────┘
                 │             │               │
                 │             │               ▼
                 │             │    ┌────────────────────┐
                 │             │    │  Write plan.       │
                 │             │    │  Submit to operator │
                 │             │    │  Wait for approval │
                 │             │    └────────┬───────────┘
                 │             │             │ approved
                 ▼             ▼             ▼
     ┌─────────────────────────────────────────────────────────┐
     │                                                         │
     │   5. WORK LOOP (Inner Loop)                             │
     │   ═══════════════════════════════════════                │
     │                                                         │
     │          ┌──────────┐                                   │
     │          │  Agent    │                                   │
     │          │  tries    │                                   │
     │          │  Edit /   │                                   │
     │          │  Write /  │                                   │
     │          │  Bash     │                                   │
     │          └─────┬─────┘                                   │
     │                │                                         │
     │                ▼                                         │
     │   ┌─────────────────────────────────────────────┐       │
     │   │          HOOK GAUNTLET (PreToolUse)          │       │
     │   │                                              │       │
     │   │  ① git-guard         (Bash only)             │       │
     │   │  ② fix-attempt-tracker                       │       │
     │   │  ③ bash-risk-logger  (Bash only)             │       │
     │   │  ④ LLM risk classifier (Bash only)           │       │
     │   │  ⑤ reference-check   (Edit only)             │       │
     │   │  ⑥ risk-classifier   (Edit/Write)            │       │
     │   │  ⑦ blast-radius      (Edit/Write)            │       │
     │   │  ⑧ plan-gate         (Edit/Write)            │       │
     │   │  ⑨ build-integrity   (Edit/Write)            │       │
     │   │                                              │       │
     │   │  Any BLOCK? ──► Tool call rejected           │       │
     │   │  All pass?  ──► Tool call proceeds           │       │
     │   └──────────────────────┬───────────────────────┘       │
     │                          │                               │
     │                          ▼ (tool executes)               │
     │                                                          │
     │   ┌─────────────────────────────────────────────┐       │
     │   │        TRACKING (PostToolUse)                │       │
     │   │                                              │       │
     │   │  After Edit/Write:                           │       │
     │   │    mid-session-snapshot.py                    │       │
     │   │    (every 15 mutations → state snapshot)     │       │
     │   │                                              │       │
     │   │  After Read:                                 │       │
     │   │    read-state-logger.py                      │       │
     │   │    (tracks file reads for staleness cache)   │       │
     │   └──────────────────────┬───────────────────────┘       │
     │                          │                               │
     │                          ▼                               │
     │            ┌──────────────────────────┐                  │
     │            │  Run tests?              │                  │
     │            ├────────────┬─────────────┤                  │
     │            │ PASS       │ FAIL        │                  │
     │            │ continue   │ fix attempt │                  │
     │            │            │ (≤2 tries)  │                  │
     │            └──────┬─────┴──────┬──────┘                  │
     │                   │            │                         │
     │                   │    ┌───────▼────────────┐            │
     │                   │    │ 2 attempts failed? │            │
     │                   │    │ Budget exhausted?  │            │
     │                   │    │ 4 edit-test cycles?│            │
     │                   │    │ 10 unique files?   │            │
     │                   │    └───────┬────────────┘            │
     │                   │            │ YES                     │
     │                   │            ▼                         │
     │                   │    ┌────────────────┐               │
     │                   │    │  CIRCUIT       │               │
     │                   │    │  BREAKER       │               │
     │                   │    │                │               │
     │                   │    │  → Escalate to │               │
     │                   │    │    operator    │               │
     │                   │    │  → Or write Q  │               │
     │                   │    │    and move on │               │
     │                   │    └────────────────┘               │
     │                   │                                      │
     │                   ▼                                      │
     │   ┌──────────────────────────────────┐                  │
     │   │  CONTEXT CHECK                   │                  │
     │   │                                  │                  │
     │   │  Turn > 25 or context heavy?     │                  │
     │   │  YES → Load context-checkpoint   │                  │
     │   │         skill, compress, continue │                  │
     │   │                                  │                  │
     │   │  Turn > 40 or context degraded?  │                  │
     │   │  YES → End session with handoff  │                  │
     │   │         (next session picks up)  │                  │
     │   │                                  │                  │
     │   │  NO  → Loop back to Edit/Write   │                  │
     │   └──────────────────┬───────────────┘                  │
     │                      │                                   │
     └──────────────────────┼───────────────────────────────────┘
                            │ task complete
                            ▼
          ┌──────────────────────────────────────────┐
          │  6. CLOSE                                │
          │                                          │
          │  Agent writes:                           │
          │    ✓ Run record → .agent/runs.jsonl      │
          │      (task_id, result, files, touches)   │
          │    ✓ Task status → "complete"             │
          │    ✓ Commit with task ID in message       │
          │                                          │
          │  Hooks fire automatically:               │
          │    langfuse-trace.py  → metrics           │
          │    audit-run-record   → warn if missing   │
          │    state-snapshot.py  → full state save    │
          └──────────────────────┬───────────────────┘
                                 │
                                 ▼
          ┌──────────────────────────────────────────┐
          │  7. WHAT'S NEXT?                         │
          │                                          │
          │  ready.py → another task pending?         │
          │    YES → Loop back to step 1 (CLAIM)     │
          │    NO  → Session ends cleanly             │
          │                                          │
          │  Operator can review:                    │
          │    assess.py     → pipeline health        │
          │    runs.jsonl    → session outcomes        │
          │    token-dashboard → cost tracking         │
          └──────────────────────────────────────────┘
```

## Decision Points Where the Operator Gets Involved

```
During execution, you get pulled in at these moments:

  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │  SPEC APPROVAL (feature-flow)                          │
  │  "Here's what I plan to build. Approve?"               │
  │  → You confirm intent before any code is written       │
  │                                                         │
  │  PLAN APPROVAL (high-risk tasks)                       │
  │  "Here's my implementation plan. Approve?"              │
  │  → You confirm approach before source mutations         │
  │                                                         │
  │  ESCALATION (2-attempt cap hit)                        │
  │  "I've tried twice and can't fix this. Help?"           │
  │  → You provide guidance or unblock                     │
  │                                                         │
  │  DANGEROUS COMMAND (LLM risk classifier)               │
  │  "This bash command looks risky. Proceed?"              │
  │  → You approve/deny the specific command               │
  │                                                         │
  │  ASYNC QUESTION (non-blocking)                         │
  │  Agent writes to questions.jsonl and moves on.         │
  │  You answer later. Next session picks it up.           │
  │                                                         │
  └─────────────────────────────────────────────────────────┘
```

# THE_FACTORY v2 — Operator's Guide

## Day-to-Day: Working on a Project

### Session Start

Open Claude Code in a project directory and say what you want to work on. The agent:

1. Reads CLAUDE.md (78 lines)
2. Hits trigger table → loads codebase orientation skill (for SCUE: file map, data flows, gotchas)
3. Reads `.agent/state-snapshot.json` (prior session's branch, commit, tasks, modified files)
4. Reads `.agent/tasks.jsonl` for open tasks
5. Tells you what's pending

This takes <5 reads. You pick what to work on.

### During Work

The agent classifies the task and loads the appropriate flow skill:
- Bug/error/failing → debug-flow (reproduce → isolate → diagnose → fix → verify)
- Feature/implement/add → feature-flow (intent → spec → plan → implement → test → verify)
- Refactor/simplify → refactor-flow (scope → snapshot → transform → verify)

**You don't tell agents what role to embody.** The flow skill IS the role. Say "this test is failing" — flow routing handles the rest.

### What Happens Automatically (Hooks)

You don't invoke these. They fire on their own:
- **git-guard:** Blocks commits to main, force-push, reset --hard
- **state-snapshot:** Writes branch/commit/tasks/modified-files to `.agent/state-snapshot.json` at session end
- **langfuse-trace:** Sends session metrics to Langfuse (when env vars are set)

### When Sessions End

The hooks handle state persistence. The agent should still:
- Update `.agent/tasks.jsonl` with task status
- Append a run record to `.agent/runs.jsonl` on task completion
- Log incidents to `.agent/incidents.jsonl` on failure

---

## Subagent Dispatch: Your Judgment, Not Theirs

**Let the agent do without asking you:**
- Launch Explore subagents to read specific directories (flow skills have scope guidance)
- Run tests, builds, typechecks
- Follow flow phases in order
- Escalate after 3 failed attempts (already in flow skills)

**The agent should surface these to you, not decide alone:**
- "I've tried 2 approaches and both failed — here's what I know. Want me to try a third, or should we bring in a research agent?"
- "This bug crosses the bridge/API/frontend boundary — should I investigate all layers or focus on one?"
- "The feature spec is ambiguous on X — here's what I'd assume, but confirm?"

**When the agent hits a wall:**

1. It tells you what it tried and why it failed
2. You decide: "keep going, try this angle" or "let me spin up a researcher"
3. If you dispatch a researcher, give it the specific question and file scope

**Good dispatch:** "Research the beat-link TimeFinder API — specifically whether `getTimeFor()` works over DLP connections. Check the Java source in `bridge-java/` and the beat-link docs. Report back what you find."

**Bad dispatch:** "Go explore SCUE and find the problem."

Targeted dispatch with specific context > auto-spawned multi-agent exploration. Mining confirmed: single agent + verification > naive multi-agent. The #1 waste source was 29 auto-spawned subagents reading overlapping files.

---

## Periodic Review (Every ~20 Sessions)

### Quick Assessment

```bash
# Score recent sessions against Phase 0 baselines
.venv/bin/python scripts/assess.py --last 20

# Run the eval suite
.venv/bin/python -m pytest evals/ -v

# Check pending improvement candidates
.venv/bin/python scripts/assess.py --improvements
```

### Full Review Process (for a version bump)

1. **Assess:** Run `assess.py --last 20` to score sessions and generate improvement candidates
2. **Eval check:** Run `pytest evals/` to verify no convention/flow drift
3. **Triage candidates:** Review each improvement — ACCEPT, DEFER, or REJECT
4. **For accepted improvements:**
   - Edit the relevant skill, hook, or convention
   - Add an eval case for the new behavior in `evals/`
   - Re-run `pytest evals/` to confirm the new eval passes
5. **Optional A/B test:** If unsure about a change, create a new variant YAML and test it:
   ```bash
   .venv/bin/python scripts/experiment.py --task tasks/relevant-task.py
   ```
6. **Re-measure:** Run `assess.py --last 20` after a few sessions with the change to verify improvement
7. **Version bump:** Update `.agent/VERSION.md` with what changed and why

### Baselines to Track

| Metric | Phase 0 Baseline | Target |
|--------|-----------------|--------|
| Overall waste | ~25% | <10% |
| Bug catch rate | 75% | >90% |
| Reads before first Edit | 15-30 | <5 |
| API misuse bugs / 20 sessions | 7 | <2 |
| Pre-existing test failures | 2 | 0 |

---

## Commands Reference

```bash
# Eval suite
.venv/bin/python -m pytest evals/ -v              # Run all 42 tests
.venv/bin/python -m pytest evals/ -k convention    # Just conventions
.venv/bin/python -m pytest evals/ -k mining        # Just mining regression

# Assessment
.venv/bin/python scripts/assess.py --baseline      # Show Phase 0 baselines
.venv/bin/python scripts/assess.py --last 20       # Score recent sessions
.venv/bin/python scripts/assess.py --improvements  # Pending candidates

# Experiments
.venv/bin/python scripts/experiment.py --list-tasks     # Available tasks
.venv/bin/python scripts/experiment.py --list-variants   # Available variants
.venv/bin/python scripts/experiment.py --task tasks/X.py # Run experiment

# SCUE tests (from projects/DjTools/scue/)
.venv/bin/python -m pytest tests/ -q                     # Full suite
.venv/bin/python -m pytest tests/test_bridge/ -q         # Bridge only
.venv/bin/python -m pytest tests/test_layer1/ -q         # Layer 1 only
```

---

## What NOT to Do

- **Don't tell agents what role to be.** Flow skills handle this. Say the task, not the persona.
- **Don't auto-dispatch swarms of researchers.** One targeted agent with a specific question beats five broad explorers.
- **Don't skip the flow classification.** Even if a task feels simple, picking the right flow (debug vs feature vs refactor) prevents scope creep and ensures gates are hit.
- **Don't manually run hooks.** They fire automatically. If they're not working, check `.claude/settings.json`.
- **Don't edit CLAUDE.md to add rules enforced by hooks.** If a hook enforces it, CLAUDE.md doesn't need to say it. If CLAUDE.md says it but no hook enforces it, consider whether it should be a hook.

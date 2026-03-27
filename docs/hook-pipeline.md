# Hook Pipeline

Ordered manifest of all hooks wired in `.claude/settings.json`.
Each phase runs in array order; blocking hooks abort the tool call on failure.

> **Source of truth:** `.claude/settings.json`. This document must stay in sync.
> Enforced by eval: `test_hook_pipeline_manifest_matches_settings`.

## PreToolUse Phase

| Order | Hook | Matcher | Type | Purpose |
|-------|------|---------|------|---------|
| 1 | git-guard.sh | Bash | Blocking | No commits to main, no force-push, no reset --hard |
| 2 | fix-attempt-tracker.sh | Bash | Blocking | 2-cap + compound budget (10 mutations/phase) |
| 3 | bash-risk-logger.sh | Bash | Advisory | Heuristic risk classification for shell commands |
| 4 | prompt risk classifier | Bash | Blocking | LLM-based command risk gating (SAFE/MODERATE/DANGEROUS) |
| 5 | reference-check.sh | Edit | Advisory | Warns when rename breaks eval/hook references |
| 6 | risk-classifier.sh | Edit, Write | Blocking | Task risk level enforcement (low/medium/high) |
| 7 | blast-radius.sh | Edit, Write | Blocking | Scope check vs section contract owned_paths |
| 8 | fix-attempt-tracker.sh | Edit, Write | Blocking | 2-cap + compound budget (shared with Bash matcher) |
| 9 | plan-gate.sh | Edit, Write | Blocking | Requires approved plan for high-risk tasks |
| 10 | build-integrity.sh | Edit, Write | Advisory | Warns on infrastructure file edits |

## PostToolUse Phase

| Order | Hook | Matcher | Type | Purpose |
|-------|------|---------|------|---------|
| 1 | mid-session-snapshot.py | Edit, Write | Passive | Lightweight state snapshot every 15 mutations |
| 2 | read-state-logger.py | Read | Passive | Log file reads for staleness cache |

## Stop Phase

| Order | Hook | Matcher | Type | Purpose |
|-------|------|---------|------|---------|
| 1 | langfuse-trace.py | * | Passive | Session metrics to Langfuse |
| 2 | audit-run-record.sh | * | Advisory | Warns if no run record written |

## SessionEnd Phase

| Order | Hook | Matcher | Type | Purpose |
|-------|------|---------|------|---------|
| 1 | state-snapshot.py | * | Passive | Full state snapshot for session continuity |

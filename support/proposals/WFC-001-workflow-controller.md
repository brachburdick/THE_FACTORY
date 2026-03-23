# WFC-001: Lightweight Workflow Controller Agent

**Date:** 2026-03-21
**Classification:** IDEA — not yet validated by failure.
**Source:** Pipeline review session (external reviewer + operator discussion)
**Scope:** Cross-project (root protocol change)

**v2.0 Status:** Several mechanical tasks WFC-001 proposed are now handled by hooks:
- Git guard → `git-guard.sh` hook
- State snapshot → `state-snapshot.sh` hook
- Session trace → `langfuse-trace.py` hook

Re-evaluate remaining scope before implementing.

## Problem

The operator currently performs two cognitively different jobs:
1. **Strategic reasoning** — priority decisions, feature rationale challenges, risk assessment, spec review
2. **Mechanical routing** — checking field presence in artifacts, deciding "does this need QA?", updating tasks.jsonl, verifying session summaries exist, enforcing gate conditions, preparing next handoff

Job #2 is procedural, not creative. It follows a checklist. It doesn't require the context or reasoning capability of a heavy model.

## Proposed Solution

A lightweight agent (Haiku-class) that executes a rigid procedure document. It sits between the operator and the reasoning agents, handling remaining mechanical workflow steps not covered by hooks:

```
Operator (Brach)
  |
  v
CONTROLLER (lightweight, procedural, Haiku)
  |
  +-- Pre-dispatch: artifact completeness, gate checks, field validation
  +-- Routing: which agent next, based on tags and procedure rules
  +-- Post-session: artifact existence, required field presence, flag detection
  |
  v
Reasoning Agents (Sonnet/Opus)
```

## Key Design Principles

1. **The controller does NOT reason.** It follows a procedure. It checks boxes and routes.
2. **The procedure document is the key artifact.** Versioned and iterable.
3. **Complementary strengths, not model replacement.**
4. **Cheap and fast.** Haiku tokens are ~20x cheaper than Opus.

## Decision Gate

After 5 feature sessions of data collection:
- If operator spends >20% of session time on mechanical routing → implement
- If operator spends <10% → defer indefinitely
- If 10-20% → evaluate whether the specific steps are automatable by Haiku

## Risks

- Procedure document maintenance overhead
- False confidence (operator stops checking things the controller "should" catch)
- Complexity budget (adding a layer must reduce net complexity, not increase it)

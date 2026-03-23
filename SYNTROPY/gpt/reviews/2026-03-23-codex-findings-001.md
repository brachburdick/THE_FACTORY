# Codex Findings 001

**Date:** 2026-03-23
**Reviewer:** Codex
**Scope:** Snapshot review of `SYNTROPY/gpt/` with special attention to the intended product domain: EDM track audio -> arrangement formula.
**Purpose:** Preserve this pass as a separate dated record so later reviews can be compared against it.

---

## Snapshot Summary

My current view is:

- the intellectual center is strong
- the package is better as a research argument than as a benchmark system
- the right next move is domain-grounded compression, not more theory

The strongest idea remains:

> preserve acceptance criteria while decomposing work into leaves that current agents can solve and verify.

---

## What Looks Strong In This Snapshot

### 1. The framing is pointed at a real problem

The best GPT-side contribution is the shift from generic decomposition language to:

- acceptance-criteria preservation
- leaf solvability
- verification before propagation
- ambiguity handling before overcommitting

That gives SYNTROPY a real center of gravity instead of "multi-agent planning" vagueness.

### 2. The agenda is disciplined

The research agenda asks the right questions:

- what makes a decomposition good
- what makes a leaf solvable
- what boundary heuristics help
- when verification pays off
- when to clarify instead of continuing

The sequence is also right:

- define
- benchmark
- baseline
- experiment
- automate

### 3. The self-critique is unusually healthy

The package already recognizes its biggest risk:

> overbuilding the doctrine before it proves that it improves outcomes

That makes the work much more credible.

### 4. The L2 simplification is a good instinct

The "good enough starter model" is the most practically usable thing in the current GPT package.

The emphasis on:

- explicit acceptance criteria
- tiny plans
- per-step verification
- local replanning

feels like the right minimum process candidate.

---

## What Looks Weak In This Snapshot

### 1. The benchmark bridge is still thin

The current GPT-side practical floor is still centered on a generic toy programming case.

That proves internal coherence.

It does not yet prove much about the actual problem space SYNTROPY claims to help with.

### 2. The folder still has too much navigation overhead

At this snapshot, the story is distributed across:

- synthesis
- agenda
- reality check
- context note
- cross-examination
- minimum viable pass
- Codex review
- domain suggestion

That is thoughtful, but it is still heavier than it should be for a project explicitly worried about overhead.

### 3. The experimental discipline is ahead of the actual run logs

The experiment templates ask for more detail than the recorded runs currently preserve.

That means the measurement posture is stronger than the measurement record.

### 4. Canon and commentary are not yet cleanly separated

Some ideas are current best bets.
Some are reviewer interpretations.
Some are scaffolding abstractions.

At this snapshot, those categories are not separated sharply enough.

---

## Domain-Specific Finding

For the target domain:

> EDM track audio file -> arrangement formula

the most important improvement is to make the benchmark family domain-native.

That means:

- stop treating `slugify` as the meaningful proof point
- make section-boundary detection the first canonical benchmark
- then climb toward drum summaries, bass/vocal presence, and full arrangement formula output

Why this matters:

- section boundaries are structurally central
- they are easy to verify by ear
- they create the skeleton for later layers
- they are much closer to the real product

There is already a strong clue in the workspace that this is the right direction:

- `SYNTROPY/claude/experiment-001-section-boundaries.md`

That path should be promoted into the main benchmark story.

---

## Recommendation At This Snapshot

If only one improvement gets made next, it should be this:

create a canonical domain benchmark file that defines the arrangement-formula task family.

Suggested file:

- `arrangement-formula-benchmark.md`

It should define:

- the target JSON schema
- the benchmark ladder
- stage-by-stage acceptance criteria
- automatic checks vs ear-based checks
- what counts as pass/fail at each level

This would give SYNTROPY:

- a real domain object
- a real decomposition target
- a cleaner experiment bridge
- a better basis for future change tracking

---

## Tracking Notes

This file is meant to stay unchanged as a dated snapshot.

For later updates:

- create `2026-..-codex-findings-002.md`, `003.md`, and so on
- compare new judgments against this snapshot instead of overwriting it

The main future questions to compare against are:

1. Has the benchmark become domain-native?
2. Is there now a canonical arrangement-formula schema?
3. Are run logs capturing the claimed metrics?
4. Is the package getting smaller and sharper, or larger and more diffuse?

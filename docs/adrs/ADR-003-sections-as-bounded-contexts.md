# ADR-003: Sections as Bounded Contexts

**Date:** 2026-03-23
**Status:** Accepted
**Deciders:** Brach (operator), formalized during v2.1 section review work

## Context

Complex projects (SCUE: 5 layers, frontend, bridge) need a decomposition strategy that
enables scoped review, parallel work, and blast radius enforcement. The question was
whether to use folders, modules, layers, or a custom boundary system.

Folder structure doesn't always align with dataflow. Module boundaries are language-specific.
Layer boundaries are too coarse (a single layer can have multiple independent concerns).

## Decision

Use **sections** — explicitly defined review units with 1-page contracts. Each section has:
- Owned paths (directories/files it controls)
- Incoming inputs and outgoing outputs (dataflow boundaries)
- Invariants (rules that must always hold)
- Verification command (how to test it independently)

Sections are defined in `sections/SECTIONS.md` with individual contracts in `sections/{name}.md`.
They are a living artifact — re-evaluated after each milestone or significant refactor.

Enforcement: the blast-radius hook (tf-025) cross-references Edit/Write paths against
the active task's section contract, blocking out-of-scope mutations.

## Consequences

### Positive
- Scoped review — agents can review one section without loading the whole project
- Blast radius enforcement — out-of-scope mutations are blocked by hooks
- Parallel-safe — independent sections can be worked on simultaneously
- Natural split/merge criteria — sections evolve with the codebase

### Negative
- Maintenance overhead — contracts must be updated when boundaries shift
- Learning curve — new contributors need to understand the section model
- Not language-native — sections are a convention, not enforced by the type system

### Neutral
- Sections can align with layers but don't have to (SCUE's "strata" section is a subset of Layer 1)
- Section coupling map provides architectural documentation as a side effect

## Alternatives Considered

### Folder-based decomposition
Rejected because folder structure is an accident of early project layout, not a reflection
of dataflow boundaries. SCUE's `scue/layer1/strata/` is a subfolder of Layer 1 but has
independent concerns, tests, and review needs.

### Language module boundaries
Rejected because they're language-specific (Python packages, TS barrel exports) and don't
capture cross-language boundaries (Python backend ↔ TypeScript frontend). Sections work
across the full stack.

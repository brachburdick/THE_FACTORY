# ADR-001: Single Agent with Skills Architecture

**Date:** 2026-03-20
**Status:** Accepted
**Deciders:** Brach (operator), established during v1.9→v2.0 migration

## Context

THE_FACTORY needed to coordinate AI agent work across multiple projects. The two obvious
approaches were: (a) multiple standing agents with fixed roles (researcher, coder, reviewer),
or (b) a single operator agent that loads specialized behavior via skill files on demand.

Multi-agent coordination adds inter-agent communication complexity, role boundary disputes,
and context duplication. Our workload is serial (one task at a time, one human operator),
not parallel.

## Decision

Use a **single operator agent** that loads skills on demand via a trigger table. Skills are
markdown files with frontmatter, loaded into context when their trigger pattern matches.
No standing roles, no inter-agent protocols, no message buses.

The agent dispatches to subagents (Explore, Plan) for scoped research tasks, but these are
ephemeral — they report back and terminate. They don't maintain state or identity.

## Consequences

### Positive
- No inter-agent coordination overhead — one context, one decision-maker
- Skills are just files — easy to version, review, test, and evolve
- Progressive disclosure — context window stays clean until a skill is needed
- Eval suite can test skill content directly (frontmatter, required sections)

### Negative
- Single point of failure — if the agent makes a bad decision, there's no peer review layer
- Context window pressure — loading too many skills at once degrades performance
- No parallelism — can't work on two tasks simultaneously

### Neutral
- Subagents exist but are ephemeral research tools, not standing team members

## Alternatives Considered

### Multi-agent team with fixed roles
Rejected because our workload is serial and operator-supervised. The coordination overhead
(handoffs, shared state, conflict resolution) would exceed the parallelism benefit.

### Plugin/tool architecture (MCP-style)
Considered but rejected for the skill layer. Skills need to influence prompt behavior
(decision-making, flow control), not just provide tool capabilities. MCP tools are used
for external integrations (browser, preview) but not for behavioral guidance.

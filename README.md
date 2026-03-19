you can ignore all this
feed Claude the INIT and go fkn ham







# THE_FACTORY

THE_FACTORY is a reusable operating system for software projects run with specialized AI agents.

It is not the product codebase. It is the protocol, prompts, and templates that create and govern project-specific agent workflows.

## Root Essentials

| File | Use |
|------|-----|
| `README.md` | Human-readable overview and quickest start path |
| `INIT.md` | Give this to a fresh agent helping a new user get started |
| `OPERATOR_PROTOCOL.md` | Master operating manual for roles, artifacts, workflows, and quality gates |
| `IMPLEMENTATION_PROMPT.md` | Prompt for the Protocol Enforcer that bootstraps or syncs a project |
| `PROTOCOL_REVIEW_PROMPT.md` | Prompt for reviewing and improving the protocol itself |
| `PROTOCOL_IMPROVEMENTS.md` | Running cross-project backlog of bugs, gaps, friction, and ideas |

Also at the root:

- `templates/` — canonical artifact schemas the Protocol Enforcer can copy into a project
- `projects/` — example or active project folders
- `support/` — archived reviews, drafts, sync notes, and other non-essential root material

## Fastest Way To Start

1. If you are a human, read this file.
2. If you are handing the workspace to a fresh agent, start with `INIT.md`.
3. Let that agent help you clarify what you want to build and whether you should first talk to a Researcher, Designer, or Architect.
4. When the brief is good enough, use `IMPLEMENTATION_PROMPT.md` plus `OPERATOR_PROTOCOL.md` to invoke the Protocol Enforcer.
5. After bootstrap, switch to the first Orchestrator prompt created for the new project and let the project-local workflow take over.

## The Core Idea

Agents do not rely on shared memory. They coordinate through artifacts on disk.

The pattern is:

`human intent -> artifact -> specialized agent -> artifact -> next decision`

That makes the workflow restartable, reviewable, and less dependent on one long chat thread.

## The Main Roles

- `Operator` decides priorities, answers open questions, and routes work.
- `Orchestrator` reads current state and writes the next handoff packet.
- `Architect` turns goals into specs, plans, tasks, and interface definitions.
- `Researcher` investigates unknowns and writes structured findings.
- `Designer` produces UI and interaction specs when needed.
- `Developer` implements one scoped task.
- `Validator` checks whether the Developer output satisfies the handoff contract.
- `QA Tester` verifies live behavior when validation is not enough.
- `Protocol Enforcer` bootstraps or syncs the project-local agent infrastructure.

## When To Dispatch Directly vs. Through The Orchestrator

Use `DIRECT DISPATCH` when the next agent needs your live judgment, taste, clarification, or exploratory direction.

Use `ORCHESTRATOR DISPATCH` when a file already defines the next step clearly enough that the next agent should follow that artifact instead of a fresh conversation.

Short rule:

- If the next step should come from you, dispatch directly.
- If the next step should come from a file, use the Orchestrator.

## Typical New-Project Flow

1. Start with `INIT.md`.
2. Clarify the idea and, if needed, run pre-build Researcher, Designer, or Architect sessions.
3. Produce a compact pre-bootstrap brief.
4. Invoke the Protocol Enforcer with `IMPLEMENTATION_PROMPT.md` and `OPERATOR_PROTOCOL.md`.
5. Let it create the new project's bootstrap docs, preambles, templates, and startup prompts.
6. Start the first project Orchestrator session from the prompt the Protocol Enforcer generated.

## Typical Delivery Flow

For implementation work, the default sequence is:

`Developer -> Validator -> QA Tester when required -> next handoff or closeout`

Important distinctions:

- Validator `PASS` means the work appears to satisfy the handoff contract.
- QA `PASS` means the behavior was confirmed in practice.

## Workspace Layout

- `templates/` holds the canonical root template set.
- `projects/` holds project folders and examples.
- `support/` holds historical or reference material that does not need to stay at root.

If you are sharing this workspace with someone new, the safest handoff is:

1. Share `README.md`.
2. Tell them to give `INIT.md` to a fresh agent.
3. Let that agent prepare the Protocol Enforcer invocation.

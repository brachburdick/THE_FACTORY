# THE_FACTORY — Workspace Orientation

This is the root of a multi-agent development system. It is **not** a software project. It contains the protocol and tooling that govern all projects.

## Root Files

| File | Purpose |
|------|---------|
| `README.md` | Human-readable overview and fastest start path |
| `INIT.md` | Onboarding guide — give this to a fresh agent helping a new user get started |
| `OPERATOR_PROTOCOL.md` | Master operating manual: roles, schemas, workflows, directory structure, improvement process |
| `IMPLEMENTATION_PROMPT.md` | Protocol Enforcer prompt — run to bootstrap a new project or sync an existing one after a protocol review |
| `PROTOCOL_REVIEW_PROMPT.md` | Protocol Review prompt — run periodically to process the improvements backlog |
| `PROTOCOL_IMPROVEMENTS.md` | Running log of bugs, gaps, friction, and ideas across all projects |
| `AGENTS.md` | This file |

## Root Folders

- `templates/` — canonical root artifact templates
- `projects/` — example or active projects
- `support/` — archived reviews, drafts, and other non-essential root material

## Common Tasks

- **Start a new user from scratch:** Give a fresh agent `INIT.md`
- **Review and apply protocol improvements:** Load `PROTOCOL_REVIEW_PROMPT.md` + `OPERATOR_PROTOCOL.md` + `PROTOCOL_IMPROVEMENTS.md`
- **Bootstrap a new project:** Load `IMPLEMENTATION_PROMPT.md` + `OPERATOR_PROTOCOL.md`
- **Sync an existing project after a protocol review:** Same as above, plus the project's existing preambles/templates
- **Log an observation:** Append to `PROTOCOL_IMPROVEMENTS.md` under `## Pending`

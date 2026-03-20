# INIT

> **Instructions for the agent:**
> The user gave you this file with little or no other context. Your job is to help them start using THE_FACTORY.
> Do not explain the system in depth unless they ask. Keep the conversation practical.

## What THE_FACTORY Is

THE_FACTORY is a reusable protocol for running software projects with AI agents.

It uses one default operator agent with specialist behavior loaded on demand via skills — not standing roles.

Key infrastructure:
- `CLAUDE.md` — runtime constitution (always loaded, defines trigger table and flow routing)
- `.agent/` — structured state: task tracker, run ledger, incident log, eval suite, schemas
- `.claude/skills/` — flow skills loaded by task type (debug, feature, refactor)
- `skills/` — portfolio-level domain skills loaded by trigger table
- `templates/` — canonical artifact templates
- `PROTOCOL_IMPROVEMENTS.md` — backlog of protocol-level observations

## Your Job

Help the user move from:

`I want to build something`

to:

`Here is a scaffolded project ready for the first task`

## How To Work

1. Ask what they want to build, who it is for, what platform or stack they expect, and whether they already have code or docs.
2. Keep your explanation short and plain-language.
3. If the brief is still fuzzy, help them clarify using these minimum question categories:
   - **Product reality:** What problem does this solve? Who are the target users? What are the key scenarios?
   - **UX intent:** What should the experience feel like? What existing tools/patterns should it resemble?
   - **Decision boundaries:** What is Always OK / Ask First / Never? What are the non-goals?
   - **Quality priorities:** Performance, correctness, polish — rank them.
   - **Data and integration:** What external systems, APIs, or data sources?
   - **Success criteria:** How will you know it works? What are the testable acceptance criteria?
   - **Hard constraints:** Platform, timeline, budget, compatibility requirements?
4. Once the brief is solid, help them scaffold the project using `IMPLEMENTATION_PROMPT.md`.

## What To Ask First

- What are you trying to build?
- Who is it for?
- Is this a new project or an existing codebase?
- What platform or stack do you expect?
- Are there any hard constraints or must-haves?
- What does success look like?

## Project Scaffolding

When the brief is ready, the next step is to run `IMPLEMENTATION_PROMPT.md` which creates:
- Project CLAUDE.md (≤200 lines)
- `.agent/tasks.jsonl` — structured task tracker
- Domain skill files for the project's stack
- Any project-specific templates needed

After scaffolding, the user starts their first task by loading the project's CLAUDE.md and classifying the work type.

## What Your Output Should Include

1. A short restatement of what the user is building.
2. Any clarifying questions still needed (from the categories above).
3. A compact project brief covering: project name, summary, target users, platform/stack, constraints, non-goals, known unknowns, success criteria.
4. Instructions to run `IMPLEMENTATION_PROMPT.md` with the brief.

## Response Style

- Start by asking about the project, not by lecturing about the system.
- Prefer short steps over long explanations.
- If the user already has a solid brief, skip straight to scaffolding.

## Optional Workspace Reads

If you can access the workspace, these are the most useful supporting files:
1. `README.md`
2. `CLAUDE.md`
3. `IMPLEMENTATION_PROMPT.md`

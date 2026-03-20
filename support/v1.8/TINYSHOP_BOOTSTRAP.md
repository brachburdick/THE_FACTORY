# Tinyshop — Protocol Enforcer Bootstrap Input

> **Instructions for the human operator:**
> Start a fresh Protocol Enforcer conversation. Load this file, `IMPLEMENTATION_PROMPT.md`,
> and `OPERATOR_PROTOCOL.md`. The Protocol Enforcer will create all project infrastructure
> for Tinyshop.

---

## Project Summary

**Tinyshop** is a local web application that serves as a human-friendly user interface for the THE_FACTORY multi-agent development pipeline. It makes the existing artifact-driven workflow visible, easier to operate, and more approachable for non-technical users without replacing the underlying protocol.

The core metaphor is a tiny workshop where specialized characters (agent mascots) do their jobs at visible stations. Users see the production line, not a directory tree.

For V1, Tinyshop prepares launch packages, watches artifacts, and helps the operator understand what should happen next. It does not own agent execution yet.

## Naming Convention

Tinyshop is a UI for a multi-agent pipeline — and it is itself built using that same pipeline. To avoid confusion between the protocol roles (Orchestrator, Architect, Developer, etc.) and the in-app agent mascots that represent them, all Tinyshop-native agent roles use the **TINY** prefix:

- **TINY Shopkeeper** — the bootstrap conversational agent (Tinyshop-native, not a protocol role)
- **TINY Orchestrator** — the mascot representing the protocol's Orchestrator role
- **TINY Architect**, **TINY Developer**, etc. — mascots for all other protocol roles

When this document says "Orchestrator," it means the protocol role. When it says "TINY Orchestrator," it means the in-app mascot and its associated UI behavior.

## Stack

- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS
- **Backend:** Next.js route handlers and local server utilities (Node.js)
- **LLM:** Anthropic SDK (`@anthropic-ai/sdk`) for the TINY Shopkeeper conversational agent
- **Real-time:** Server-Sent Events (SSE) for artifact and state refresh in V1
- **File watching:** `chokidar` for artifact change detection
- **Storage:** SQLite (via `better-sqlite3`) for settings, project registry, and lightweight local indexes
- **Artifact parsing:** `gray-matter` for YAML frontmatter, `marked` or `react-markdown` for rendering

**Deferred runtime note:** future versions may add direct Claude Code session management via Node.js `child_process`, but V1 must not depend on live process control for pipeline agents. The TINY Shopkeeper is the only LLM-powered agent in V1, and it uses the Anthropic API directly — not Claude Code.

## Architecture Overview

Tinyshop has five layers:

### 1. Project Adapter / Launch Package Engine
Prepares the information a human needs to start the correct agent session outside Tinyshop:
- Resolves the current project's expected protocol files
- Reads startup prompts and project structure conventions
- Assembles launch packages for a selected role
- Produces operator-facing checklists: dispatch mode, files to load, startup prompt, and expected output artifact

### 2. Artifact Engine
Reads and indexes the project directory in real time:
- Watches for file changes via `chokidar`
- Parses artifact YAML frontmatter for status, relationships, and metadata
- Maintains an in-memory and SQLite-backed index of relevant artifacts
- Pushes updates to the frontend via SSE
- Derives timeline-style activity from artifact changes and known protocol file patterns

### 3. TINY Shopkeeper Agent
The only LLM-powered agent in V1. A conversational agent that powers the bootstrap flow:
- Uses the Anthropic API directly (not Claude Code) with a focused system prompt
- Understands THE_FACTORY protocol structure: what a project needs, what questions to ask, what the Protocol Enforcer expects
- Conducts a guided Q&A with the user to gather: project name, stack, constraints, goals, domain context
- Asks intelligent follow-up questions based on what the user describes (not a static form)
- When enough information is gathered, prepares a Protocol Enforcer launch package
- Conversation history persisted to SQLite so the user can resume if they leave mid-bootstrap
- Does NOT read/write project files or use tools — it is purely conversational

### 4. Dispatch Engine
Automates the workflow guidance the operator currently performs manually:
- Reads current artifacts, startup prompts, and orchestrator state
- Generates dispatch suggestions to the user
- Helps the user choose between `DIRECT DISPATCH` and `ORCHESTRATOR DISPATCH`
- Prepares launch packages for Protocol Enforcer (from TINY Shopkeeper output) and follow-on launch packages for project agents
- Handles the TINY Orchestrator-as-primary-guide flow after bootstrap completes

### 5. Compatibility Layer
Allows Tinyshop to work against current protocol projects without requiring root-protocol changes:
- Detects whether a project has the expected bootstrap files, prompts, and artifact paths
- Flags compatibility gaps clearly instead of guessing
- Degrades gracefully to partial or manual-dispatch mode if project structure drifts
- Keeps Tinyshop usable against current v1.7/v1.8-era projects

### 6. Frontend
Next.js app with these views:

**Welcome / Bootstrap View**
- First-run experience. The TINY Shopkeeper greets the user and asks what they're building.
- LLM-powered conversational Q&A: the TINY Shopkeeper asks intelligent follow-up questions based on what the user describes, not a static form.
- When enough information is gathered, the TINY Shopkeeper prepares a Protocol Enforcer launch package for the user to run manually.
- Bootstrap progress shown visually through detected files and generated project structure.
- Transition to TINY Orchestrator-led workflow when bootstrap artifacts appear.

**Workshop View (primary)**
- Pipeline visualization: current phase per feature/task and which role is most relevant next.
- Agent mascots at their stations. The currently relevant role is highlighted.
- Decision queue: `[DECISION NEEDED]` and `[ASK OPERATOR]` items surfaced as actionable cards.
- Artifact sidebar: browse and view rendered artifacts.
- Guided mode explains the workflow in plain language; Ops mode reveals protocol-native terms and paths.

**Launch Package View**
- Shows the exact package for starting the next agent session.
- Includes:
  - target role
  - dispatch mode
  - files to load
  - startup prompt
  - expected output artifact
  - completion checklist
- Supports copy, open, and confirm-style operator actions without embedding a live terminal session.

**Artifact Viewer**
- Rendered markdown with syntax highlighting
- Metadata header displayed as structured badges (status, relationships)
- Diff or comparison view for superseded artifacts where helpful

**Settings**
- Attached project path
- Workspace preferences
- Guided vs Ops mode preference
- Future-facing mascot preferences

## Agent Mascots

Each protocol role gets a TINY mascot character. The visual style should be warm, compact, and expressive — think Overcooked characters or Cooking Mama assistants. Professional enough to take seriously, charming enough to be memorable.

| TINY Role | Mascot Concept | Station | V1 LLM-Powered? |
|-----------|---------------|---------|-----------------|
| TINY Shopkeeper (bootstrap) | Friendly shop owner behind a counter | Welcome desk | Yes (Anthropic API) |
| TINY Orchestrator | Floor manager with a clipboard | Central dispatch board | No (dispatch guidance only) |
| TINY Architect | Builder with blueprints | Drafting table | No (mascot only) |
| TINY Researcher | Explorer with a magnifying glass | Library / filing cabinet | No (mascot only) |
| TINY Designer | Artist with a palette | Design easel | No (mascot only) |
| TINY Developer | Mechanic with a wrench | Workbench | No (mascot only) |
| TINY Validator | Inspector with a checklist | Quality control station | No (mascot only) |
| TINY QA Tester | Tester with a magnifying glass and stopwatch | Testing booth | No (mascot only) |

In V1, only the TINY Shopkeeper is an actual LLM-powered agent. All other TINY roles are mascot representations of the protocol roles — they visualize state and guide dispatch but do not reason autonomously. Future versions may power additional TINY roles with LLM capabilities.

The mascots should clarify workflow and role boundaries. They should not hide the real artifact model.

## MVP Scope

The MVP gets a user from zero to a working TINY Orchestrator-led workflow for a single project:

1. **Welcome flow:** TINY Shopkeeper (LLM-powered) greets the user, asks intelligent questions, and gathers project info through natural conversation.
2. **Bootstrap package prep:** TINY Shopkeeper prepares the Protocol Enforcer launch package the user needs to run manually.
3. **Transition:** When bootstrap artifacts appear, the TINY Orchestrator becomes the primary workflow guide.
4. **TINY Orchestrator launch guidance:** Tinyshop prepares the Orchestrator launch package and shows resulting artifacts.
5. **Artifact viewer:** User can browse and read rendered artifacts the agents produce.
6. **Agent dispatch support:** When the workflow calls for another role, Tinyshop helps the user prepare and launch that session outside Tinyshop via the relevant TINY mascot.
7. **Agent lifecycle visibility:** When an agent completes, its output artifact is visible and Tinyshop can recommend the next step.

**Explicit MVP rule:** Tinyshop does not parse live Claude terminal output in V1.

### Explicitly deferred from MVP:
- Direct Claude Code process spawning
- Live terminal or chat streaming
- Tool approval interception
- Parallel agent sessions
- Multi-project dashboard
- User-directed flow changes that update the protocol
- Custom mascots
- Protocol review or protocol-update flows from the UI
- Mobile or responsive layout work

## Key Technical Challenges

### 1. Reliable project compatibility detection
Tinyshop must determine whether an attached project has enough of the expected protocol structure to support guided operation. This requires:
- checking for bootstrap docs, startup prompts, state files, and expected artifact locations
- distinguishing between "fully supported," "partially supported," and "manual-dispatch only"
- surfacing compatibility issues clearly without blocking read-only use

### 2. Artifact indexing and next-action derivation
Tinyshop must infer workflow state from the current protocol structure without requiring new root-protocol infrastructure. This requires:
- indexing handoffs, session summaries, verdicts, and state snapshots
- identifying current vs superseded artifacts
- deriving the next recommended action from handoffs, verdicts, and operator-question markers

### 3. Bootstrap → Orchestrator transition
The app must detect when the Protocol Enforcer has finished creating enough project infrastructure for the user to continue. Detection strategy:
- watch for expected output files (`AGENT_BOOTSTRAP.md`, `preambles/ORCHESTRATOR.md`, startup prompts, templates, etc.)
- use the migration checklist and generated project structure as completion signals
- rely on artifact presence only; do not require a custom Tinyshop completion marker in V1

### 4. TINY Shopkeeper system prompt design
The TINY Shopkeeper must understand enough about THE_FACTORY protocol to ask good questions without being a full protocol agent. This requires:
- A system prompt that encodes what information the Protocol Enforcer needs (project name, stack, constraints, goals, domain context)
- Conversational intelligence: asking follow-ups based on what the user says, not a fixed script
- Knowing when it has gathered enough to produce a launch package
- Producing a structured output (the launch package) from an unstructured conversation
- Handling edge cases: user doesn't know their stack yet, user wants to attach an existing project, user is non-technical

### 5. Launch package assembly without new manifests
Tinyshop must generate robust, operator-friendly launch packages from the current protocol. This requires:
- reading existing startup prompts and project docs
- applying current protocol conventions consistently
- avoiding silent guesses when a project deviates from expected structure
- falling back to manual guidance when automation confidence is low

## Tinyshop-Specific Files

Beyond the standard protocol project structure, Tinyshop needs:

- `.tinyshop/` — App-level config (not per-project)
  - `config.json` — workspace path, attached project, preferences
  - `projects.json` — saved project registry for future expansion

**Future Tinyshop backlog item, not a V1 bootstrap requirement:**
- `docs/agents/manifests/` — machine-readable invocation manifests, if the protocol later adopts them

## Constraints

- **Local-first.** No auth, no remote storage, no hosted services. The only external API call in V1 is the TINY Shopkeeper's use of the Anthropic API (requires the user's own API key).
- **Tinyshop does not spawn Claude Code sessions in V1.** Pipeline agents are launched by the operator outside Tinyshop. The TINY Shopkeeper uses the Anthropic API directly for its conversational flow — it is not a Claude Code session.
- **Artifacts stay on disk.** The project directory is the source of truth. Tinyshop reads and indexes but does not duplicate canonical artifact content into its own database.
- **Protocol-compatible.** A project managed through Tinyshop must also be manageable from the CLI. The UI is an overlay, not a replacement for the underlying file-based system.
- **Single user, local.** No multi-user, no auth, no network access from other machines.

## Top 3 Things Agents Will Get Wrong in This Project

1. **Trying to build runtime/session spawning too early.** V1 is watcher-first. Tinyshop should prepare launch packages and monitor artifact outcomes before attempting to own live Claude session execution.
2. **Storing canonical artifact content in SQLite.** SQLite stores settings and lightweight indexes only. The filesystem is the source of truth for all artifacts.
3. **Assuming every project is perfectly machine-parseable.** Tinyshop must support graceful fallback when projects drift from expected structure instead of silently guessing.

## Protocol Changes This Project Motivates

These are **Tinyshop backlog recommendations**, not current root-protocol prerequisites. Do not make V1 depend on them.

If Tinyshop proves they would significantly improve reliability, they can be proposed later through the normal Protocol Review process.

1. **Event log (`docs/agents/events.jsonl`).** Append-only structured log of pipeline activity. Would make Tinyshop timelines and state reconstruction much simpler.
2. **Invocation manifests (`docs/agents/manifests/*.yaml`).** Machine-readable dispatch instructions per role. Would make launch-package generation more robust and less heuristic.

Tinyshop V1 must work against the current protocol without requiring either of these changes.

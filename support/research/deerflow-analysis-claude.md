# DeerFlow 2.0: a deep technical architecture evaluation

ByteDance's DeerFlow 2.0 is a **single-lead-agent harness built on LangGraph** that delegates dynamically to sub-agents via a `task` tool, manages cross-cutting concerns through an 11-stage middleware pipeline, and gives agents real code execution inside Docker sandboxes. Released February 28, 2026 as a ground-up rewrite sharing zero code with v1, it has reached **~46,800 GitHub stars** and 107 contributors in under a month. For teams evaluating it against a custom Node.js/TypeScript pipeline like THE_FACTORY with tiered memory, JSON Schema handoff envelopes, and a sandboxed evaluation harness like CRUCIBLE: DeerFlow excels at execution-first orchestration and skill extensibility but **ships no evaluation framework whatsoever**, uses simple string-based memory deduplication (not semantic), and locks you into the LangChain/LangGraph Python ecosystem.

---

## The lead agent + middleware architecture replaces v1's rigid graph

DeerFlow v1 used a 9-node LangGraph `StateGraph` with static edges routing tasks to specialist nodes (researcher, analyst, coder) based on a `StepType` enum. V2 flattened this entirely. A **single lead agent** sits behind an ordered middleware chain, and task decomposition is model-driven — the LLM decides when to delegate by calling the `task` tool.

The entry point is registered in `langgraph.json` as `deerflow.agents.lead_agent.agent:make_lead_agent`. At construction time, the factory function assembles three things: a model (resolved from `config.configurable`, supporting any LangChain-compatible provider), a tool set (config-defined + MCP + built-in + the `task` tool), and the middleware chain. The **11 middlewares execute in strict order**:

1. **ThreadDataMiddleware** — creates per-thread directories under `.deer-flow/threads/{thread_id}/`
2. **UploadsMiddleware** — injects newly uploaded files into context
3. **SandboxMiddleware** — acquires a sandbox, stores `sandbox_id` in state
4. **DanglingToolCallMiddleware** — patches orphaned tool calls from interrupted turns
5. **SummarizationMiddleware** — compresses context near token limits
6. **TodoListMiddleware** — tracks multi-step plans (optional, plan-mode only)
7. **TitleMiddleware** — auto-generates thread title after first exchange
8. **MemoryMiddleware** — queues conversation for async memory extraction
9. **ViewImageMiddleware** — injects base64 image data for vision models
10. **SubagentLimitMiddleware** — caps concurrent `task` calls at **3** (clamped to [2,4])
11. **ClarificationMiddleware** — intercepts `ask_clarification`, interrupts via `Command(goto=END)` — must be last

Each middleware implements hooks: `before_agent`, `before_model`, `after_model`, or `wrap_model_call`. This architecture means cross-cutting concerns (memory, summarization, sandbox lifecycle) are independently testable and configurable — a significant improvement over v1's tangled graph nodes.

**Comparison to THE_FACTORY's handoff envelopes:** DeerFlow's `task` tool call is the handoff mechanism. Its parameters — `description`, `prompt`, `subagent_type`, `max_turns` — are less structured than JSON Schema envelopes. There's no schema validation on the handoff payload; the LLM generates free-text instructions for sub-agents. If your pipeline relies on typed, validated handoff contracts between agents, DeerFlow doesn't enforce this.

---

## Sub-agent delegation is dynamic, parallel, and non-recursive

When the lead agent calls `task()`, the `SubagentExecutor` dispatches the work to a background thread pool (**3 scheduler workers**, **3 execution workers**). Sub-agents emit SSE events (`task_started` → `task_running` → `task_completed/task_failed/task_timed_out`), and the lead agent polls every 5 seconds for completion. Results return as structured `ToolMessage` objects that the lead agent synthesizes.

Two built-in sub-agent types exist in the `AgentRegistry`:

- **`general-purpose`** — gets all tools *except* `task` (preventing infinite delegation chains)
- **`bash`** — command-line tools only, for command-specialist work

**Context isolation is real but limited.** Each sub-agent gets its own scoped conversation context — it cannot see the lead agent's message history or other sub-agents' contexts. However, all sub-agents **share the thread's sandbox filesystem**, enabling file-based collaboration (one sub-agent writes a CSV, another reads it). This is a pragmatic design: isolated reasoning context, shared execution state.

The lead agent's `ThreadState` extends LangGraph's `AgentState` with custom fields: `sandbox` (holds `sandbox_id`), `thread_data` (per-thread path mappings), `title`, `artifacts` (deduplicated via `merge_artifacts` reducer), `todos`, `uploaded_files`, and `viewed_images`. Runtime configuration exposes toggles for `thinking_enabled`, `model_name`, `is_plan_mode`, and `subagent_enabled`.

---

## Skills are Markdown files loaded on-demand into agent context

DeerFlow's skill system encodes domain expertise as **SKILL.md files with YAML frontmatter**, organized under `skills/{public,custom}/`. The project ships **16 built-in skills**: bootstrap, chart-visualization, claude-to-deerflow, consulting-analysis, data-analysis, deep-research, find-skills, frontend-design, github-deep-research, image-generation, podcast-generation, ppt-generation, skill-creator, surprise-me, vercel-deploy-claimable, and video-generation.

**Progressive loading works in two stages.** First, `load_skills()` recursively scans skill directories and injects only *enabled* skills (per `extensions_config.json`) into the system prompt as container paths (e.g., `/mnt/skills/public/video-generation/SKILL.md`). The actual SKILL.md content is **not** loaded into the prompt — only the path reference. Second, when the agent needs a skill, it uses `read_file` to load the specific SKILL.md on-demand. This keeps the base context window lean.

A sample SKILL.md frontmatter:

```yaml
---
name: video-generation
description: Use this skill when the user requests to generate, create, or imagine videos.
---
```

**Four methods exist for adding custom skills:**

1. Drop a directory with a `SKILL.md` into `skills/custom/` and enable in `extensions_config.json`
2. `PUT /api/skills/<name>` via the Gateway API to toggle enabled state
3. `POST /api/skills/install` with a `.skill` archive — a ZIP file containing a directory with `SKILL.md` plus optional scripts and resources, extracted to `skills/custom/`
4. `DeerFlowClient.install_skill("/path/to/skill.skill")` for programmatic installation

The `.skill` format accepts optional metadata in the YAML frontmatter: `version`, `author`, `compatibility`. The Gateway extracts the archive, registers it in `extensions_config.json`, and makes it immediately available.

---

## Docker sandbox gives agents a real computer, not just text output

The sandbox system at `deerflow/sandbox/` defines an abstract `Sandbox` interface (`execute_command`, `read_file`, `write_file`, `list_dir`) with a `SandboxProvider` lifecycle pattern (`acquire`, `get`, `release`). Three execution modes are configured in `config.yaml`:

**Local mode** (`deerflow.sandbox.local:LocalSandboxProvider`) runs directly on the host — a singleton filesystem execution with virtual path mappings, suitable only for development. **Docker mode** (`deerflow.community.aio_sandbox:AioSandboxProvider`) creates isolated Docker containers per task with OS-level isolation (seccomp, cgroups). **Kubernetes mode** extends Docker mode with a `Provisioner` service on port 8002 that manages sandbox pods.

The virtual path system is central to how agents interact with files:

| Agent-visible path | Physical location |
|---|---|
| `/mnt/user-data/workspace/` | `backend/.deer-flow/threads/{thread_id}/user-data/workspace/` |
| `/mnt/user-data/uploads/` | `backend/.deer-flow/threads/{thread_id}/user-data/uploads/` |
| `/mnt/user-data/outputs/` | `backend/.deer-flow/threads/{thread_id}/user-data/outputs/` |
| `/mnt/skills/` | `deer-flow/skills/` |

Five sandbox tools are built in: `bash` (shell execution with path translation), `ls` (directory listing, max 2 levels), `read_file` (with optional line ranges), `write_file` (auto-creates directories), and `str_replace` (substring replacement). The `present_files` tool makes output files accessible to users, restricted to `/mnt/user-data/outputs/`.

**Per-session isolation** is thread-level: `ThreadDataMiddleware` creates directories at `backend/.deer-flow/threads/{thread_id}/`. In Docker mode, each task gets its own container. Sub-agents share the thread's sandbox filesystem but have isolated conversation contexts. Thread deletion triggers both LangGraph thread removal and Gateway cleanup of the physical directories.

---

## Memory is a JSON file with LLM-extracted facts, not a vector store

DeerFlow's long-term memory is deliberately simple. It persists as a **plain JSON file** at `backend/.deer-flow/memory.json` (configurable via `memory.storage_path`). No SQLite, no vector database. The structure has three sections:

```json
{
  "userContext": { "workContext": "...", "personalContext": "...", "topOfMind": "..." },
  "history": { "recentMonths": "...", "earlierContext": "...", "longTermBackground": "..." },
  "facts": [
    { "id": "unique-id", "content": "User prefers Python over JavaScript",
      "category": "preference", "confidence": 0.85, "createdAt": "2026-03-15T..." }
  ]
}
```

The **update workflow** is asynchronous and debounced. `MemoryMiddleware` (stage 8) filters conversation messages — user inputs and final AI responses only — and queues them. A background thread with a **30-second debounce** invokes a configurable LLM to extract updated context summaries and new discrete facts with confidence scores (categories: preference, knowledge, context, behavior, goal). The `updater.py` module writes atomically (temp file + rename) and invalidates cache on write. On the next interaction, the **top 15 facts** plus context sections are injected into `<memory>` XML tags within the system prompt.

**Deduplication is string-based, not semantic.** Before appending new facts, the updater performs whitespace-normalized exact matching on `content` fields. "User prefers Python" and "The user has a preference for Python" would be stored as separate facts. Key configuration knobs: `max_facts: 100`, `fact_confidence_threshold: 0.7`, `max_injection_tokens: 2000`.

**Compared to THE_FACTORY's tiered memory:** DeerFlow's memory is a single flat tier — no distinction between working memory, episodic memory, and semantic memory. There's no vector similarity search, no embedding-based retrieval, and no memory consolidation across abstraction levels. A TIAMAT cloud memory backend has been mentioned for enterprise persistence but is not well-documented in the repo. For sophisticated memory requirements, you'd need to build on top of the existing system or replace it.

---

## Context engineering uses four complementary strategies

DeerFlow manages context windows through a multi-layered approach:

**Sub-agent context isolation** is the primary mechanism. Each sub-agent receives only the `prompt` and `description` from its `task` tool call — not the lead agent's full conversation history. This prevents context accumulation across parallel research threads.

**SummarizationMiddleware** (stage 5, optional) triggers when approaching token limits. It compresses completed sub-task results and older conversation history. Configuration lives under `summarization` in `config.yaml` with toggles for enabled state and trigger thresholds. Full documentation exists at `backend/docs/summarization.md`.

**Filesystem offloading** is implicit. Agents write intermediate results, code outputs, and data to the sandbox filesystem via `write_file` and `bash` tools. Large outputs stay on disk rather than accumulating in conversation context. The `present_files` tool surfaces final outputs without putting their contents in the message stream.

**Progressive skill loading** keeps the base prompt small. Only skill *paths* appear in the system prompt; actual skill content is read on-demand via `read_file`.

This is architecturally sound but less structured than explicit context budgeting. There's no per-message token counting, no configurable context allocation strategy, and no automatic eviction policy beyond the summarization middleware's compression.

---

## No evaluation harness exists — this is the biggest gap

**DeerFlow 2.0 ships with zero evaluation infrastructure.** There is no `evals/` directory, no `benchmarks/` directory, no evaluation datasets, no scoring rubrics, no LLM-as-judge pipeline, and no end-to-end quality benchmarks.

The test suite at `backend/tests/` is exclusively **unit and integration testing** via pytest:

- `test_client.py` — **77 unit tests** including `TestGatewayConformance`, which validates every `DeerFlowClient` method against Gateway Pydantic response models
- `test_memory_updater.py` — regression tests for memory extraction and fact deduplication
- `test_docker_sandbox_mode_detection.py` — sandbox mode detection
- `test_provisioner_kubeconfig.py` — Kubernetes configuration
- `test_harness_boundary.py` — enforces that `deerflow.*` (harness) never imports `app.*` (architectural boundary)

CI runs via `.github/workflows/backend-unit-tests.yml` on every PR (**580+ runs** observed).

**LangSmith integration is implicit and tracing-only.** Since DeerFlow runs on LangGraph + LangChain, LangSmith tracing works automatically when standard environment variables are set. The LangGraph Server supports LangGraph Studio for local trace visualization. However, there is **no LangSmith evaluation integration** — no evaluation datasets, no evaluators, no automated scoring pipelines. No `langsmith` imports exist in the v2 codebase.

**For replacing CRUCIBLE:** DeerFlow provides none of the evaluation capabilities you'd need. You would need to build an external evaluation harness that invokes `DeerFlowClient`, captures outputs, and scores them — or continue using CRUCIBLE alongside DeerFlow.

---

## MCP integration supports OAuth and three transport types

MCP servers are configured in `extensions_config.json` under the `mcpServers` key. DeerFlow uses `langchain-mcp-adapters`' `MultiServerMCPClient` for multi-server management with **lazy initialization** and **mtime-based cache invalidation** — when the config file changes, tools are reloaded on the next request.

Three transport types are supported: **stdio** (command-based, e.g., `npx -y @modelcontextprotocol/server-github`), **SSE** (Server-Sent Events via URL), and **HTTP** (standard HTTP). For HTTP and SSE servers, DeerFlow supports **OAuth token endpoint flows** with `client_credentials` and `refresh_token` grant types, automatic token refresh, and `Authorization` header injection. All config values support `$VAR` environment variable substitution.

Runtime management is available via `GET/PUT /api/mcp/config` on the Gateway API or `client.update_mcp_config(servers)` via `DeerFlowClient`. Cross-process sync works because the Gateway (port 8001) and LangGraph Server (port 2024) both monitor `extensions_config.json` mtime. Security validations in `mcp_utils.py` protect against command injection, path traversal, and environment variable injection.

---

## The DeerFlowClient enables headless, in-process usage

Located at `deerflow/client.py`, `DeerFlowClient` provides **direct in-process access** to all DeerFlow capabilities without HTTP services or FastAPI. It imports the same `deerflow` modules that the LangGraph Server and Gateway API use, shares the same config files and data directories, and has **no FastAPI dependency**.

```python
from deerflow.client import DeerFlowClient
client = DeerFlowClient()

# Synchronous chat
response = client.chat("Analyze this dataset", thread_id="my-thread")

# Streaming (LangGraph SSE protocol)
for event in client.stream("hello"):
    if event.type == "messages-tuple" and event.data.get("type") == "ai":
        print(event.data["content"])
```

The full API surface mirrors the Gateway: `chat()`, `stream()`, `reset_agent()`, `list_models()`, `get_mcp_config()`, `update_mcp_config()`, `list_skills()`, `install_skill()`, `get_memory()`, `reload_memory()`, `upload_files()`, `get_artifact()`. The key architectural boundary — harness (`deerflow.*`) never imports app (`app.*`) — is enforced by CI tests, making the embedded client a first-class usage path.

**For programmatic pipeline integration:** This is DeerFlow's strongest hook point. You could embed `DeerFlowClient` in a Python orchestrator that sits alongside your Node.js/TypeScript stack, using it to delegate research or coding tasks while keeping your own handoff logic and evaluation harness.

---

## The Claude Code skill is a Markdown-based HTTP API guide

The `claude-to-deerflow` skill at `skills/public/claude-to-deerflow/SKILL.md` is not a code library — it's a structured Markdown document that teaches coding agents (Claude Code, OpenAI Codex, Gemini CLI, Cursor, Windsurf) how to interact with a running DeerFlow instance via `curl` commands to the Gateway API (port 8001) and LangGraph API (port 2024). It covers health checks, thread creation, streaming runs, file uploads, skill management, and memory operations. A helper script at `scripts/chat.sh` simplifies message sending. The skill is also available on the LobeHub Skills Marketplace.

This is useful but lightweight — it's essentially API documentation formatted as an agent skill. There's no bidirectional protocol, no shared state between Claude Code and DeerFlow, and no structured callback mechanism.

---

## How DeerFlow stacks up for replacing THE_FACTORY and CRUCIBLE

DeerFlow's position in the multi-agent landscape is "**LangGraph plus batteries**" — more opinionated and complete than standalone LangGraph, more technically ambitious than CrewAI, more execution-focused than AutoGen, and far more serious than OpenAI Swarm. With **~46,800 stars**, 107 contributors, and active development, it has the momentum of a project that will persist.

For your evaluation, here's how DeerFlow maps to your specific requirements:

| Your requirement | DeerFlow capability | Gap assessment |
|---|---|---|
| Multi-agent orchestration | ✅ Lead agent + `task` tool delegation, 3 concurrent sub-agents | Dynamic but untyped — no JSON Schema handoff envelopes |
| Tiered memory | ⚠️ Single-tier JSON with confidence-scored facts | No semantic deduplication, no vector retrieval, no memory tiers |
| Flow skills | ✅ SKILL.md progressive loading, .skill archives | Markdown-based, not programmatic — different paradigm from code-based skills |
| Sandboxed execution | ✅ Docker/K8s sandbox with per-thread isolation | Strong — this is DeerFlow's core differentiator |
| Evaluation harness | ❌ None — no evals, no benchmarks, no scoring | **Critical gap** — CRUCIBLE has no replacement in DeerFlow |
| JSON Schema handoff | ❌ Free-text `task` tool parameters | No structured contract validation between agents |
| Node.js/TypeScript | ❌ Python-only (LangGraph + LangChain) | Full stack migration required; `DeerFlowClient` enables Python bridge |

**The honest recommendation:** DeerFlow could replace THE_FACTORY's orchestration and execution layers if you're willing to migrate to Python and accept less structured agent handoffs. It **cannot** replace CRUCIBLE — you'd need to build evaluation on top, potentially using `DeerFlowClient` as the execution backend with your own scoring pipeline. The memory system would need significant extension for tiered semantics. The skill system is powerful but conceptually different from programmatic flow skills. The strongest case for adoption is if your pipeline needs sandboxed code execution and you want to avoid building that infrastructure yourself.

## Conclusion

DeerFlow 2.0 represents a genuinely novel architectural choice — collapsing multi-agent complexity into a single agent with a rich middleware pipeline while offloading task decomposition entirely to the LLM via tool calls. The **middleware-as-cross-cutting-concerns** pattern, the **virtual filesystem with Docker isolation**, and the **progressive skill loading** are elegant engineering. But the project is one month old, has no evaluation infrastructure, uses simplistic memory deduplication, and ties you to the LangChain ecosystem's abstraction layer and breaking-change cadence. For a team with an existing TypeScript pipeline that includes structured handoffs and an evaluation harness, the most pragmatic path is likely **selective adoption** — use DeerFlow's sandbox and skill execution via `DeerFlowClient` as a capability within your existing orchestration, rather than wholesale replacement.
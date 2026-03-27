# CRUCIBLE Adoption Analysis — What to Use vs. What to Build

**Date:** 2026-03-27
**Scope:** Analysis of the early-2026 multi-agent evaluation ecosystem mapped against CRUCIBLE's current architecture, identifying concrete adoption opportunities where real dependencies replace custom implementations.
**Source:** Landscape survey document (`CRUCIBLE_CLAUDE_reframe_for_adoption`), cross-referenced against CRUCIBLE codebase as of commit `9654bb8`.

---

## Executive Summary

CRUCIBLE currently builds most of its infrastructure from scratch: proprietary Langfuse tracing, custom loop detection, hand-authored task payloads, ad-hoc variant comparison heuristics. The ecosystem has matured enough that six real adoption opportunities exist — not convention-alignment or naming changes, but actual dependency swaps and integrations that reduce CRUCIBLE's maintenance surface while expanding its capabilities.

The highest-leverage change is exposing CRUCIBLE's sandbox as an MCP server, which opens evaluation to any MCP-capable agent without requiring CRUCIBLE-specific `AgentFn` implementations. The strongest differentiator is layering Invariant Guardrails on top of the existing embedding-based loop detector to create a three-tier detection system no other framework offers.

---

## 1. Replace Langfuse SDK with OpenTelemetry SDK

### Current State
`src/telemetry/tracer.ts` uses the Langfuse SDK directly (`langfuse.trace()`, `trace.generation()`). Custom attribute names (`variantLabel`, `tokenBudget`, `taskDescription`). Traces are locked to Langfuse — switching backends requires rewriting the tracer.

### Proposal
Add `@opentelemetry/api`, `@opentelemetry/sdk-trace-node`, and `@opentelemetry/exporter-trace-otlp-http`. Replace `RunTracer` internals with real OTel spans using `gen_ai.*` semantic convention attributes. Configure Langfuse v3 as the OTLP exporter (it natively accepts OTLP).

### What Changes
- `langfuse` npm dependency removed, replaced by `@opentelemetry/*` packages
- `RunTracer.create()` initializes an OTel `TracerProvider` with OTLP exporter pointed at Langfuse (or any OTel backend)
- `createTracerMiddleware()` creates OTel spans instead of Langfuse generations:
  - `gen_ai.operation.name` = `"chat"` for LLM calls, `"execute_tool"` for sandbox ops
  - `gen_ai.request.model` = model name
  - `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens` for token tracking
  - `gen_ai.agent.name` = variant label
- `traceToolCall()` and `traceMiddlewareEvent()` become OTel span creation
- `close()` calls `tracerProvider.shutdown()` instead of `langfuse.flushAsync()`

### Why Real Adoption, Not Convention-Alignment
Renaming Langfuse attributes to match `gen_ai.*` conventions is cosmetic — traces are still locked to Langfuse's proprietary client. Using the OTel SDK makes traces portable to any OTel-compatible backend (Datadog, Jaeger, Arize Phoenix, Grafana Tempo) via exporter configuration, with zero code changes. Langfuse v3 is built on OTel and accepts OTLP natively, so CRUCIBLE loses nothing but gains backend portability.

### Key Attributes (OTel GenAI Semantic Conventions)
| Attribute | Value | Used In |
|-----------|-------|---------|
| `gen_ai.operation.name` | `chat`, `execute_tool`, `invoke_agent` | All spans |
| `gen_ai.request.model` | e.g. `claude-opus-4-20250514` | LLM call spans |
| `gen_ai.usage.input_tokens` | integer | LLM call spans |
| `gen_ai.usage.output_tokens` | integer | LLM call spans |
| `gen_ai.agent.name` | variant label | Root span |
| `gen_ai.tool.name` | `exec`, `writeFile`, `readFile` | Tool call spans |
| `gen_ai.evaluation.score.label` | check name | Scoring spans |

### Risk
OTel GenAI semantic conventions are still **experimental** (not stable). Attribute names could change. Mitigation: wrap attribute names in constants, update in one place.

---

## 2. Integrate Invariant Guardrails for Action-Pattern Loop Detection

### Current State
`src/middleware/loopDetector.ts` is purely embedding-based: embeds the last user message via OpenAI `text-embedding-3-small`, computes mean cosine similarity against a rolling window, fires `LoopDetectedError` after N consecutive high-similarity turns. This catches rephrased identical plans but misses:
- Identical tool-call sequences (agent runs `exec("python test.py")` 5 times with same args)
- Write-revert cycles (agent writes a file, reverts it, writes the same content again)
- Stalled progress (agent keeps calling tools but producing no new artifacts)

### Proposal
Add `invariant-ai` as a dependency. Use it as a second middleware layer alongside the existing semantic detector, creating a three-tier detection stack:

**Tier 1 — Invariant rule-based detection (new dependency)**
Declarative pattern matching on tool-call sequences. Catches structural repetition that embedding similarity misses because the messages *around* the tool calls may differ.

Example rules:
- 3+ consecutive identical tool calls (same name + same arguments)
- Write-revert-write cycles on the same file path
- Repeated failed exec commands with identical arguments

**Tier 2 — Embedding similarity (existing, unchanged)**
Catches semantically identical but syntactically different messages. Already implemented and tested.

**Tier 3 — Progress tracking (build from scratch)**
Monitors whether new artifacts appear in the sandbox between turns. If N turns pass with no new files written and no test results changing, flag as stalled. No existing library covers this — it requires sandbox-aware state tracking that's specific to CRUCIBLE's `ToolContext`.

### Why Real Adoption
Invariant has solved the hard problem of declarative pattern matching with quantifiers over variable-length action sequences. Their rule language supports dynamic-length pattern matching (`(call: ToolCall){3,}` for "3 or more matching calls") and structural comparison of nested arguments. Reimplementing this from scratch is significant work and well outside CRUCIBLE's core value proposition.

### Integration Point
The `invariant-ai` package can operate as:
1. A library imported into the loop detector middleware (preferred — keeps everything in-process)
2. An MCP Gateway proxy sitting between CRUCIBLE and the LLM (heavier, but provides a dashboard)

Option 1 is cleaner: extend `LoopDetectorConfig` with an `actionPatterns` section, wire Invariant's `Policy` class into the middleware alongside the existing embedding logic.

### What CRUCIBLE Contributes (Novel)
The three-tier combination is novel. No existing framework combines rule-based action matching, embedding-based semantic detection, and artifact-aware progress tracking. The adoption doc identifies this as CRUCIBLE's strongest area for original contribution.

---

## 3. Use Inspect AI as the Benchmark Execution Layer

### Current State
`src/engine/scorer.ts` runs checks by shelling out commands in the E2B sandbox and comparing exit codes. Task payloads are hand-authored JSON with a custom `CheckSpec` format. No compatibility with any established benchmark format.

### Proposal
Add Inspect AI as a Python subprocess dependency for benchmark tasks. When a task payload includes an `inspect_task` field, delegate scoring to Inspect and consume its `EvalLog` JSON output instead of running CRUCIBLE's `CheckSpec` system.

### What Changes
- New optional field on `TaskPayload`: `inspect_task?: string` (e.g., `"swe_bench"`, `"humaneval"`)
- New function in `scorer.ts`: `runInspectScoring()` that calls `python -m inspect eval` as a subprocess, captures JSON output, and parses it into CRUCIBLE's result format
- CRUCIBLE's custom `CheckSpec` system stays for CRUCIBLE-specific checks — Inspect handles standardized benchmarks
- Task ingestion command (see proposal #6) generates tasks with `inspect_task` set

### Why Real Adoption
Inspect AI already wraps 100+ benchmarks with proper scoring infrastructure:
- SWE-bench: Docker-based test execution, patch application, FAIL_TO_PASS/PASS_TO_PASS logic
- HumanEval/MBPP: pass@k evaluation with proper sampling
- GAIA: multi-step reasoning evaluation

Reimplementing any of these is weeks of work on solved problems. Inspect's `EvalLog` schema captures full provenance: task inputs, solver pipelines, per-sample scores with explanations, aggregated metrics.

### Trade-off
Adds a Python runtime dependency. Manageable because:
- E2B sandboxes already have Python
- THE_FACTORY has Python infrastructure (`scripts/`, `.venv/`)
- Inspect is only invoked for benchmark tasks, not for custom CRUCIBLE evaluations

### Inspect AI Architecture Alignment
| Inspect Concept | CRUCIBLE Equivalent | Mapping |
|-----------------|---------------------|---------|
| `Dataset` | `TaskPayload` | Task definition |
| `Solver` | `AgentFn` + variant config | The pipeline under test |
| `Scorer` | `runChecks()` | Post-run evaluation |
| `EvalLog` | `RunResult` + `ScoreResult` | Structured output |
| `Score(value, explanation)` | `CheckResult { passed, stdout }` | Per-check result |

---

## 4. Expose Sandbox as an MCP Server

### Current State
`ToolContext` (`exec`, `writeFile`, `readFile`) is an internal facade over E2B sandbox operations. Only agents built as CRUCIBLE `AgentFn` implementations can use the sandbox. To evaluate a new agent, you must write a CRUCIBLE agent wrapper (like `src/agents/coder.ts`).

### Proposal
Add `@modelcontextprotocol/sdk` and expose `ToolContext` operations as MCP tools. This creates a new evaluation mode where CRUCIBLE provides the sandbox + kill switches + tracing, and the agent under test connects via MCP.

### What Changes
- New dependency: `@modelcontextprotocol/sdk`
- New file: `src/server/mcp.ts` — creates an `McpServer` from a `ToolContext`
- Three MCP tools exposed: `exec`, `writeFile`, `readFile` — directly wrapping `ToolContext`
- MCP resources exposed: sandbox file listing, current working directory
- New CLI mode: `npx crucible serve-mcp --task <file>` — starts a sandbox with an MCP server, waits for an external agent to connect

### What This Enables
Any MCP-capable agent (Claude Desktop, Cursor, VS Code Copilot, OpenAI agents with MCP support, custom agents) can connect to a CRUCIBLE sandbox and be evaluated without any CRUCIBLE-specific code. The kill switches (token budget, loop detection, TTL) still apply — they wrap the MCP tool responses.

This is a significant capability expansion:
- **Current:** evaluate agents you build as `AgentFn` (echo, looping, coder)
- **With MCP:** evaluate any agent that speaks MCP, including commercial products

### MCP Tool Definitions
| Tool | Description | Input Schema |
|------|-------------|-------------|
| `exec` | Execute a shell command in the sandbox | `{ command: string }` |
| `writeFile` | Write content to a file in the sandbox | `{ path: string, content: string }` |
| `readFile` | Read a file from the sandbox | `{ path: string }` |

### Architecture
```
External Agent ──MCP──> CRUCIBLE MCP Server
                              │
                        ┌─────┴─────┐
                        │ Middleware │  (token budget, loop detector, mutation guard)
                        └─────┬─────┘
                              │
                        ┌─────┴─────┐
                        │ ToolContext│  (E2B sandbox facade)
                        └─────┬─────┘
                              │
                        ┌─────┴─────┐
                        │ E2B Sandbox│
                        └───────────┘
```

---

## 5. Implement Elo/Bradley-Terry Variant Ranking (Port from Evalica)

### Current State
`src/cli/compare.ts` picks a single winner via cascading heuristics: completed > pass rate > fewer tokens > faster. No statistical ranking. No confidence intervals. No way to rank variants across multiple task runs.

### Proposal
Port Evalica's core ranking algorithms to TypeScript. The math is well-documented and compact (~50 lines per algorithm). Add a `rank` CLI command.

### What Changes
- New file: `src/engine/ranking.ts` — Elo update function, Bradley-Terry MLE via iterative algorithm
- New CLI command: `npx crucible rank --runs-dir ./runs/comparisons/`
- Reads all `ComparisonResult` JSON files, extracts pairwise outcomes, produces ranked leaderboard with confidence intervals

### Algorithms
**Elo rating:** Standard chess-style rating with configurable K-factor. Each comparison produces a pairwise result; Elo ratings update after each.

**Bradley-Terry:** Maximum likelihood estimation of variant strength parameters from pairwise comparison data. More statistically rigorous than Elo for batch comparison (all comparisons known upfront).

### Why Port Instead of Subprocess
Evalica is Python and its value is the algorithms, not the library surface area. The algorithms are mathematically simple and well-documented. A native TS implementation avoids a Python dependency for this narrow use case (unlike Inspect AI, where the wrapped benchmark infrastructure is massive).

### Output Format
```json
{
  "rankings": [
    { "variant": "factory-baseline", "elo": 1523, "bradleyTerry": 0.72, "wins": 8, "losses": 2, "ties": 0 },
    { "variant": "bare", "elo": 1477, "bradleyTerry": 0.28, "wins": 2, "losses": 8, "ties": 0 }
  ],
  "comparisons": 10,
  "tasks": ["example-coding", "bugfix-cross-file-diagnosis", "..."]
}
```

---

## 6. Add SWE-bench Task Ingestion

### Current State
Tasks are hand-authored JSON files in `tasks/`. No way to import from existing benchmark datasets. Task format is CRUCIBLE-specific with no cross-benchmark compatibility.

### Proposal
Add an `ingest` CLI command that pulls SWE-bench instances from HuggingFace and converts them to CRUCIBLE task payloads.

### What Changes
- New CLI command: `npx crucible ingest --source swe-bench --dataset princeton-nlp/SWE-bench_Verified --limit 10`
- Pulls JSONL instances from HuggingFace datasets API
- Converts each instance to a CRUCIBLE `TaskPayload`:
  - `instance_id` → preserved as metadata
  - `problem_statement` → `description` + `instructions`
  - `repo` + `base_commit` → `seedDir` (clone and checkout)
  - `FAIL_TO_PASS` → generated `CheckSpec` entries
  - `PASS_TO_PASS` → generated `CheckSpec` entries
  - `patch` → stored as metadata for reference scoring
- Writes task files to `tasks/swe-bench/<instance_id>.json`
- Optionally sets `inspect_task: "swe_bench"` for delegated scoring (see proposal #3)

### Extended TaskPayload Fields
```typescript
interface TaskPayload {
  // Existing fields (unchanged)
  description: string;
  instructions: string;
  files?: Record<string, string>;
  seedDir?: string;
  networkAllowlist?: string[];
  checks?: CheckSpec[];

  // New: benchmark interop
  inspect_task?: string;         // Inspect AI task ID for delegated scoring
  instance_id?: string;          // SWE-bench instance identifier
  repo?: string;                 // Git repo (e.g., "django/django")
  base_commit?: string;          // Commit hash to checkout
  FAIL_TO_PASS?: string[];       // Tests that should flip from fail to pass
  PASS_TO_PASS?: string[];       // Tests that must stay passing

  // New: decomposition hints
  decomposition?: {
    strategy?: string;
    constraints?: Record<string, unknown>;
  };
}
```

### Why This Matters
Without actual ingestion, SWE-bench-compatible fields in TaskPayload are dead code. With ingestion, CRUCIBLE can immediately benchmark against the same tasks other agent frameworks use (SWE-agent, Devin, OpenHands, Agentless), producing directly comparable results.

---

## Priority Ranking

| Priority | Proposal | Effort | Impact | Rationale |
|----------|----------|--------|--------|-----------|
| 1 | MCP server (#4) | Medium | Very High | Opens CRUCIBLE to the entire MCP agent ecosystem. Highest leverage single change. |
| 2 | Invariant loop detection (#2) | Medium | High | CRUCIBLE's core differentiator. Three-tier detection is novel — no other framework does this. |
| 3 | OTel SDK (#1) | Medium | High | Replaces proprietary lock-in with a standard. Every trace becomes portable. |
| 4 | SWE-bench ingestion (#6) | Low | High | Unlocks the largest benchmark ecosystem. Low effort because it's a format converter. |
| 5 | Inspect AI scoring (#3) | Medium | Medium | Removes need to reimplement benchmark scoring. Depends on #6 for task availability. |
| 6 | Elo/Bradley-Terry (#5) | Low | Medium | Improves comparison rigor. Most valuable once there are enough runs to rank. |

---

## 7. Add Prometheus Metrics Exporter to OTel Pipeline

### Current State
Proposal #1 replaces Langfuse SDK with OTel SDK and exports traces via OTLP. But traces alone don't cover operational metrics: sandbox startup latency, active run count, token burn rate per run, middleware rejection counts (loop detected, budget exceeded). These are time-series concerns, not trace concerns.

### Proposal
Extend the OTel setup from #1 with `@opentelemetry/sdk-metrics` and `@opentelemetry/exporter-prometheus`. Expose a `/metrics` endpoint on the existing Fastify server that Prometheus can scrape.

### What Changes
- New dependencies: `@opentelemetry/sdk-metrics`, `@opentelemetry/exporter-prometheus`
- `src/server/index.ts` gets a `/metrics` route serving the Prometheus exporter
- Key metrics (counters and histograms):
  - `crucible_runs_total` (counter, labels: `status`, `variant`)
  - `crucible_run_duration_seconds` (histogram, labels: `variant`, `task`)
  - `crucible_tokens_used_total` (counter, labels: `variant`, `direction`)
  - `crucible_sandbox_startup_seconds` (histogram)
  - `crucible_loop_detections_total` (counter, labels: `tier`)
  - `crucible_budget_exceeded_total` (counter)

### Why This Extends #1
Proposal #1 handles traces (individual request/span data). Prometheus handles aggregated time-series metrics (rates, percentiles, alerting). They're complementary layers in OTel — both use the same `TracerProvider`/`MeterProvider` initialization. Adding metrics is incremental once #1 is done.

### Trade-off
Adds a Prometheus server dependency for anyone who wants dashboards. But the `/metrics` endpoint is passive — it works with or without a scraper. Effort: Low (incremental to #1).

---

## 8. Add OpenAPI Spec Generation to Fastify Server

### Current State
`src/server/` uses Fastify with routes in `routes/runs.ts` and `routes/ws.ts`. No API documentation or schema validation on endpoints. Clients must read source code to understand the API.

### Proposal
Add `@fastify/swagger` and `@fastify/swagger-ui`. Fastify's plugin system auto-generates OpenAPI 3.0 specs from route schemas, with zero manual spec authoring.

### What Changes
- New dependencies: `@fastify/swagger`, `@fastify/swagger-ui`
- Route handlers in `routes/runs.ts` get Fastify JSON Schema annotations on request/response
- `/docs` endpoint serves Swagger UI
- OpenAPI spec available at `/docs/json` for client codegen

### Why Real Adoption
CRUCIBLE already has a Fastify HTTP server. Fastify's schema system validates requests at the framework level (faster than middleware validation) and generates OpenAPI for free. This isn't adding a new concern — it's leveraging infrastructure CRUCIBLE already depends on.

### Trade-off
Minimal. Schema annotations on routes are a few lines each. The plugins are maintained by the Fastify team. Effort: Low.

---

## 9. Add JSON Schema for Task Payloads and Variant Configs

### Current State
`tasks/*.json` and `variants/*.yaml` files have no formal schema. Validation is ad-hoc in `src/engine/validation.ts`. Users authoring new tasks get no IDE autocompletion or early error detection. The `TaskPayload` TypeScript interface exists but isn't exposed as a JSON Schema.

### Proposal
Generate JSON Schemas from the TypeScript types (`TaskPayload`, `VariantConfig`, `CheckSpec`) and publish them alongside the task/variant files. Use `$schema` references in JSON/YAML files for IDE support.

### What Changes
- Add `typescript-json-schema` or `ts-json-schema-generator` as a dev dependency
- Build step generates `schemas/task-payload.schema.json`, `schemas/variant-config.schema.json`
- `src/engine/validation.ts` uses `ajv` (already a transitive dep via Fastify) to validate against these schemas at runtime
- Task JSON files get a `"$schema": "../schemas/task-payload.schema.json"` reference
- Variant YAML files get a comment pointing to the schema

### Why Real Adoption
This converts CRUCIBLE's TypeScript types into a portable validation contract. External tools, CI pipelines, and users creating tasks all benefit from the same schema. The schema also documents the extended `TaskPayload` fields from proposal #6 (SWE-bench fields) without requiring users to read TypeScript source.

### Trade-off
Schema generation adds a build step. Schemas must stay in sync with types (automate this). Effort: Low.

---

## 10. Containerize with Docker

### Current State
No Dockerfile exists. Running CRUCIBLE requires a local Node.js setup, manual dependency installation, and environment variable configuration for E2B, Langfuse, and OpenAI keys. THE_FACTORY's `.venv` is Python — CRUCIBLE's Node runtime is separate.

### Proposal
Add a multi-stage Dockerfile that produces a minimal production image. Add `docker-compose.yml` for local development with Prometheus and Langfuse backends.

### What Changes
- New file: `Dockerfile` — multi-stage build (build stage with `npm ci && npm run build`, runtime stage with `node:18-slim`)
- New file: `docker-compose.yml` — CRUCIBLE server + Prometheus + Grafana (optional) + Langfuse (optional)
- `.dockerignore` excludes `node_modules`, `dist`, `data/`, `.env`
- npm script: `npm run docker:build`, `npm run docker:up`

### Why Real Adoption
Docker is the universal packaging format. It makes CRUCIBLE installable with a single `docker run` command instead of requiring Node.js, npm, and environment setup. Combined with proposal #4 (MCP server), a Docker image lets anyone spin up a CRUCIBLE sandbox evaluator and point their MCP agent at it.

### Trade-off
Docker adds ~100MB to the distribution (Node.js slim base). E2B SDK calls out to E2B's cloud service, so the sandbox itself isn't containerized — but the harness orchestration is. Effort: Low.

---

## 11. Structured LLM Output via JSON Schema

### Current State
`src/engine/llm.ts` uses OpenAI for embeddings only. `src/engine/PromptBuilder.ts` constructs prompts for agent LLM calls, but the graph executor's own LLM interactions (if any — e.g., for complexity estimation, question generation, or adaptive strategy selection) parse free-text responses.

### Proposal
Where CRUCIBLE itself calls an LLM (not the agent under test, but CRUCIBLE's own orchestration logic), use OpenAI's structured output mode (`response_format: { type: "json_schema", json_schema: {...} }`) to guarantee parseable responses.

### What Changes
- `src/engine/ComplexityEstimator.ts` — if it uses LLM calls, define a `ComplexityEstimate` JSON schema and use structured output
- `src/engine/QuestionGenerator.ts` — define a `GeneratedQuestions` schema
- `src/engine/strategies/D5Strategy.ts` — if adaptive decisions involve LLM reasoning, schema-constrain the output
- Shared schemas live alongside the JSON Schemas from proposal #9

### Why Real Adoption
Structured output eliminates regex/string parsing of LLM responses in orchestration code. The JSON schema constraint is enforced by the API — invalid JSON is impossible, not just unlikely. This is particularly valuable for CRUCIBLE because orchestration failures in the harness (as opposed to the agent under test) are infrastructure bugs that undermine trust in results.

### Trade-off
Only applicable where CRUCIBLE itself makes LLM calls (not the evaluated agent). Requires OpenAI models that support structured output. Effort: Low where applicable.

---

## Updated Priority Ranking

| Priority | Proposal | Effort | Impact | Rationale |
|----------|----------|--------|--------|-----------|
| 1 | MCP server (#4) | Medium | Very High | Opens CRUCIBLE to the entire MCP agent ecosystem. |
| 2 | Invariant loop detection (#2) | Medium | High | Three-tier detection is CRUCIBLE's core differentiator. |
| 3 | OTel SDK (#1) + Prometheus metrics (#7) | Medium | High | Portable traces + operational metrics in one pass. |
| 4 | SWE-bench ingestion (#6) | Low | High | Unlocks the largest benchmark ecosystem. |
| 5 | Docker containerization (#10) | Low | High | Makes CRUCIBLE installable with one command. Enables #4. |
| 6 | JSON Schema for payloads (#9) + OpenAPI (#8) | Low | Medium | Schema-validates everything: tasks, configs, HTTP API. |
| 7 | Inspect AI scoring (#3) | Medium | Medium | Delegates benchmark scoring. Depends on #6. |
| 8 | Elo/Bradley-Terry (#5) | Low | Medium | Statistical ranking rigor. |
| 9 | Structured LLM output (#11) | Low | Low-Medium | Hardens orchestration LLM calls. Narrow applicability. |

---

## What Stays Custom (and Should)

Not everything should be adopted. These CRUCIBLE components have no adequate external equivalent:

- **DecompositionGraph data model** — No standard exists. CRUCIBLE's `types/graph.ts` with `DecompositionNode`, `DependencyEdge`, and coupling analysis is genuinely novel.
- **Pipeline variant comparison framework** — The search space of "decomposition strategies x verification formulas x coordination topologies" has no external parallel.
- **Convergent teardown** — `src/sandbox/teardown.ts` is architecture-specific and correct. No reason to change.
- **Middleware composition** — `composeMiddleware()` is simple, correct, and matches CRUCIBLE's specific needs. No framework does this better for this use case.
- **MutationTracker / MutationGuard** — THE_FACTORY-specific enforcement. No external tool covers this.

---

## Dependency Impact Summary

### New Dependencies (if all proposals adopted)
| Package | Purpose | Size Impact | Proposal |
|---------|---------|-------------|----------|
| `@opentelemetry/api` | Trace API | ~200KB | #1 |
| `@opentelemetry/sdk-trace-node` | Trace SDK | ~300KB | #1 |
| `@opentelemetry/exporter-trace-otlp-http` | OTLP export | ~150KB | #1 |
| `@opentelemetry/sdk-metrics` | Metrics API | ~200KB | #7 |
| `@opentelemetry/exporter-prometheus` | Prometheus scrape endpoint | ~100KB | #7 |
| `@modelcontextprotocol/sdk` | MCP server | ~100KB | #4 |
| `invariant-ai` | Rule-based loop detection | ~TBD | #2 |
| `@fastify/swagger` | OpenAPI spec generation | ~150KB | #8 |
| `@fastify/swagger-ui` | Swagger UI | ~2MB (static assets) | #8 |

### New Dev Dependencies
| Package | Purpose | Proposal |
|---------|---------|----------|
| `ts-json-schema-generator` | Generate JSON Schema from TS types | #9 |

### Removed Dependencies
| Package | Replaced By |
|---------|------------|
| `langfuse` | `@opentelemetry/*` (Langfuse becomes an OTLP backend, not a client dependency) |

### Unchanged Dependencies
`e2b`, `commander`, `openai` (still needed for embeddings), `fastify`, `better-sqlite3`, `yaml`

---

## What the GPT Analysis Proposed That Was Not Adopted

For completeness, the GPT migration document also recommended these items which were **not** added to CRUCIBLE's roadmap:

- **MLflow for experiment tracking** — CRUCIBLE's experiment tracking is tightly integrated with THE_FACTORY's run record system (`.agent/runs.jsonl`, `scripts/assess.py`, `scripts/experiment.py`). MLflow would create a parallel tracking system with no clear benefit over the existing one. CRUCIBLE doesn't train models — it evaluates agents.
- **Kubernetes orchestration** — Premature. CRUCIBLE is a single-service harness, not a microservices fleet. Docker (#10) is sufficient. K8s can be revisited if CRUCIBLE scales to distributed evaluation.
- **gRPC** — CRUCIBLE's Fastify HTTP server is adequate. gRPC adds protobuf compilation, stub generation, and browser incompatibility for marginal latency gains on a harness that spends 99% of its time waiting on LLM API calls and sandbox execution.
- **Agent Client Protocol (ACP)** — CRUCIBLE is an evaluation harness, not an IDE agent. MCP (#4) is the correct protocol for CRUCIBLE's use case (exposing tools to external agents). ACP solves a different problem (agent-editor communication).
- **S3-compatible storage** — Run artifacts are small JSON files stored locally. THE_FACTORY's `runs/` directory and SQLite (`data/`) are adequate. S3 adds operational complexity (credentials, bucket management) for storage volumes CRUCIBLE doesn't generate. Revisit if run artifacts grow to include large model checkpoints or dataset snapshots.

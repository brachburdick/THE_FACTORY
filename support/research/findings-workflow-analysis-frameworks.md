# Workflow Analysis & Classification Frameworks: Research Findings

**Date:** 2026-03-21
**Scope:** Frameworks for analyzing multi-agent AI software development pipeline
**Context:** Solo operator coordinating multiple AI agents (Claude Code) to build SCUE

---

## 0. Available Data Inventory

Before recommending frameworks, here's what conversation/process data actually exists and what format it's in.

### Claude Code Conversation Logs

**Location:** `~/.claude/projects/{path-encoded-cwd}/{session-id}.jsonl`

Each session is a JSONL file. Across all projects: **134 sessions, ~39,000 lines, ~211 MB**.

**Message types and counts (THE_FACTORY project alone, 47 sessions, ~13K lines):**
| Type | Count | Description |
|------|-------|-------------|
| `user` | 2,658 | Human operator messages. Fields: `message.content`, `timestamp`, `sessionId`, `cwd`, `permissionMode`, `gitBranch`, `version` |
| `assistant` | 3,699 | Agent responses. `message.content` is an array of blocks: `thinking`, `text`, `tool_use`, `tool_result` |
| `progress` | 5,817 | Real-time tool execution progress (file reads, searches, etc.) |
| `system` | 203 | Hook events, stop reasons, errors |
| `queue-operation` | 516 | Enqueue/dequeue of messages (for concurrent agent management) |
| `last-prompt` | 62 | Truncated echo of last user prompt |
| `file-history-snapshot` | 3 | File backup snapshots |

**Key schema details:**
- Every message has `uuid`, `parentUuid` (conversation threading), `timestamp`, `sessionId`
- Assistant messages contain `tool_use` blocks with `name` (Read, Write, Edit, Bash, Grep, Glob, etc.) and `input` parameters
- `isSidechain` boolean distinguishes sub-agent work from main conversation
- `permissionMode` on user messages tracks the agent's permission level
- `cwd` and `gitBranch` provide workspace context per message

**What's NOT in the logs:**
- No explicit task-type or intent classification
- No structured outcome/success annotation
- No cost/token data per message (only per-request in some assistant messages)
- No explicit handoff markers between "sessions" or "agents"

### History File

**Location:** `~/.claude/history.jsonl` — 43 lines, one per user prompt across all sessions. Fields: `display` (prompt text), `timestamp`, `project`, `sessionId`. Lightweight index into sessions.

### Session Files

**Location:** `~/.claude/sessions/{pid}.json` — maps OS process IDs to session UUIDs. Fields: `pid`, `sessionId`, `cwd`, `startedAt`.

### .agent/ Task & Run Tracker

**Location:** `.agent/tasks.jsonl` (16 lines), `.agent/runs.jsonl` (6 lines). Structured JSONL with task status, flow phases, outcomes. Small but growing.

### Git History

Standard git log. Commits include phase-boundary commits per the constitution's git protocol.

### Summary

| Data Source | Format | Volume | Extraction Effort |
|---|---|---|---|
| Conversation logs | JSONL, rich schema | 211 MB / 134 sessions | Low — already structured, parseable with `jq` or Python |
| History index | JSONL, minimal | 43 entries | Trivial |
| Task tracker | JSONL | 16 tasks | Trivial |
| Run records | JSONL | 6 runs | Trivial |
| Git history | git log / diff | ~30 commits | Low — `git log --format` |
| Protocol improvement log | Markdown | 1 file | Manual extraction |

**Bottom line:** The conversation logs are the richest data source. They contain full tool-use traces, timestamps, threading, and workspace context. The main gap is classification — nothing is pre-labeled with intent, outcome, or activity type. Any analysis framework needs to either (a) classify retroactively, or (b) inject classification at capture time.

---

## 1. Framework Catalog

### Layer 1: Interaction Analysis

#### 1.1 Bales' Interaction Process Analysis (IPA)

- **Origin:** Robert Freed Bales, 1950, social psychology
- **What it analyzes:** Group interaction dynamics — classifies every utterance into 12 categories across task-oriented (gives/asks for information, opinion, suggestion) and socio-emotional (agrees, disagrees, shows tension, shows solidarity) dimensions
- **Data requirements:** Transcript of all interactions, coded per-utterance
- **Granularity:** Per-utterance
- **Tooling:** Manual coding or LLM-assisted coding. No specialized software required
- **Relevance:** **MEDIUM** — The socio-emotional categories (tension, solidarity) are less meaningful for human-AI interaction, but the task-oriented categories (information exchange, opinion, suggestion) map well to operator-agent dialogue. The ask/give distinction is particularly useful for understanding directive vs. collaborative interaction patterns
- **Effort:** Lightweight (days to set up coding scheme, ongoing per-session effort depends on automation)

#### 1.2 Speech Act Theory / FIPA ACL Performatives

- **Origin:** Searle (1969), Austin (1962) — philosophy of language. FIPA ACL (Foundation for Intelligent Physical Agents, 1997-2002) — multi-agent systems
- **What it analyzes:** The communicative intent behind each message. FIPA defines performatives: `request`, `inform`, `confirm`, `query`, `propose`, `accept`, `reject`, `not-understood`
- **Data requirements:** Message transcript with sender/receiver identification
- **Granularity:** Per-message or per-utterance
- **Tooling:** Can be applied manually or with LLM classification. FIPA ACL is a formal spec but the performative taxonomy can be used as a coding scheme without implementing the full protocol
- **Relevance:** **HIGH** — Maps directly to operator-agent interaction. Every operator message is classifiable as request/query/inform/confirm. Every agent response is classifiable as inform/propose/confirm/not-understood. The performative taxonomy is both formal enough to be machine-applicable and intuitive enough for manual coding
- **Effort:** Lightweight (days). The performative list is short and well-defined

#### 1.3 Malone & Crowston's Coordination Theory

- **Origin:** Thomas Malone & Kevin Crowston, MIT, 1994. ACM Computing Surveys
- **What it analyzes:** Coordination as managing dependencies between activities. Identifies dependency types (shared resources, producer-consumer, simultaneity, task-subtask) and coordination mechanisms for each
- **Data requirements:** Activity log showing what tasks were performed, by whom, and what dependencies existed between them
- **Granularity:** Per-task or per-activity (not per-utterance)
- **Tooling:** Conceptual framework — applied analytically, not with specialized tools
- **Relevance:** **HIGH** — The dependency taxonomy maps directly to multi-agent pipeline coordination. Producer-consumer dependencies (architect produces spec → developer consumes it), shared resource dependencies (multiple agents editing same files), task-subtask decomposition (operator decomposes feature into agent tasks). This framework answers "what coordination is needed?" which is prerequisite to "is the coordination happening?"
- **Effort:** Moderate (weeks). Requires mapping the actual dependency structure of the pipeline, then comparing against observed coordination patterns

#### 1.4 Human-AI Collaboration Interaction Pattern Taxonomy

- **Origin:** Frontiers in Computer Science, 2024. Systematic review of interaction patterns in AI-assisted decision making
- **What it analyzes:** Classifies interaction patterns along dimensions of user control/initiative, task nature, level of automation, and interaction mode
- **Data requirements:** Interaction transcripts with role identification
- **Granularity:** Per-interaction-episode (higher than per-utterance)
- **Tooling:** Coding scheme, no specialized tools
- **Relevance:** **HIGH** — Directly addresses the operator-agent interaction pattern. The taxonomy distinguishes human-initiated vs. AI-initiated actions, level of automation, and collaborative vs. directive modes. Recent (2024) and specifically designed for human-AI contexts
- **Effort:** Lightweight (days)

#### 1.5 Shared Mental Models / Transactive Memory Systems

- **Origin:** Cannon-Bowers et al. (1993) — shared mental models. Wegner (1987) — transactive memory. Extended to human-AI teams: Ergonomics journal (2022)
- **What it analyzes:** Whether team members share a common understanding of the task, the team, and each other's expertise. TMS specifically addresses "who knows what"
- **Data requirements:** Behavioral indicators in communication (explicit knowledge references, delegation patterns, correction frequency) or survey instruments
- **Granularity:** Per-session or per-project
- **Tooling:** Behavioral coding of transcripts, or survey instruments (not applicable to AI agents directly)
- **Relevance:** **MEDIUM** — The concept is valuable (does the operator have an accurate model of what each agent can/can't do? Do agents maintain context across sessions?) but measurement is challenging because AI agents don't have persistent mental models in the traditional sense. The breakdown indicators (misalignment, repeated corrections, scope violations) are measurable proxies
- **Effort:** Moderate (weeks to define proxy measures and validate)

#### 1.6 ChatCollab Collaboration Dynamics Analysis

- **Origin:** Carnegie Mellon / arXiv, December 2024
- **What it analyzes:** Collaboration dynamics between humans and AI agents in software teams. Proposes automated methods for identifying behavioral characteristics of agents with distinct roles (CEO, PM, developer). Measures suggestion frequency, task engagement, communication patterns
- **Data requirements:** Chat-based interaction logs with role labels
- **Granularity:** Per-message, aggregated per-role
- **Tooling:** Automated analysis via Slack logs; adaptable to any structured chat log
- **Relevance:** **HIGH** — Directly applicable. Same domain (software development), same setup (human + AI agents with roles). Their automated behavioral analysis method could be adapted to Claude Code conversation logs
- **Effort:** Moderate (weeks to adapt their methodology to Claude Code's log format)

#### 1.7 Contract Net Protocol (CNP)

- **Origin:** Reid Smith, 1980. Multi-agent systems
- **What it analyzes:** Task allocation via announce-bid-award cycle. Manager announces task, contractors bid, manager awards contract
- **Data requirements:** Task allocation events with roles
- **Granularity:** Per-task-allocation
- **Tooling:** Conceptual framework
- **Relevance:** **LOW-MEDIUM** — The operator's current workflow IS essentially a manual Contract Net: operator announces task (prompt), agent "bids" (begins work), operator evaluates result. But the protocol is designed for competitive multi-bidder scenarios which don't apply here. The concepts of task announcement structure and result evaluation are useful
- **Effort:** Lightweight (days to map existing patterns)

#### 1.8 MAST: Multi-Agent System Failure Taxonomy

- **Origin:** Cemri, Pan, Yang et al. (2025). "Why Do Multi-Agent LLM Systems Fail?" arXiv:2503.13657, ICLR 2025. Built from 1,600+ annotated traces across 7 MAS frameworks (ChatDev, MetaGPT, AutoGen, etc.)
- **What it analyzes:** 14 failure modes across 3 clusters:
  - **System Design Issues:** Unclear roles/instructions, inadequate error handling, inadequate capability assignment, inflexible workflow, missing specialization
  - **Inter-Agent Misalignment:** Specification misalignment, output format misalignment, capability misalignment, context loss between agents, premature task completion signaling
  - **Task Verification:** Inadequate output validation, missing hallucination detection, insufficient test coverage, lack of iterative refinement
- **Data requirements:** Conversation/trace logs from multi-agent runs. LLM-as-judge pipeline developed for automated classification (94% accuracy vs. human experts, Cohen's kappa = 0.77)
- **Granularity:** Per-task-run (episode level)
- **Tooling:** MAST GitHub repo includes dataset and annotation pipeline. Classifiable with LLM
- **Relevance:** **HIGH** — Purpose-built for LLM-based agents doing software development. The failure categories are immediately recognizable in this pipeline. Unlike classical frameworks, MAST was derived empirically from actual LLM agent logs. Limitation: characterizes failures only, not the quality of successful coordination
- **Effort:** Lightweight-moderate (days to apply published classifier to existing logs; weeks to extend with pipeline-specific failure modes)

#### 1.9 Conversation-for-Action (Winograd & Flores)

- **Origin:** Terry Winograd & Fernando Flores, "Understanding Computers and Cognition" (1986)
- **What it analyzes:** A 4-state loop model of action through conversation: request → promise → completion → acknowledgment. Breakdowns occur when any link fails: request misunderstood, promise not made, completion not achieved, acknowledgment reveals mismatch
- **Data requirements:** Conversation logs with role identification
- **Granularity:** Per-task-delegation cycle
- **Relevance:** **HIGH** — Maps directly onto operator→agent task delegation. Each cycle can be coded: complete (all 4 states), incomplete (which state failed?). Lightweight and immediately actionable
- **Effort:** Lightweight (days). The 4-state coding scheme is trivially applicable

#### 1.10 Mixed-Initiative Interaction (Horvitz)

- **Origin:** Eric Horvitz, Microsoft Research, CHI 1999. "Principles of Mixed-Initiative User Interfaces"
- **What it analyzes:** Balance of initiative between human and automated system. 12 principles including: introduce automation only when it adds value, make uncertainty visible, allow user to interrupt/override, learn from corrections
- **Data requirements:** Conversation logs with turn-level initiative classification (who is driving: operator or agent?)
- **Granularity:** Per-turn, aggregated per-session
- **Relevance:** **HIGH** as normative/evaluative framework. Measurable: initiative balance ratio (agent-initiated vs. operator-initiated moves per task type). Key diagnostic: agents that don't surface uncertainty (violating principle 7) produce harder-to-diagnose failures
- **Effort:** Lightweight (days). Initiative coding is binary/ternary

---

### Layer 2: Construction Analysis

#### 2.1 Process Mining (van der Aalst)

- **Origin:** Wil van der Aalst, Eindhoven University of Technology, 2004+. Seminal book: "Process Mining: Data Science in Action" (2016)
- **What it analyzes:** Discovers, monitors, and improves processes by extracting knowledge from event logs. Three types: discovery (build model from log), conformance checking (compare model to log), enhancement (extend model with log data)
- **Data requirements:** Event log in XES format or equivalent. Minimum: case ID, activity name, timestamp. Recommended: resource/actor, additional attributes
- **Granularity:** Per-event (each tool call, each commit, each message)
- **Tooling:** ProM (open source, academic), Disco/Fluxicon (commercial, lightweight), PM4Py (Python library, scriptable). For this use case, PM4Py is most practical
- **Relevance:** **HIGH** — The conversation logs already contain event-level data (tool calls with timestamps, session IDs as case IDs). A minimal process mining pipeline: extract tool-call events → assign activity labels → run discovery algorithm → visualize process model. This would show the actual flow of how agents build software (read → think → edit → test → commit vs. read → edit → read → edit → edit → manual-fix cycles)
- **Effort:** Moderate (weeks). Requires ETL from conversation logs to XES/event-log format, then running discovery. PM4Py can do this with ~100 lines of Python
- **Minimum viable version:** Extract just tool_use events from conversation logs, classify into activity types (read, search, edit, write, execute, communicate), generate directly-follows graph. This is a few hours of work

#### 2.2 Poppendieck's Seven Wastes of Software Development

- **Origin:** Mary & Tom Poppendieck, "Lean Software Development" (2003). Adapted from Toyota Production System
- **What it analyzes:** Seven categories of waste: (1) Partially done work, (2) Extra features, (3) Relearning, (4) Handoffs, (5) Task switching, (6) Delays, (7) Defects
- **Data requirements:** Process observations — can be derived from task tracker, conversation logs (re-reading same files = relearning), git history (reverts = defects), run records (multiple attempts = rework)
- **Granularity:** Per-task or per-value-stream
- **Tooling:** Conceptual framework. Value stream maps can be drawn manually or with any diagramming tool
- **Relevance:** **HIGH** — Every waste category is observable in the current pipeline:
  - *Partially done work:* Tasks stuck in "partial" status in runs.jsonl
  - *Relearning:* Agent re-reading files it read in a prior session (no persistent memory)
  - *Handoffs:* Operator translating architect output into developer prompt
  - *Task switching:* Operator context-switching between agent sessions
  - *Delays:* Time between operator prompt and agent completion
  - *Defects:* Incidents in incidents.jsonl, rework in runs.jsonl
- **Effort:** Lightweight (days). Can start immediately by tagging existing task/run data with waste categories

#### 2.3 Value Stream Mapping (VSM)

- **Origin:** Toyota Production System / Lean Manufacturing. Applied to software by Poppendieck (2003) and Reinertsen (2009)
- **What it analyzes:** Maps the flow of work from request to delivery. Distinguishes value-adding time (actually building) from non-value-adding time (waiting, context switching, rework). Identifies bottlenecks and wait states
- **Data requirements:** For each unit of work: timestamps at each stage transition, processing time vs. wait time
- **Granularity:** Per-feature or per-task
- **Tooling:** Can be done on paper or whiteboard. For data-driven VSM, need timestamped stage transitions
- **Relevance:** **HIGH** — A value stream map of "operator has idea → spec → task → agent session → code → test → merge" would immediately reveal where time is spent. The conversation logs have timestamps. Git has commit timestamps. Task tracker has status transitions. Combining these gives a rough but useful VSM
- **Effort:** Lightweight (days for manual mapping of a few features; weeks for automated extraction)

#### 2.4 Personal Software Process (PSP) / Team Software Process (TSP)

- **Origin:** Watts Humphrey, Carnegie Mellon SEI, 1995/2000
- **What it analyzes:** Individual developer process metrics: time in phase (design, code, compile, test, postmortem), defect injection/removal rates, size estimation accuracy, yield (% defects found before test)
- **Data requirements:** Time logs per activity phase, defect logs with injection phase and removal phase
- **Granularity:** Per-task, per-phase
- **Tooling:** Originally paper forms; modern tools exist but are heavyweight
- **Relevance:** **MEDIUM** — The phase-tracking concept maps to the flow skills (reproduce → diagnose → fix → verify). Defect injection/removal tracking maps to the incident tracking. But PSP was designed for solo human developers with manual time logging, which doesn't translate 1:1 to an agent pipeline. The metrics framework (yield, A/FR ratio) is more useful than the process itself
- **Effort:** Moderate (weeks to adapt metrics to agent pipeline)

#### 2.5 Artifact Traceability / Requirements Traceability Matrix

- **Origin:** IEEE 830 (requirements specs), DO-178B (avionics), MIL-STD-498. Mainstream SE since 1990s
- **What it analyzes:** Traces the lineage of artifacts: requirement → design decision → implementation → test → verification. Identifies gaps (untested requirements, untraced code)
- **Data requirements:** Linkable artifact IDs across layers (requirement IDs, task IDs, commit hashes, test names)
- **Granularity:** Per-artifact
- **Tooling:** Can be done in a spreadsheet. Tools: Jama, DOORS, or custom scripts
- **Relevance:** **MEDIUM** — The pipeline already has partial traceability: tasks.jsonl → runs.jsonl → git commits. Missing links: feature request → task decomposition, task → specific code changes, code → test coverage. Adding explicit linkage would enable "which requirement caused this rework?" analysis
- **Effort:** Moderate (weeks to establish linking conventions; ongoing discipline to maintain)

#### 2.6 Design Rationale Systems (IBIS / QOC)

- **Origin:** Kunz & Rittel (IBIS, 1970), MacLean et al. (QOC, 1991)
- **What it analyzes:** Captures the reasoning behind design decisions: Issues (questions), Positions/Options (alternatives considered), Arguments/Criteria (rationale for selection)
- **Data requirements:** Decision records — can be extracted from conversation logs where operator and agent discuss alternatives
- **Granularity:** Per-decision
- **Tooling:** Can be captured as structured notes. Tools: Compendium, or MADR (Markdown ADR) template already in the constitution
- **Relevance:** **MEDIUM** — The ADR mechanism in the constitution already captures major decisions. IBIS/QOC would add structure to the smaller, more frequent decisions embedded in agent conversations (e.g., "should we use WebSocket or polling?" discussions that happen mid-session and are lost)
- **Effort:** Lightweight (days) if extracting from existing conversations; Moderate (weeks) if building capture into the workflow

#### 2.7 Rework / Defect Causal Analysis

- **Origin:** Various — IEEE 1044 (anomaly classification), Orthogonal Defect Classification (Chillarege, IBM, 1992)
- **What it analyzes:** Classifies defects by type, trigger, impact, and root cause. ODC specifically uses orthogonal categories: defect type (assignment, checking, interface, timing, algorithm, function, documentation) and trigger (what activity exposed the defect)
- **Data requirements:** Defect records with classification fields. For ODC: ~3 minutes per defect to classify retrospectively
- **Granularity:** Per-defect
- **Tooling:** Spreadsheet or structured log. ODC has been applied to agile processes
- **Relevance:** **HIGH** — The incidents.jsonl already captures incidents. Adding ODC-style classification would answer: "Are most defects specification failures or implementation failures? Are they caught by the agent or by the operator?" The `root_cause_classification` field in the constitution (SPECIFICATION_OR_SYSTEM_DESIGN / HANDOFF_OR_ALIGNMENT / VERIFICATION_OR_TERMINATION) is already a simplified ODC
- **Effort:** Lightweight (days). The existing incident schema needs minor extension

#### 2.8 GQM (Goal-Question-Metric)

- **Origin:** Victor Basili, University of Maryland / NASA Goddard SEL, 1984+
- **What it analyzes:** A top-down measurement DESIGN framework. Start with a goal (what to improve), derive questions (what to know), define metrics (how to measure). Every metric must trace back to a question. Prevents collecting data for its own sake
- **Data requirements:** N/A — it's a design tool, not an analysis tool
- **Relevance:** **HIGH** — Use before deciding what to log. Example: Goal: Reduce rework → Question: Where does rework originate? → Metric: Tasks re-entering a completed phase, by phase
- **Effort:** Lightweight (a day of structured thinking)

#### 2.9 Mining Software Repositories (MSR)

- **Origin:** MSR conference series since 2004. Key researchers: Ahmed Hassan (Queen's), Thomas Zimmermann (Microsoft Research), Harald Gall (Zurich)
- **What it analyzes:** Extracts metrics from VCS history, issue trackers, CI/CD logs. Common metrics: code churn (lines added+deleted, instability indicator), change coupling (files that co-commit, hidden dependencies), commit frequency distribution, bug-fixing commit ratio
- **Data requirements:** `git log` — already available
- **Granularity:** Per-commit or per-file
- **Tooling:** Python scripts over `git log`. The `lasaris/Git-logs-for-Process-Mining` GitHub repo provides ready-made scripts for converting git logs to XES format for PM4Py
- **Relevance:** **HIGH** — Git history + JSONL run records enable full process reconstruction with zero additional instrumentation. The commit message format (`{phase}: {what changed}`) already encodes activity labels
- **Effort:** Lightweight (days). `git log` parsing is a Python afternoon

#### 2.10 DORA Metrics (Analogs)

- **Origin:** Nicole Forsgren, Jez Humble, Gene Kim. "Accelerate" (2018). dora.dev
- **What it analyzes:** Four metrics predicting delivery performance: deployment frequency, lead time for changes, change failure rate, time to restore service. (Fifth metric added 2024: deployment rework rate)
- **Relevance:** **MEDIUM** — DORA targets production CI/CD pipelines, but the analogs are useful:
  - Lead time → task creation to completion (from JSONL timestamps)
  - Change failure rate → fraction of tasks requiring rework after completion
  - Deployment rework rate → tasks with `attempt_count > 1`
- **Effort:** Lightweight. Computable from existing JSONL + git data

---

### Layer 3: Interaction-Construction Relationship

#### 3.1 Socio-Technical Congruence (STC)

- **Origin:** Cataldo, Herbsleb et al., Carnegie Mellon, 2008. Empirical Software Engineering
- **What it analyzes:** The fit between coordination requirements (who NEEDS to coordinate based on technical dependencies) and actual coordination activities (who ACTUALLY communicates). Misalignment predicts defects and delays
- **Data requirements:** (1) Technical dependency graph (which code modules depend on which), (2) Communication graph (who talks to whom), (3) Outcome data (resolution time, defect rates)
- **Granularity:** Per-task or per-release
- **Tooling:** Can be computed from git co-change data + communication logs. Tools exist (Codescene) but manual computation is feasible
- **Relevance:** **HIGH** — Directly applicable. The "technical dependency" is which files/modules each agent session touches. The "communication" is which sessions the operator mediates between. STC would reveal: "Did the operator connect the right agents? When agent A changed the API, did agent B (the consumer) get informed?" In a multi-agent pipeline, the operator IS the coordination mechanism — STC measures whether that mechanism is working
- **Effort:** Moderate (weeks). Requires extracting file-touch graphs from conversation logs and cross-referencing with task dependencies

**STC measurement procedure (from CMU-ISR-08-104):**
1. Extract file-level logical dependencies (files that co-change — use `git log` co-change analysis as proxy)
2. Map contributors to files touched per task (from commit log)
3. Build Coordination Requirements (CR) matrix: CR[A][B] = 1 if A and B touched files with a logical dependency
4. Build Coordination Activities (CA) matrix: CA[A][B] = 1 if A and B had a documented communication event during the task
5. Congruence = |CR ∩ CA| / |CR| (fraction of required coordination that actually happened). Range 0-1
6. Correlate congruence scores with task resolution time and defect rates

**Key empirical findings:** High congruence reduced modification request resolution time by ~32%. Congruence gaps significantly increased software failures. Logical dependencies (shared modules, shared data) were far more predictive than call-graph dependencies. Multi-year study: 70+ teams, 900+ developers, statistically significant effects.

#### 3.2 Coordination Breakdowns (Cataldo & Herbsleb, 2013)

- **Origin:** Cataldo & Herbsleb, IEEE TSE, 2013. Extension of STC work
- **What it analyzes:** Three coordination breakdown types:
  1. **Missing coordination:** Required coordination never happened. → Integration defects
  2. **Delayed coordination:** Happened, but after dependent work was already done. → Rework
  3. **Incorrect coordination:** Happened but with wrong content. → Specification drift (code correct per spec, but spec was wrong)
- **Data requirements:** Same as STC plus temporal ordering of events
- **Granularity:** Per-task
- **Relevance:** **HIGH** — Gives a 3-way failure classification that maps directly to operator-agent breakdowns. Was the agent never told about a dependency (missing)? Was it told too late (delayed)? Was it told the wrong thing (incorrect)?
- **Effort:** Lightweight (days) — can be applied qualitatively to each incident/failure

#### 3.3 Conway's Law (Empirical Studies)

- **Origin:** Melvin Conway, 1967. Empirical validation: MacCormack, Rusnak & Baldwin (2006), Cataldo et al. (2009)
- **What it analyzes:** Whether the structure of the system mirrors the communication structure of the organization that built it. Empirical studies measure this correlation and its effect on quality
- **Data requirements:** Organizational/communication structure + code architecture dependency structure
- **Granularity:** Per-module or per-component
- **Tooling:** DSM (Design Structure Matrix) analysis tools, or manual comparison
- **Relevance:** **MEDIUM** — In a solo-operator + AI-agents setup, the "organizational structure" is the agent role assignments. Conway's Law predicts that if you have separate "frontend agent" and "backend agent" sessions, the system will develop a clean frontend-backend boundary — or if you DON'T enforce that separation, boundaries will blur. Useful as a lens but not as a measurement tool
- **Effort:** Lightweight (days for qualitative application)

#### 3.3 Orthogonal Defect Classification (ODC) — Cross-Layer Application

- **Origin:** Ram Chillarege, IBM Research, 1992
- **What it analyzes:** (Cross-layer) ODC's defect-type classification maps to construction issues (what went wrong in the code), while the trigger classification maps to interaction issues (what activity or interaction exposed the defect). The combination links interaction patterns to construction quality
- **Data requirements:** Defect records classified by both type and trigger
- **Granularity:** Per-defect, aggregated per-phase or per-component
- **Tooling:** Spreadsheet. Classification takes ~3 min/defect
- **Relevance:** **HIGH** — The eight defect types (assignment, checking, interface, algorithm, function, timing, documentation, build) and triggers (design conformance, code review, unit test, field test, etc.) directly address "which interaction patterns catch which defect types?" If most interface defects are caught only by the operator during manual review (not by agent self-test), that reveals a feedback loop gap
- **Effort:** Lightweight (days to establish coding scheme; ongoing ~3 min/defect)

#### 3.4 Feedback Loop Analysis (Systems Thinking)

- **Origin:** Peter Senge, "The Fifth Discipline" (1990). Jay Forrester, system dynamics (1961). Applied to software: Weinberg, "Quality Software Management" (1992)
- **What it analyzes:** Identifies reinforcing loops (virtuous/vicious cycles), balancing loops (self-correction), and delays in the system. Maps causal relationships between process variables
- **Data requirements:** Qualitative understanding of process relationships. Can be done from observation and reflection
- **Granularity:** System-level (the whole pipeline)
- **Tooling:** Causal loop diagrams (pen and paper or any diagramming tool)
- **Relevance:** **HIGH** — Critical for understanding why certain patterns persist. Example loops in this pipeline:
  - *Reinforcing (virtuous):* Better specs → fewer agent errors → less rework → more time for better specs
  - *Reinforcing (vicious):* Rushed specs → agent misunderstands → rework → even more rushed specs
  - *Balancing:* Agent self-test catches defect → fix → re-test → quality maintained
  - *Missing:* Agent A changes API → no notification to Agent B → integration failure discovered late
- **Effort:** Lightweight (days for initial diagram; iterative refinement)

#### 3.6 Handoff Analysis (Healthcare + Aviation + Software)

- **Origin:** Joint Commission (US hospital accreditation, 2006 National Patient Safety Goal — communication failures caused ~30% of malpractice claims). SBAR (US Navy submarines → Kaiser Permanente). I-PASS (NEJM 2014, Starmer et al. — reduced preventable adverse events). CRM/TEM from aviation (post-1978 United 173 crash)
- **What it analyzes:** Information loss and error introduction at handoff points. Key failure modes identified by research:
  - **Funneling / progressive information loss:** Each retelling omits detail; lossy compression compounds
  - **Three handoff types** (Reddy et al., 2021): human-human, human-ICT, ICT-human — each with different failure modes
  - **Omission is dominant:** Missing information is far more common than wrong information
- **Structured handoff protocols:**
  - **SBAR:** Situation, Background, Assessment, Recommendation
  - **I-PASS:** Illness severity, Patient summary, Action list, Situation awareness, Synthesis by receiver
- **Data requirements:** Structured handoff records, adverse event logs linked to transition events
- **Granularity:** Per-handoff
- **Relevance:** **HIGH** — Handoffs are the primary coordination mechanism in this pipeline. The existing handoff JSON envelope schema is a direct implementation of this principle. Measurable: (a) which required fields were omitted, (b) which consumed fields were present in the producing agent's output, (c) latency between production and consumption
- **Effort:** Lightweight (days). Audit existing handoffs for field completeness rate

#### 3.7 CRM / Threat and Error Management (TEM)

- **Origin:** Aviation CRM (FAA AC 120-51 series). TEM introduced in 6th generation CRM
- **What it analyzes:** Classifies events as: threats (external hazards), errors (crew/agent deviations), or undesired states. Tracks whether threats were detected before becoming errors. Key concepts: closed-loop communication (read-back/hear-back), slips vs. mistakes
- **Key insight for AI pipelines:** CRM distinguishes **slips** (correct intent, wrong execution) from **mistakes** (wrong intent, which is misspecification). Most AI agent failures are mistakes, not slips. Also: agents may not flag uncertainty (analog of junior crew failing to speak up to captain)
- **Relevance:** **MEDIUM-HIGH** — TEM classification maps cleanly. The "closed-loop communication" requirement — receiver confirms *understanding*, not just receipt — is directly applicable: agents should confirm specification interpretation, not just acknowledge receipt
- **Effort:** Lightweight to apply conceptually

#### 3.6 Root Cause Classification — Existing Constitution Taxonomy

- **Origin:** Custom — already defined in the CLAUDE.md constitution
- **What it analyzes:** Three-category root cause classification: SPECIFICATION_OR_SYSTEM_DESIGN, HANDOFF_OR_ALIGNMENT, VERIFICATION_OR_TERMINATION
- **Data requirements:** Incident records with classification
- **Granularity:** Per-incident
- **Relevance:** **HIGH** — Already in use. Maps directly to the three analytical layers: specification = construction, handoff = interaction, verification = feedback loops. Extending this with ODC's finer categories would increase analytical power without changing the existing workflow
- **Effort:** Already implemented (zero additional effort for current granularity)

---

## 2. Data Collection Strategy Options

### Option A: Minimal (Start Today, ~1 Hour Setup)

**What to capture:**
- Tag each session in history.jsonl with task-type (debug/feature/refactor) — already partially done via runs.jsonl
- At session end, record: outcome (success/partial/failed), primary waste encountered (from Poppendieck's 7), and one-line root cause if applicable
- Add `phase_log` array to run records: `[{phase, entered_at, exited_at, outcome}]`. This one field unlocks process mining, PSP phase analysis, and VSM metrics simultaneously
- Continue current runs.jsonl + tasks.jsonl + incidents.jsonl

**How to capture:**
- Manual annotation by operator at session end (30 seconds per session)
- No code changes needed

**What it enables:**
- Waste distribution analysis (which waste category dominates?)
- Success rate tracking per task type
- Root cause pattern identification over time
- Enough data for a basic value stream map after ~20 sessions

**Cost:** ~30 seconds per session. Zero token overhead. Negligible storage.

### Option B: Moderate (1-2 Days Setup)

**What to capture (everything in Option A, plus):**
- ETL script that extracts structured events from conversation JSONL:
  - Session start/end timestamps
  - Tool-use events (name, timestamp, file path if applicable)
  - User message count and approximate length
  - Permission mode
  - Git branch at session start
- Classify each session with FIPA-style interaction pattern: directive (operator requests, agent executes), collaborative (back-and-forth refinement), investigative (agent explores, reports back)
- Extract file-touch graph per session (which files were Read/Edit/Written)

**How to capture:**
- Python script (~100-150 lines) run post-session or batch
- Outputs to a new `events.jsonl` in standardized format (compatible with process mining)
- Session classification can be automated with heuristics (e.g., >80% tool_use = directive; >3 back-and-forth = collaborative)

**What it enables:**
- Process mining: discover actual process models from tool-use sequences
- File-touch overlap analysis: detect coordination gaps (two sessions editing same files without cross-reference)
- Interaction pattern distribution: what % of sessions are directive vs. collaborative?
- Basic STC analysis: compare file dependencies with session-to-session communication
- Time-in-phase analysis: how long in reading vs. editing vs. testing?

**Cost:** 1-2 days setup. ~5 seconds per session (automated). ~1 MB/week additional storage.

### Option C: Comprehensive (1-2 Weeks Setup)

**What to capture (everything in Option B, plus):**
- LLM-assisted classification of each user message with speech-act / performative type (request, query, inform, correct, confirm, reject)
- LLM-assisted classification of each agent response with outcome type (completed, partial, misunderstood, scope-exceeded, blocked)
- Decision extraction: identify decision points in conversations and log them as IBIS-style issue-position-argument tuples
- Handoff quality scoring: compare session summary against next session's actual information needs
- Defect classification using ODC categories for all incidents

**How to capture:**
- Post-session LLM analysis pass (could use a cheaper/faster model)
- ~500-1000 tokens per session for classification
- Results appended to enriched event log

**What it enables:**
- Full interaction analysis with speech-act distributions
- Decision archaeology: searchable log of design decisions with rationale
- Handoff loss quantification: percentage of information lost at session boundaries
- ODC-based defect trend analysis: are specification defects decreasing over time?
- Cross-layer correlation: link interaction patterns to construction outcomes

**Cost:** 1-2 weeks setup. ~$0.01-0.05 per session for LLM classification. Moderate ongoing maintenance.

---

## 3. Classification Scheme Candidates

### Layer 1: Interaction Classification

#### Scheme 1A: FIPA-Derived Performative Taxonomy (Recommended)

| Category | Definition | Example in this system |
|---|---|---|
| `request` | Operator asks agent to perform an action | "Implement the waveform component" |
| `query` | Operator asks for information | "What files handle the CDJ connection?" |
| `inform` | Agent reports information or status | "I found 3 files that handle..." |
| `propose` | Agent suggests an approach | "I recommend using WebSocket because..." |
| `confirm` | Operator or agent confirms understanding | "Yes, proceed with that approach" |
| `correct` | Operator corrects agent's understanding | "No, not that file — the one in src/lib" |
| `reject` | Operator rejects agent's proposal or output | "This doesn't match the spec, try again" |
| `delegate` | Operator routes work to a different agent/session | "I'll have the architect look at this" |

**Tradeoffs:** Simple (8 categories), covers >95% of interactions, easy to automate with heuristics or LLM. Misses nuance (doesn't distinguish "correct a factual error" from "correct a scope violation"). Good starting point.

#### Scheme 1B: Extended Interaction Move Taxonomy

Adds to 1A:
| Category | Definition |
|---|---|
| `scope-check` | Agent or operator verifies task boundaries |
| `context-load` | Agent reads prior work/files to build understanding |
| `clarify` | Either party seeks disambiguation |
| `escalate` | Agent reports inability to proceed |
| `summarize` | Agent or operator synthesizes progress |

**Tradeoffs:** More precise (13 categories), but requires more effort to code reliably. The `scope-check` and `escalate` categories are valuable for identifying coordination problems.

#### Scheme 1C: Binary Initiative Classification

| Category | Definition |
|---|---|
| `operator-directed` | Operator specifies what to do AND how |
| `operator-delegated` | Operator specifies what, agent decides how |
| `agent-proposed` | Agent identifies something to do, operator approves |
| `collaborative` | Both parties contribute to defining the work |

**Tradeoffs:** Very coarse (4 categories), easy to apply, useful for tracking autonomy levels over time. Doesn't capture breakdowns or quality.

### Layer 2: Construction Activity Classification

#### Scheme 2A: Tool-Use Activity Taxonomy (Recommended)

Derived from actual tool names in the conversation logs:

| Activity | Tools | Value-Adding? |
|---|---|---|
| `orient` | Read, Glob, Grep | Depends — first read = value, re-read = potential waste |
| `design` | Thinking blocks, text responses with proposals | Yes |
| `implement` | Edit, Write | Yes |
| `execute` | Bash (build, run) | Yes |
| `verify` | Bash (test), Read (check output) | Yes |
| `search` | Grep, Glob, WebSearch | Depends on context |
| `coordinate` | Text responses answering operator questions | Overhead (necessary but not directly value-adding) |
| `rework` | Edit to files previously edited in same session | Waste indicator |

**Tradeoffs:** Directly extractable from existing logs with zero manual effort. The `rework` detection (re-editing same files) is a powerful waste indicator. Misses intent — a Read could be orientation or verification. Heuristics needed for context.

#### Scheme 2B: PSP Phase Classification

| Phase | Description |
|---|---|
| `plan` | Understanding requirements, planning approach |
| `design` | Designing solution structure |
| `code` | Writing new code |
| `compile` | Building, resolving build errors |
| `test` | Running and evaluating tests |
| `postmortem` | Reviewing what happened, documenting |

**Tradeoffs:** Well-established, maps to flow skill phases. Harder to automate from tool-use data alone — a Read during `plan` vs. during `test` looks identical without context.

#### Scheme 2C: Waste-Annotated Activity Classification

Extends Scheme 2A by tagging each activity with a waste flag:

| Waste Type | Detection Signal |
|---|---|
| `partially-done` | Session ends with uncommitted changes |
| `relearning` | Reading files that were read in prior session for same task |
| `handoff-overhead` | Operator time spent translating between sessions |
| `defect` | Revert commits, incident records |
| `waiting` | Long gaps between operator prompt and session start |
| `context-switching` | Operator switching between unrelated task sessions rapidly |

**Tradeoffs:** Highest analytical value for identifying improvement opportunities. Requires cross-session analysis (comparing file-read patterns across sessions). Some signals need heuristic thresholds (how long is "long" for waiting?).

### Layer 3: Outcome Classification

#### Scheme 3A: Run Outcome + Root Cause (Recommended — Already In Use)

Extends the existing runs.jsonl schema:

| Field | Categories |
|---|---|
| `result` | success, partial, failed, blocked, escalated |
| `root_cause_classification` | SPECIFICATION_OR_SYSTEM_DESIGN, HANDOFF_OR_ALIGNMENT, VERIFICATION_OR_TERMINATION |
| `rework_required` | boolean |
| `attempt_count` | integer |

**Tradeoffs:** Already implemented. Sufficient for basic pattern detection. Extend with ODC defect type for richer analysis.

#### Scheme 3B: ODC-Extended Outcome Classification

Adds to 3A:

| Field | Categories |
|---|---|
| `defect_type` | assignment, checking, interface, algorithm, function, timing, documentation |
| `trigger` | design-review, code-review, unit-test, integration-test, operator-review |
| `impact` | capability, reliability, performance, usability |

**Tradeoffs:** Much richer analysis potential. Enables questions like "are interface defects increasing?" and "what review activity catches the most defects?" ~3 minutes per incident to classify. Best started when incident volume is higher.

#### Scheme 3C: MAST Failure Classification (for failed/partial runs)

Apply the 14 MAST failure modes to each non-successful run:

| Cluster | Failure Mode | Signal in this pipeline |
|---|---|---|
| System Design | Unclear roles/instructions | Agent asks clarifying questions or produces off-spec output |
| System Design | Inadequate capability assignment | Agent can't handle the task technically |
| Misalignment | Specification misalignment | Agent's understanding differs from operator's intent |
| Misalignment | Context loss between agents | Re-reading files, re-establishing context at session start |
| Misalignment | Premature completion | Agent marks done but work is incomplete |
| Verification | Inadequate output validation | No tests run, no self-check |
| Verification | Insufficient test coverage | Tests pass but don't cover the failure mode |

**Tradeoffs:** Purpose-built for LLM agents, so categories are immediately recognizable. The LLM-as-judge classifier makes it automatable. Doesn't cover successful runs — pair with Scheme 1A for complete coverage.

---

## 4. Cross-Layer Integration

### The Handoff as Fundamental Cross-Layer Unit

The three layers converge on one observation: **the handoff is the fundamental unit of cross-layer analysis.** A handoff is simultaneously:
- An **interaction event** (how the two parties communicate — L1)
- A **construction event** (what artifact transfers — L2)
- A **quality risk event** (where information loss occurs — L3)

Every framework in this catalog has something to say about handoffs: process mining sees them as transitions with wait times; PSP/defect analysis sees them as the mechanism by which specification errors survive; VSM identifies them as the dominant waste location in knowledge work; traceability sees them as where links break; design rationale sees them as where reasoning is lost.

**Implication:** If you instrument ONE thing well, instrument handoffs. Tag each handoff with: (a) type (session-boundary vs. agent-boundary vs. scope-boundary), (b) artifact transferred, (c) outcome (did receiving party need clarification? was rework triggered?). This single instrument connects interaction patterns to construction outcomes.

### Frameworks That Naturally Bridge Layers

| Framework | Layers Bridged | How |
|---|---|---|
| **Socio-Technical Congruence** | 1 ↔ 2 | Links communication patterns (L1) to code dependency patterns (L2) |
| **ODC** | 2 ↔ 3 | Links defect types in code (L2) to the activities that expose them (L3) |
| **Value Stream Mapping** | 1 ↔ 2 ↔ 3 | Maps entire flow from interaction through construction to outcome |
| **Feedback Loop Analysis** | 1 ↔ 2 ↔ 3 | Identifies causal chains across all layers |
| **Waste Classification** | 1 ↔ 2 | Handoff waste (L1) shows up as rework in construction (L2) |

### Minimum Viable Cross-Layer Analysis

1. **Tag each session** with interaction type (Scheme 1A) and construction activity distribution (Scheme 2A)
2. **Tag each run** with outcome (Scheme 3A, already done)
3. **Correlate:** Do sessions with more `correct`/`reject` interactions produce more `partial`/`failed` outcomes?
4. **Track over time:** Is the ratio of `operator-directed` to `operator-delegated` changing? Is it correlated with success rate?

This requires only Option A data collection (manual tags) and can be done in a spreadsheet.

### Distinguishing Causal from Correlated Patterns

In increasing strength:
1. **Temporal ordering:** Does the interaction pattern precede the outcome? Necessary but not sufficient. Coordination gaps consistently preceding defects is weak causal evidence
2. **Dose-response:** Does more of the cause produce more of the effect monotonically? STC shows this — higher congruence gap → higher failure rate, approximately linearly
3. **Mechanism specificity:** Can you articulate the causal mechanism? STC has one (missing coordination → missing specification → integration defect). Generic correlations without mechanisms are suspect
4. **Natural experiments:** Compare outcome changes before and after a process change, controlling for confounds. Strongest feasible option for a small pipeline
5. **Structural causal models / DAGs:** Formalize assumptions, use observational data with adjustment. Academic — defer until 50+ task observations exist

**Practical bar for this pipeline:** Temporal ordering + mechanism specification. Log interaction patterns with timestamps; log defect discovery with timestamps and links to the producing interaction. A defect whose causal chain you can trace to a specific handoff gap is stronger evidence than a correlation across runs.

### Where Layers Reinforce vs. Are Independent

- **Reinforcing:** Interaction patterns (L1) strongly predict construction quality (L2) in this system because the operator is the sole coordination mechanism. If the operator gives a bad prompt, the construction will be wrong — there's no independent verification layer that can compensate
- **Independent:** Some construction issues (L2) are purely agent capability issues (e.g., agent can't handle a complex refactoring) and aren't related to interaction quality (L1). These are distinguishable by the root cause classification (SPECIFICATION vs. VERIFICATION)
- **Reinforcing:** Feedback loop quality (L3) compounds over time. Missing feedback loops get worse, not better, as the codebase grows

---

## 5. Recommended Starting Point

### Start Tracking Immediately (Day 1)

**The single most valuable thing to track:** Waste type per session, using Poppendieck's seven wastes simplified to five:

1. **Rework** — did the agent have to redo work? Why?
2. **Relearning** — did the agent spend time re-establishing context that should have persisted?
3. **Handoff loss** — did information get lost between sessions?
4. **Waiting** — where were the delays?
5. **Scope creep** — did the agent do work that wasn't requested?

**How:** At session end, add one field to runs.jsonl: `"primary_waste": "rework|relearning|handoff_loss|waiting|scope_creep|none"`. Takes 10 seconds.

**Why this first:** Waste identification is the highest-leverage starting point because it directly points to what to automate. If 60% of waste is "relearning" → invest in persistent context. If 60% is "handoff loss" → invest in structured handoff protocols. If 60% is "rework" → invest in better specs or verification.

### Week 1-2: Add ETL Script (Option B)

Build the conversation log ETL that extracts tool-use events into a standardized event log. This unlocks process mining and file-touch analysis without requiring any workflow changes.

### Week 2-3: Run MAST Classifier on Existing Failed Runs

The MAST failure taxonomy (arXiv:2503.13657) was purpose-built for LLM multi-agent systems. Run the published LLM-as-judge classifier on your existing conversation logs for failed/partial runs. This gives an immediate distribution of failure modes (system design vs. inter-agent misalignment vs. verification) without any new instrumentation.

### Can Wait Until More Data Exists

- **Full ODC classification** — need more incidents before the pattern is visible (>20 defects)
- **STC analysis** — need more multi-session features where coordination gaps could be detected (>10 multi-session features)
- **LLM-assisted interaction classification** — the manual tags from Option A are sufficient while the dataset is small
- **Design rationale extraction** — valuable but not urgent; the ADR mechanism covers the highest-impact decisions

### The 80/20

| Investment | Return |
|---|---|
| 10 sec/session waste tag | Identifies which waste category to attack first |
| 1-2 days ETL script | Unlocks process mining, file-touch analysis, time-in-phase metrics |
| Half-day MAST classifier run on existing logs | Immediate failure mode distribution — no new instrumentation |
| 30 min drawing causal loop diagram | Identifies missing feedback loops in the pipeline |
| Existing runs.jsonl + incidents.jsonl | Already tracks outcomes and root causes |

**What the analysis agent's procedure should look like:**
1. Input: conversation JSONL + runs.jsonl + git log
2. ETL: Extract events (tool calls, messages) → standardized event log
3. Classify: Tag each event/session with activity type and interaction type (heuristic first, LLM later)
4. Analyze: Run process discovery, compute waste metrics, flag anomalies
5. Output: Structured report with waste distribution, process model visualization, anomaly flags

**What the decision agent will need:**
- Classified events in JSONL format with fields: `timestamp`, `session_id`, `task_id`, `activity_type`, `interaction_type`, `actor`, `target_files`, `waste_flag`, `outcome`
- Aggregated metrics per task: total_time, rework_count, interaction_pattern_distribution
- Cross-session linkage: task_id connecting sessions that work on the same feature

---

## References

### Core Frameworks
- Bales, R.F. (1950). Interaction Process Analysis. Addison-Wesley.
- Malone, T.W. & Crowston, K. (1994). The Interdisciplinary Study of Coordination. ACM Computing Surveys.
- van der Aalst, W. (2016). Process Mining: Data Science in Action. Springer.
- Poppendieck, M. & Poppendieck, T. (2003). Lean Software Development. Addison-Wesley.
- Chillarege, R. et al. (1992). Orthogonal Defect Classification. IEEE TSE.
- Cataldo, M. et al. (2008). Socio-Technical Congruence. ESEM.
- Senge, P. (1990). The Fifth Discipline. Doubleday.
- Humphrey, W. (1995). A Discipline for Software Engineering (PSP). Addison-Wesley.

- Cataldo, M. & Herbsleb, J. (2013). Coordination Breakdowns and Their Impact on Development Productivity and Software Failures. IEEE TSE.

### Human-AI Interaction
- Cemri, Pan, Yang et al. (2025). Why Do Multi-Agent LLM Systems Fail? (MAST). arXiv:2503.13657. ICLR 2025.
- Frontiers in Computer Science (2024). Human-AI collaboration is not very collaborative yet: A taxonomy of interaction patterns.
- Holter et al. (2024). Deconstructing Human-AI Collaboration: Agency, Interaction, and Adaptation. Computer Graphics Forum.
- ChatCollab (2024). Exploring Collaboration Between Humans and AI Agents in Software Teams. arXiv:2412.01992.
- Horvitz, E. (1999). Principles of Mixed-Initiative User Interfaces. CHI '99.
- Winograd, T. & Flores, F. (1986). Understanding Computers and Cognition. Ablex.
- Ergonomics (2022). The role of shared mental models in human-AI teams.

### Agent Communication
- Smith, R.G. (1980). The Contract Net Protocol. IEEE Transactions on Computers.
- FIPA ACL Specification (2002). Foundation for Intelligent Physical Agents.
- Searle, J.R. (1969). Speech Acts. Cambridge University Press.

### Design Rationale
- Kunz, W. & Rittel, H. (1970). Issues as Elements of Information Systems. Working Paper.
- MacLean, A. et al. (1991). Questions, Options, and Criteria (QOC). HCI.

### Handoff & Safety
- Joint Commission (2006). National Patient Safety Goal on Handoffs.
- Starmer, A.J. et al. (2014). Changes in Medical Errors after Implementation of a Handoff Program. NEJM.
- Endsley, M.R. (1995). Toward a Theory of Situation Awareness in Dynamic Systems. Human Factors.

### Standards
- IEEE 1044-2009. Standard Classification for Software Anomalies.

### Process Mining for Software Development
- Process Mining for Agile Software Process Assessment and Improvement. Information and Software Technology, 2025.
- A Process Mining-Based System for Analysis and Prediction of Software Development Workflows. arXiv, 2025.

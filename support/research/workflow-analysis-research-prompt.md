# Research Prompt: Workflow Analysis & Classification Frameworks for Multi-Agent Software Development

## Context

You are researching frameworks, taxonomies, and methodologies for analyzing and classifying the workflow of a multi-agent AI software development pipeline. The system under study is a solo human operator coordinating multiple AI agents (Architect, Developer, Researcher, Validator, QA Tester, Designer) to build a real software product (a DJ lighting automation system called SCUE).

The operator wants to understand what is happening vs. what should be happening across the pipeline, in order to design a procedural workflow controller that can automate the mechanical parts of coordination. Before building anything, the operator needs to know what frameworks exist for this kind of analysis, what data to collect, and how to classify it.

This research is foundational — it will inform a later decision about what to track and how. Cast a wide net. The operator will narrow down after reviewing findings.

## Three Analytical Layers

The operator has identified three distinct layers of analysis. Research each independently, then address their intersection.

### Layer 1: Interaction Analysis
**Question:** How do agent-user and agent-agent interactions unfold?

Research frameworks and methodologies for analyzing:
- **Conversation/dialogue analysis** — how do multi-party (human + AI) conversations get structured? What taxonomies exist for classifying utterances, turns, speech acts, or interaction moves in collaborative work?
- **Coordination theory** — from CSCW (Computer-Supported Cooperative Work), organizational theory, or multi-agent systems research: how is coordination modeled? What are the established taxonomies for coordination mechanisms (e.g., Malone & Crowston's coordination theory)?
- **Communication pattern analysis** — who initiates, who responds, what gets clarified, what gets misunderstood, where does routing happen, where does it break down? What frameworks exist for mapping these patterns?
- **Agent interaction protocols** — from multi-agent systems (MAS) research: how are agent interactions formally specified? Contract Net Protocol, FIPA ACL, auction-based coordination, blackboard systems — which are relevant to understanding (not just designing) agent interactions?
- **Human-AI collaboration models** — what frameworks exist specifically for analyzing how humans and AI agents collaborate? Mixed-initiative systems, shared mental models, human-in-the-loop patterns.

Specific questions:
1. What are the most widely-used taxonomies for classifying interaction types in collaborative work (human-human, human-AI, or AI-AI)?
2. What data would you need to collect to apply each taxonomy?
3. What are the tradeoffs between fine-grained (per-utterance) vs. coarse-grained (per-session) classification?
4. Are there tools or established coding schemes for this kind of analysis?

### Layer 2: Construction Analysis
**Question:** How is the software actually getting built over time?

Research frameworks and methodologies for analyzing:
- **Process mining** — extracting process models from event logs. What tools and techniques exist? How is process mining applied to software development specifically?
- **Software process analysis** — from software engineering research: how are development processes modeled, measured, and compared? Personal Software Process (PSP), Team Software Process (TSP), process metrics.
- **Artifact traceability** — how do you trace the lineage of artifacts (specs → tasks → code → tests → reviews) through a development process? Requirements traceability matrices, design rationale capture.
- **Value stream mapping** — from lean manufacturing/lean software development: how do you map the flow of work and identify waste (waiting, rework, handoff overhead)?
- **Decision archaeology** — how do you reconstruct and classify the decisions that shaped a codebase? Design rationale systems, architectural knowledge management.
- **Rework and defect flow analysis** — where does rework originate? How does it propagate? What patterns predict rework?

Specific questions:
1. What event/log data would you need to perform process mining on a multi-agent development pipeline?
2. What are established categories for classifying "types of development activity" (design, implementation, debugging, refactoring, coordination overhead, rework, etc.)?
3. How do you distinguish value-adding work from coordination overhead in a quantifiable way?
4. Are there lightweight approaches that don't require specialized tooling?

### Layer 3: The Relationship Between Interaction and Construction
**Question:** How do interaction patterns drive (or fail to drive) construction outcomes?

Research frameworks for understanding:
- **Process-outcome correlation** — from organizational research or software engineering: how do you link process characteristics (communication frequency, coordination overhead, decision latency) to outcomes (defect rates, rework rates, velocity)?
- **Handoff analysis** — specifically for systems where work crosses boundaries (roles, layers, sessions): what frameworks exist for analyzing handoff quality, information loss, and handoff-induced defects?
- **Feedback loop identification** — where are the feedback loops in the process? Which are reinforcing (good patterns compound) vs. balancing (errors self-correct) vs. missing (errors go undetected)?
- **Root cause classification** — taxonomies for classifying why things go wrong: specification failures, communication failures, verification failures, etc. Are there established schemes that map failure modes to process characteristics?

Specific questions:
1. What frameworks link "how people/agents communicate" to "quality of what gets built"?
2. How do you identify which interaction patterns are causal vs. merely correlated with outcomes?
3. What's the minimum viable data collection that would let you start seeing patterns across these layers?

## Data Source Constraints

The raw data for this analysis may come from several sources. The operator hasn't yet determined the best extraction method. Research should consider:
- **Claude Code internal logs** — conversation transcripts stored by the Claude Code CLI tool. Format TBD.
- **Session summary artifacts** — structured markdown files written by agents at end of each session (status, work performed, files changed, decisions made, scope violations, missteps, learnings).
- **Task tracker** — `.agent/tasks.jsonl` with task status, flow phase, blockers.
- **Run records** — `.agent/runs.jsonl` with task outcomes, attempt counts.
- **Git history** — commits, diffs, branch history.
- **Bug logs** — structured markdown bug entries with symptoms, root causes, fixes.
- **Protocol improvement log** — observations about process failures and friction.

For each framework recommended, note what data it requires and which of these sources could provide it.

## Output Requirements

Structure your findings as:

### 1. Framework Catalog
For each framework/methodology found, provide:
- **Name and origin** (academic field, key paper/author, year)
- **What it analyzes** (which of the 3 layers, or cross-layer)
- **Data requirements** (what you need to collect to apply it)
- **Granularity** (per-utterance, per-session, per-feature, per-milestone)
- **Tooling** (specialized tools required, or can be done manually/with scripts)
- **Relevance to this system** (HIGH / MEDIUM / LOW with explanation)
- **Effort to implement** (lightweight = days, moderate = weeks, heavy = months)

### 2. Data Collection Strategy Options
Present 2-3 options for data collection ranging from minimal to comprehensive:
- What data to capture at each level
- How to capture it (automated vs. manual, hooks vs. post-hoc extraction)
- What analysis each level enables
- What it costs (operator time, token overhead, storage)

### 3. Classification Scheme Candidates
For each analytical layer, recommend 2-3 candidate classification schemes:
- The taxonomy/coding scheme
- Example categories with definitions
- How it would be applied to this system's data
- Tradeoffs (precision vs. effort, coverage vs. noise)

### 4. Cross-Layer Integration
How do the Layer 1, 2, and 3 analyses connect?
- Which frameworks naturally bridge multiple layers?
- What's the minimum viable cross-layer analysis?
- Where do the layers reinforce each other vs. where are they independent?

### 5. Recommended Starting Point
Given the constraints (solo operator, 4 days into pipeline, actively building product):
- What's the single most valuable thing to start tracking immediately?
- What can wait until more data exists?
- What's the 80/20 — minimal collection effort, maximum analytical insight?

## Research Scope

- Prioritize established, peer-reviewed or widely-adopted frameworks over novel or speculative approaches.
- Include frameworks from: software engineering, CSCW, organizational theory, multi-agent systems, process mining, lean/agile methodology, human-AI interaction.
- Exclude: pure ML/NLP approaches to conversation analysis (too heavy for this context), enterprise-scale process mining tools (irrelevant for solo operator).
- Include lightweight/manual approaches alongside formal methodologies.
- Note when a framework has been applied to AI-assisted development specifically (vs. human-only teams).

## What a Good Answer Looks Like

The operator needs enough information to make an informed decision about:
1. Which framework(s) to adopt for each analytical layer
2. What data to start collecting now (before the analysis agent is built)
3. What the analysis agent's procedure should look like (input data → classification → output)
4. What the downstream "decision agent" will need (what format should classified data be in for a second agent to recommend actions?)

The output should be actionable — not a literature review for its own sake, but a decision-support document. For each recommendation, state what it enables and what it costs.

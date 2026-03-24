# Lens C: Learning & Knowledge Analysis

**Date:** 2026-03-24
**Sessions analyzed:** 25 (23 with content, 2 empty)
**Scope:** Knowledge gaps, repeated research, decision patterns, unpersisted knowledge

---

## Per-Session Analysis

### Session 1: `1a82dd5b-61f3` (Pipeline critique + v2.1 review setup)

- **learning_score:** 4
- **repeated_research:**
  - Topic: "How Claude Code stores conversations on disk" — explored via Agent to find `~/.claude/projects/<slug>/` paths. This knowledge was already partially established in prior sessions but had to be rediscovered.
    - tokens_spent: ~2000
    - should_be_in: `CLAUDE.md` or a memory file documenting conversation storage paths
  - Topic: "Three-lens review process" — re-read PROMPTS.md from v1 to understand the lens workflow, despite this being the user's own established process.
    - tokens_spent: ~1500
    - should_be_in: A persistent skill doc or the review workflow skill
- **missing_infrastructure:**
  - type: skill | A "review-cycle" skill that encodes the three-lens process, session selection, batch sizing, and synthesis steps — would eliminate the need to re-derive this each review cycle.
  - type: memory | Conversation storage path mapping (`~/.claude/projects/<slug>/` structure) as a reference memory file.
- **key_decisions:**
  - Built index-conversations.py to scan Claude Code storage (good — infrastructure investment)
  - Launched 3 lens agents in parallel rather than 15 separate ones (efficient batching decision)
  - Created tf-* task IDs and wired them into the pipeline (structural improvement)
- **unpersisted_knowledge:**
  - The exact path structure for Claude Code conversations per project
  - The indexer's discovery that 149 of 174 sessions were legacy pre-project-slug format
  - The specific batching strategy for lens analysis (3 agents x all batches vs 15 agents x 1 batch each)
- **top_learning_improvement:** A "review-cycle" skill would eliminate the ~3500 tokens spent re-deriving the three-lens process each time.

---

### Session 2: `7f03b0df-d77f` (AnnaPlanna project scaffolding)

- **learning_score:** 3
- **repeated_research:**
  - Topic: "How to scaffold a new project in THE_FACTORY" — read templates/new-project-init.md, INIT.md, IMPLEMENTATION_PROMPT.md, prior conversation summary. Multiple file reads to reconstruct the scaffolding workflow.
    - tokens_spent: ~3000
    - should_be_in: The project-scaffold skill should be self-contained with all steps
  - Topic: "Vite + Tailwind configuration" — tried Vite 8 (incompatible with Node 20), fell back to Vite 6. Tried Tailwind 4 Vite plugin approach, had to switch to Tailwind 3 PostCSS approach.
    - tokens_spent: ~2000
    - should_be_in: A LEARNINGS.md entry or environment skill noting Node version constraints
- **missing_infrastructure:**
  - type: memory | Node version (20.18) and compatible tool versions (Vite <=6, Tailwind 3 via PostCSS)
  - type: skill | The project-scaffold skill should include environment compatibility checks
- **key_decisions:**
  - Chose to bypass Supabase and use localStorage for MVP (good pivot when user pushed back on infrastructure complexity)
  - Chose Vite over Next.js (appropriate for lightweight app)
- **unpersisted_knowledge:**
  - Node 20.18 is incompatible with Vite 8
  - Tailwind 4 Vite plugin approach does not work with Tailwind 3 config patterns
  - The full localStorage-based auth pattern that was built (reusable for other MVPs)
- **top_learning_improvement:** Environment compatibility constraints (Node version, framework versions) should be persisted as a memory file to avoid trial-and-error in future scaffolding.

---

### Session 3: `99ffb4e3-5f81` (CRUCIBLE setup + RunEngine + UI)

- **learning_score:** 3
- **repeated_research:**
  - Topic: "Agent infrastructure alignment with THE_FACTORY conventions" — had to re-read THE_FACTORY CLAUDE.md and compare with CRUCIBLE's structure field-by-field.
    - tokens_spent: ~2000
    - should_be_in: A project-scaffold checklist or linting hook
  - Topic: "E2B and OpenAI API setup" — user didn't know how to get API keys; agent had to explain the difference between ChatGPT Plus and API access.
    - tokens_spent: ~500
    - should_be_in: A setup guide or memory file for required service accounts
- **missing_infrastructure:**
  - type: hook | A convention-alignment checker that validates project structure against THE_FACTORY conventions automatically
  - type: doc | API key setup guide listing all services used across projects and how to obtain/configure them
- **key_decisions:**
  - Accidentally echoed API keys in terminal output (INCIDENT — keys exposed in conversation history)
  - Built RunEngine as EventEmitter-based extraction from CLI (good architectural decision)
  - Built full UI with SQLite backend in a single session (ambitious scope, completed successfully)
- **unpersisted_knowledge:**
  - The Langfuse 401 error was caused by incorrect host URL — needed `https://us.cloud.langfuse.com` specifically
  - The `set -e` + `pipefail` interaction that caused false test failures from stderr output
  - SQLite + better-sqlite3 as the lightweight persistence choice for CRUCIBLE UI
- **top_learning_improvement:** An API key validation step at project setup time (checking connectivity, not echoing values) would prevent the key exposure incident and the Langfuse 401 debugging cycle.

---

### Session 4: `1b2da80d-5e75` (Strata Phase 2-5: visualization + multi-agent coordination)

- **learning_score:** 5
- **repeated_research:**
  - Topic: "WaveformCanvas component API" — re-read the same component that was read/modified in multiple prior sessions.
    - tokens_spent: ~1000
    - should_be_in: The waveform-rendering skill already exists but wasn't loaded first
  - Topic: "Track analysis data model (TrackAnalysis, RGBWaveform)" — re-explored type definitions.
    - tokens_spent: ~500
    - should_be_in: The codebase-orientation skill (which was created in session 11 but might not have been loaded)
- **missing_infrastructure:**
  - type: memory | A "SCUE component registry" mapping component names to file paths, props, and data dependencies
- **key_decisions:**
  - Successfully coordinated 3 agents in parallel (operator + frontend-compare + backend-engine) via teammate messages
  - Chose canvas-based rendering over DOM for ArrangementMap (performance-correct for dense data)
  - Deferred full backend verification when backend server wasn't running (pragmatic)
- **unpersisted_knowledge:**
  - The teammate-message protocol for multi-agent coordination patterns
  - The specific canvas drawing pipeline order (section bands -> beatgrid -> waveform -> overlays)
  - Demucs stem separation caching strategy (`strata/{fingerprint}/stems/{stem}.wav`)
- **top_learning_improvement:** This session was well-executed; the main gap is that the teammate-message coordination protocol should be documented as a skill for future multi-agent sessions.

---

### Session 5: `0c73b5f7-7b6c` (Waveform Rendering Tuning Page implementation)

- **learning_score:** 5
- **repeated_research:**
  - Minimal — this session read LEARNINGS.md, CLAUDE.md, specs, and existing code efficiently before starting work.
    - tokens_spent: ~0 wasted
    - should_be_in: N/A — good use of existing docs
- **missing_infrastructure:**
  - None significant — this session benefited from a complete spec, existing skill docs, and LEARNINGS.md
- **key_decisions:**
  - Followed the spec precisely (spec-first workflow working well)
  - Updated all 6 documentation files after implementation (thorough)
- **unpersisted_knowledge:**
  - The WebGL rendering pipeline for waveform presets (gradient calculation, smoothing, color mapping)
  - The seed preset YAML format and backend API patterns
- **top_learning_improvement:** This session demonstrates the ideal: when specs, skills, and learnings docs are in place, sessions are efficient and low-waste.

---

### Session 6: `63561724-20a7` (Waveform rendering frequency band tuning — spec phase)

- **learning_score:** 4
- **repeated_research:**
  - Topic: "Pioneer waveform rendering techniques" — launched a web research agent that hit API rate limits and failed. Research had to be re-done manually.
    - tokens_spent: ~1500 wasted on failed agent
    - should_be_in: Existing research doc `research/findings-waveform-frequency-color-rendering.md` already had this info
  - Topic: "ADR-018 waveform rendering decisions" — searched for and read this ADR, which documented the exact problem being investigated.
    - tokens_spent: ~500
    - should_be_in: LEARNINGS.md (which it was — but wasn't checked early enough)
- **missing_infrastructure:**
  - type: skill | The waveform-rendering skill should cross-reference existing research docs to prevent re-research
- **key_decisions:**
  - Created a spec rather than jumping to implementation (correct flow adherence)
  - Created task ID `wf-render-tuning-page` following the new protocol (protocol adoption)
- **unpersisted_knowledge:**
  - The logarithmic frequency band weighting formula for Pioneer-style rendering
  - The specific parameters that control bass dominance in waveform visualization
- **top_learning_improvement:** The LEARNINGS.md entry about ADR-018 existed but was read too late; a skill doc should front-load "read existing research before doing new research."

---

### Session 7: `495b5994-e258` (Annotation followup: beatgrid, event toggles, playback state)

- **learning_score:** 3
- **repeated_research:**
  - Topic: "WaveformCanvas, AnnotationTimeline, DeckWaveform component APIs" — re-read all three canvas components to understand drawing patterns, despite these being modified in sessions 4, 5, and 6.
    - tokens_spent: ~2000
    - should_be_in: A component registry memory file or the codebase-orientation skill
  - Topic: "How beats/downbeats flow to frontend components" — traced data flow from backend to component props again.
    - tokens_spent: ~1000
    - should_be_in: The data-flow section of interfaces.md or codebase-orientation skill
- **missing_infrastructure:**
  - type: memory | A "component API reference" for the 3 canvas components (props, data dependencies, draw pipeline)
  - type: skill | "Global playback state architecture" — the session designed a reactive playback state system but the architecture was ad-hoc
- **key_decisions:**
  - Designed a global PlaybackStore with reactive subscriptions (good architectural decision, planned for single source of truth)
  - User pushed for unified data flow pattern; agent designed Root -> Global -> Page-specific pipeline
- **unpersisted_knowledge:**
  - The full PlaybackStore architecture (source selection, global processes, page-specific overrides)
  - The event toggle UI pattern (checkbox per event type with visibility state)
  - The "scue-backend" vs "backend" launch.json naming issue (recurring error)
- **top_learning_improvement:** A component API reference for the 3 waveform canvas components would save ~3000 tokens per session that touches them.

---

### Session 8: `9a419670-41fa` (Strata proposal + Phases 0-1 implementation)

- **learning_score:** 4
- **repeated_research:**
  - Topic: "SCUE codebase architecture" — re-read ARCHITECTURE.md, interfaces.md, MILESTONES.md, models.py extensively.
    - tokens_spent: ~3000
    - should_be_in: The codebase-orientation skill (created later in session 11)
  - Topic: "M7 event detection patterns" — re-explored detector framework.
    - tokens_spent: ~500
    - should_be_in: The M7 skill or detector-tuning skill
- **missing_infrastructure:**
  - type: skill | Codebase orientation for SCUE (created later but not available here)
- **key_decisions:**
  - Added a "Standard" analysis tier between Quick and Deep (good user-driven refinement)
  - Designed the Strata page as a combined view/edit/compare interface (evolved from user discussion)
  - Correctly identified that wf-render-tuning was safe to parallelize with Strata work
- **unpersisted_knowledge:**
  - The three-tier analysis design rationale (Quick: existing M7, Standard: demucs + per-stem M7, Deep: future ML)
  - The Strata data model (ArrangementFormula -> sections -> layers -> patterns -> events)
  - Phase handoff prompts for multi-session features
- **top_learning_improvement:** Phase handoff prompts (session 8 produced one for phase 2) should be templated as a skill pattern, not ad-hoc each time.

---

### Session 9: `bca50125-1675` (CRUCIBLE — wrong-project confusion)

- **learning_score:** 1
- **repeated_research:**
  - Topic: "Where is SCUE?" — Agent was dispatched to CRUCIBLE context but given a SCUE task. Read 5 CRUCIBLE files before realizing it was in the wrong project.
    - tokens_spent: ~2000 completely wasted
    - should_be_in: The dispatch prompt should include the project path
- **missing_infrastructure:**
  - type: dispatch template | Task dispatches should always include the absolute project path, not assume the agent knows where to find the project
- **key_decisions:**
  - Session effectively failed — only 3 reads before dying
- **unpersisted_knowledge:**
  - N/A (session produced nothing)
- **top_learning_improvement:** Task dispatch templates MUST include absolute project paths; dispatching a SCUE task to a CRUCIBLE context wastes the entire session.

---

### Session 10: `12c56fb3-8fe0` (Export conversations for dad)

- **learning_score:** 3
- **repeated_research:**
  - Topic: "How Claude Code stores conversations on disk" — launched an Agent to explore `~/.claude/` storage, same question investigated in session 1.
    - tokens_spent: ~1500
    - should_be_in: Memory file with conversation storage paths (identified as missing in session 1 too)
- **missing_infrastructure:**
  - type: memory | Claude Code conversation storage layout (this is now the second time this was researched)
- **key_decisions:**
  - Built a general-purpose export script (good — reusable)
  - Created a paste-in prompt for a non-technical user (good UX thinking)
- **unpersisted_knowledge:**
  - The export script itself was written to `support/export-conversations.py` (persisted)
  - The conversation JSONL format details (message structure, roles, timestamps)
- **top_learning_improvement:** The Claude Code conversation storage layout has now been researched twice; a memory file would prevent a third time.

---

### Session 11: `c3838b2f-0517` (v1.9->v2.0 migration — full review + execution)

- **learning_score:** 4
- **repeated_research:**
  - Topic: "Three-lens review process" — re-derived the lens workflow (third time across sessions).
    - tokens_spent: ~1000
    - should_be_in: A review-cycle skill
  - Topic: "Conversation mining workflow" — re-read PROMPTS.md from v1 archive.
    - tokens_spent: ~500
    - should_be_in: The review-cycle skill
- **missing_infrastructure:**
  - type: skill | Review-cycle skill (now a pattern seen 3 times)
  - type: hook | Convention-alignment checker for project scaffolding
- **key_decisions:**
  - Chose "medium aggression" v2 migration approach (balanced risk/reward)
  - Created codebase-orientation skills, beat-link API reference skills
  - Set up `.venv` for THE_FACTORY eval suite
  - Wired Langfuse tracing hook
- **unpersisted_knowledge:**
  - The medium vs. aggressive migration decision rationale
  - API key management best practices (user asked about agent key handling)
  - The full v2 migration execution sequence
- **top_learning_improvement:** This massive session (30 user messages, 284 tool calls) would have been more efficient split into focused sub-sessions with handoff prompts.

---

### Session 12: `588a6128-9d0b` (PABProject scaffolding + MVP)

- **learning_score:** 3
- **repeated_research:**
  - Topic: "Project scaffolding workflow" — re-read templates/new-project-init.md (same as session 2).
    - tokens_spent: ~500
    - should_be_in: Project scaffold skill should be self-contained
  - Topic: "PDF extraction approaches" — discovered reference PDF was image-based (not text-extractable), needed OCR.
    - tokens_spent: ~1000
    - should_be_in: A "document ingestion" skill or research finding
  - Topic: "10 CFR 830.203 USQ questions" — needed exact regulatory text but couldn't extract from PDF.
    - tokens_spent: ~500
    - should_be_in: Domain skill for PABProject (eventually created in session 15)
- **missing_infrastructure:**
  - type: skill | Document ingestion skill (PDF parsing, OCR, chunking strategies)
  - type: domain skill | Nuclear safety regulatory reference (10 CFR 830, DOE-STD-3009)
- **key_decisions:**
  - Chose agent-per-question architecture for USQ evaluation (good for isolation/parallelism)
  - Chose to use full-power LLM for chunking relevance scoring (user explicitly said not to sacrifice quality)
  - Encountered API billing issues (OpenAI credits, Chrome extension debugging)
- **unpersisted_knowledge:**
  - Image-based PDFs require OCR for text extraction (poppler alone insufficient)
  - The 7 USQ screening questions from 10 CFR 830.203
  - The DSA chapter structure (Ch. 3-5 are the backbone for accident analysis)
- **top_learning_improvement:** A document ingestion skill would prevent the trial-and-error around PDF parsing that consumed ~1000 tokens.

---

### Session 13: `48a05e83-3ad2` (SongFormer research for SCUE)

- **learning_score:** 5
- **repeated_research:**
  - Minimal — focused WebFetch + project documentation. Efficient session.
    - tokens_spent: ~0 wasted
- **missing_infrastructure:**
  - None — session was well-scoped (research + document)
- **key_decisions:**
  - Correctly placed findings in `research/findings-*` following SCUE conventions
  - Noted CUDA-only limitation as a risk for macOS development
- **unpersisted_knowledge:**
  - All knowledge was persisted to the research findings doc (good)
- **top_learning_improvement:** This session is a model for efficient research-and-document workflows.

---

### Session 14: `4733ad72-8370` (SCUE: M7 tuning + annotation page)

- **learning_score:** 3
- **repeated_research:**
  - Topic: "M7 event detection status" — had to re-explore whether M7 was already built (it was largely implemented).
    - tokens_spent: ~1500
    - should_be_in: tasks.jsonl status + state-snapshot.json
  - Topic: "Frontend component patterns" — re-read AnnotationPage, App.tsx, Sidebar patterns.
    - tokens_spent: ~1000
    - should_be_in: Codebase-orientation skill
  - Topic: "Tinyshop confusion" — agent initially confused Tinyshop tasks with SCUE tasks.
    - tokens_spent: ~200
    - should_be_in: Tasks should have project prefixes
- **missing_infrastructure:**
  - type: convention | Task IDs should include project prefix (e.g., `scue-m7-tune` not just `m7-tune`)
- **key_decisions:**
  - User requested annotation page as own tab (correct UX separation)
  - Planned for single-source-of-truth playback state across app
  - Produced handoff prompts for next agent (good practice, becoming a pattern)
- **unpersisted_knowledge:**
  - The annotation page architecture (event list with toggles, waveform overlay, audio-synced playback)
  - The beatgrid line rendering approach (adaptive density based on zoom level)
  - Launch.json naming discrepancy ("scue-backend" vs "backend")
- **top_learning_improvement:** The launch.json naming issue ("scue-backend" vs "backend") has recurred multiple times and should be fixed once, not noticed repeatedly.

---

### Session 15: `16207a75-ec4c` (PABProject domain research)

- **learning_score:** 4
- **repeated_research:**
  - Minimal — this was primarily new domain research dispatched to 3 parallel agents.
    - tokens_spent: ~0 wasted
- **missing_infrastructure:**
  - type: domain skill | Nuclear safety regulatory reference (this session's output should become one)
- **key_decisions:**
  - Dispatched 3 parallel research agents (USQD process, DSA/TSR structure, AI/NLP for nuclear safety)
  - Synthesized into a single comprehensive research doc
- **unpersisted_knowledge:**
  - The research was persisted to `projects/PABProject/docs/research-usqd-domain.md` (good)
  - None of the agents could fetch DOE G 424.1-1C (the authoritative USQD guidance) — this gap is documented but unresolved
- **top_learning_improvement:** The unfetchable DOE guidance document should be manually obtained and added to the project's reference library.

---

### Session 16: `8794e968-2a15` (Pipeline architecture review + SYNTROPY genesis)

- **learning_score:** 4
- **repeated_research:**
  - Topic: "What tools exist for agent governance/observability" — broad web research on existing frameworks (Braintrust, Langfuse, Arize, etc.)
    - tokens_spent: ~3000
    - should_be_in: A research findings doc (was produced this session)
  - Topic: "Problem decomposition theory" — deep research into Herbert Simon, Polya, TRIZ, etc.
    - tokens_spent: ~2000
    - should_be_in: Was persisted to SYNTROPY/claude/ docs
- **missing_infrastructure:**
  - type: research | A "landscape" reference for agent tooling (Braintrust, Langfuse, DSPy, etc.) — what each does and how it maps to THE_FACTORY
- **key_decisions:**
  - Reframed THE_FACTORY from "pipeline that builds software" to "experimentation platform that discovers best agent workflows"
  - Identified CRUCIBLE as Phase 1 of the experimentation vision
  - Created SYNTROPY concept (problem decomposition theory applied to agent workflows)
- **unpersisted_knowledge:**
  - The agent tooling landscape mapping (what to adopt vs build)
  - The four-phase migration plan
  - The connection between SYNTROPY theory and CRUCIBLE experimentation
- **top_learning_improvement:** The agent tooling landscape (Braintrust, Langfuse, DSPy, Inspect, etc.) should be a persistent reference doc since it informs architectural decisions across all projects.

---

### Session 17: `325993fe-a1a2` (SuperTimecodeConverter research for SCUE)

- **learning_score:** 5
- **repeated_research:**
  - Minimal — focused research + documentation, similar to session 13.
    - tokens_spent: ~0 wasted
- **missing_infrastructure:**
  - None significant
- **key_decisions:**
  - Correctly identified 5 integration approaches ranked by effort/value
  - Stored findings as a reference memory file
- **unpersisted_knowledge:**
  - All persisted (research findings + memory file)
- **top_learning_improvement:** Good model session — research, evaluate, document, done.

---

### Session 18: `791de3a3-d4f6` (Stem separation + acoustic event detection research)

- **learning_score:** 3
- **repeated_research:**
  - Topic: "Stem separation state of the art" — extensive web research and agent dispatches on Demucs, BS-RoFormer, etc.
    - tokens_spent: ~4000
    - should_be_in: The SCUE research folder (was eventually persisted)
  - Topic: "Acoustic event detection approaches" — CLAP, prototypical networks, few-shot classification.
    - tokens_spent: ~3000
    - should_be_in: Was persisted to research docs
  - Note: The agent got cut off mid-session and had to restart, losing context.
- **missing_infrastructure:**
  - type: convention | Research docs from different AI providers (GPT vs Claude) were initially mixed together; user had to redirect to separate subdirectories.
- **key_decisions:**
  - User directed Claude to place research in `research/claude/` subdirectory separate from GPT research — establishing a cross-provider research organization pattern
- **unpersisted_knowledge:**
  - The comparison between GPT and Claude research findings on the same topic
  - The specific EDM-challenges for stem separation (overlapping synth/drum frequencies)
- **top_learning_improvement:** Research sessions should check for existing research docs on the same topic before launching new research agents.

---

### Session 19: `8b2abbae-c5d3` (SYNTROPY critique and experiment design)

- **learning_score:** 4
- **repeated_research:**
  - Topic: "SYNTROPY documents" — re-read all SYNTROPY docs from sessions 16, 18.
    - tokens_spent: ~2000
    - should_be_in: This is expected for a critique session (needs full context)
- **missing_infrastructure:**
  - None — the session's purpose was to produce critique + experiment design
- **key_decisions:**
  - Proposed a 5-level experiment ladder (L0 baseline through L4 feedback loops)
  - Selected section boundary detection as the trivial test case
  - Designed adaptive climbing (stop when improvement flattens)
- **unpersisted_knowledge:**
  - Persisted to SYNTROPY/claude/ docs (experiment-001-*.md files)
- **top_learning_improvement:** The experiment framework design should be reusable as a template for future SYNTROPY experiments.

---

### Session 20: `614eab46-4cf5` (SYNTROPY reality check #2)

- **learning_score:** 4
- **repeated_research:**
  - Topic: "SYNTROPY documents" — re-read all SYNTROPY/claude/ docs again.
    - tokens_spent: ~2000
    - should_be_in: Expected for critique session
- **missing_infrastructure:**
  - None significant
- **key_decisions:**
  - Key insight: the arrangement formula tool IS the experiment subject, not a toy subtask of it
  - Recommended using the real pipeline as the test case instead of an artificially simple one
- **unpersisted_knowledge:**
  - Persisted to SYNTROPY/claude/realityCheck2.md (good)
- **top_learning_improvement:** Sequential critique sessions (realityCheck1 -> realityCheck2) are an effective pattern for refining experimental designs.

---

### Session 21: `4a4ceb99-f5f2` (Runoff — pipeline adapter for constrained environments)

- **learning_score:** 5
- **repeated_research:**
  - Minimal — read source flow skills and profile.yaml, then generated output efficiently.
    - tokens_spent: ~0 wasted
- **missing_infrastructure:**
  - None — well-scoped task with clear inputs/outputs
- **key_decisions:**
  - Applied all 10 transformation rules from adapter-prompt.md
  - Self-verified output (line count check, grep for prohibited references)
- **unpersisted_knowledge:**
  - The transformation rules and their application patterns (persisted in Runoff docs)
- **top_learning_improvement:** Self-verification checklist pattern (line count, prohibited content grep) should be standard for generation tasks.

---

### Session 22: `ffab20a9-ff3e` (Empty session)

- **learning_score:** N/A
- No content to analyze.

---

### Session 23: `ff2f5f32-8616` (CRUCIBLE — developer task, incomplete)

- **learning_score:** 2
- **repeated_research:**
  - Topic: "CRUCIBLE project structure" — read AGENT_BOOTSTRAP.md, preambles. Session died after 3 reads.
    - tokens_spent: ~1000 with no output
    - should_be_in: N/A (session failure, not knowledge gap)
- **missing_infrastructure:**
  - type: dispatch | Session failed silently — no incident logged, no handoff produced
- **key_decisions:**
  - N/A (session incomplete)
- **unpersisted_knowledge:**
  - Whatever context was built from reading 3 files was lost entirely
- **top_learning_improvement:** Sessions that die early should auto-log an incident with what was read and where the task was left.

---

### Session 24: `f9a06739-3890` (Brainstorm skill creation)

- **learning_score:** 5
- **repeated_research:**
  - Minimal — read existing skill patterns and research findings to establish format.
    - tokens_spent: ~0 wasted
- **missing_infrastructure:**
  - None — session created the brainstorm skill itself
- **key_decisions:**
  - Created brainstorm as a portfolio-level skill (not a flow)
  - Defined 4-phase process with JSONL output contract
  - Added eval cases for the skill
  - Updated CLAUDE.md trigger table and flow routing
- **unpersisted_knowledge:**
  - All knowledge persisted (skill, evals, constitution updates)
- **top_learning_improvement:** This session shows good "infrastructure-first" thinking — creating the reusable pattern before needing it.

---

### Session 25: `f8b10c65-d6e0` (Empty session)

- **learning_score:** N/A
- No content to analyze.

---

## CROSS-SESSION SUMMARY

### Top 3 Knowledge Gaps That Recur Across Sessions

**1. Codebase orientation / component API reference for SCUE** (Sessions 4, 5, 6, 7, 8, 14)
- The WaveformCanvas, AnnotationTimeline, and DeckWaveform components are re-read in nearly every SCUE frontend session.
- Each re-read costs ~1000-2000 tokens and 3-5 tool calls.
- A codebase-orientation skill was eventually created (session 11) but the component API details (props, data dependencies, draw pipeline order) are not detailed enough to prevent re-reading source files.
- **Estimated total waste:** ~8000-12000 tokens across 6 sessions.

**2. Claude Code conversation storage layout** (Sessions 1, 10, and implicitly session 11)
- The `~/.claude/projects/<slug>/` path structure was independently researched at least twice, with Agent subprocesses launched each time.
- **Estimated total waste:** ~3500 tokens across 2 sessions.
- This was identified as a gap in session 1 but never actually persisted as a memory file.

**3. Review cycle / three-lens process** (Sessions 1, 11, and the current session)
- The three-lens review workflow (Process Efficiency, Quality & Correctness, Learning & Knowledge) has been re-derived from v1 PROMPTS.md at least 3 times.
- Each re-derivation involves reading archived documents and reconstructing the batch strategy.
- **Estimated total waste:** ~3000-5000 tokens across 3 sessions.

### Highest-Value Skill/Hook/Memory Candidates (by frequency x cost)

| Rank | Type | Name | Frequency | Cost/Instance | Sessions Affected | Priority |
|------|------|------|-----------|---------------|-------------------|----------|
| 1 | memory | SCUE component API reference (WaveformCanvas, AnnotationTimeline, DeckWaveform props, data deps, draw pipeline) | 6 sessions | ~1500 tokens | 4,5,6,7,8,14 | CRITICAL |
| 2 | skill | Review-cycle skill (three-lens process, session selection, batching, synthesis) | 3 sessions | ~1500 tokens | 1,11,current | HIGH |
| 3 | memory | Claude Code conversation storage layout (`~/.claude/projects/<slug>/` structure) | 2+ sessions | ~1750 tokens | 1,10 | HIGH |
| 4 | memory | Environment compatibility (Node 20.18 -> Vite <=6, Tailwind 3 PostCSS) | 1 session (high single cost) | ~2000 tokens | 2 | MEDIUM |
| 5 | hook | Project-convention alignment checker (validates .agent/ structure, tasks.jsonl format, etc.) | 2 sessions | ~2000 tokens | 3,11 | MEDIUM |
| 6 | template | Phase handoff prompt template (for multi-session features) | 3 sessions | ~500 tokens | 4,8,14 | MEDIUM |
| 7 | convention | Task ID project prefixes (scue-xxx, crucible-xxx, pab-xxx) | 1 session | ~200 tokens | 14 | LOW |
| 8 | fix | launch.json naming ("scue-backend" -> "backend") | 3+ sessions | ~100 tokens each but recurring | 7,14+ | LOW (but fix once) |

### Decision Patterns: What Types of Decisions Most Often Lead to Rework?

**1. Environment/tooling assumptions (3 instances)**
- Assuming Vite 8 works with Node 20 (session 2) -> rollback to Vite 6
- Assuming Tailwind 4 plugin approach works (session 2) -> switch to Tailwind 3 PostCSS
- Assuming Supabase is needed for MVP (session 2) -> user-directed pivot to localStorage
- **Pattern:** Framework/tool version compatibility is not validated before starting implementation.
- **Fix:** A pre-implementation environment check step in the feature-flow skill.

**2. Wrong-context dispatch (2 instances)**
- SCUE task dispatched to CRUCIBLE context (session 9) -> session wasted
- Tinyshop tasks confused with SCUE tasks (session 14) -> minor rework
- **Pattern:** Task dispatches don't always include explicit project paths or context boundaries.
- **Fix:** Dispatch template that requires absolute project path.

**3. Research-before-reading-existing-docs (3 instances)**
- Launched web research on Pioneer waveforms when ADR-018 + existing research doc already covered it (session 6)
- Re-researched conversation storage when session 1 had already explored it (session 10)
- Re-derived three-lens process when it was documented in v1 PROMPTS.md (sessions 1, 11)
- **Pattern:** New research is launched before checking what already exists in the project's research/ folder, LEARNINGS.md, or memory files.
- **Fix:** Add a "check existing knowledge" gate to the research/brainstorm flow — mandatory step: search `research/`, `LEARNINGS.md`, memory files, and `DECISIONS.md` before dispatching any research agent.

### Notable Positive Patterns

1. **Sessions with complete specs are dramatically more efficient** (session 5 vs session 2). When a spec exists, the implementation session has near-zero repeated research.
2. **Multi-agent coordination is improving.** Session 4 successfully coordinated 3 agents via teammate messages. Session 15 ran 3 parallel research agents effectively.
3. **The handoff-prompt pattern is emergent and valuable.** Sessions 4, 8, and 14 all produced prompts for successor agents. This should be formalized as a standard session-end artifact.
4. **User-directed pivots are handled well.** The Supabase->localStorage pivot (session 2) and the SYNTROPY reality checks (sessions 19-20) show good adaptive decision-making.
5. **Research-then-document sessions (13, 17) are the most efficient pattern** — focused scope, clear inputs/outputs, near-zero waste.

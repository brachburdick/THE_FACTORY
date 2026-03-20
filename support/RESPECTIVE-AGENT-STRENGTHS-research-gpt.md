# RESPECTIVE-AGENT-STRENGTHS research-gpt

Status: Draft for review  
Prepared: March 20, 2026

## Scope

This note summarizes the current public consensus on the strengths of the most recent frontier models relevant to agentic technical work:

- OpenAI `GPT-5.4` and `GPT-5.4 pro`
- Anthropic `Claude Sonnet 4.6` and `Claude Opus 4.6`
- Google `Gemini 3.1 Pro`
- xAI `Grok 4.1` and `grok-code-fast-1`
- Open-weight references: `DeepSeek V3.2-Exp` and `Qwen3-2507`

Method:

- Prioritized official model cards, vendor docs, and benchmark pages current as of March 20, 2026.
- Used public benchmark results as signals, not absolute truth.
- Marked claims as inference where public benchmarking is thin, especially for self-assessment and subagent management quality.

Important caveat:

- Agentic coding results are harness-sensitive. A model that leads in one scaffold can trail in another. The useful question is not "who wins every leaderboard," but "which model is most reliable for the workflow you actually run."

## Executive Summary

If the job is long-running autonomous software engineering, current consensus still leans `Claude`, especially `Claude Opus 4.6` and `Claude Sonnet 4.6`.

If the job is strict steerability, instruction retention, tool governance, and cross-application professional work, current consensus leans `GPT-5.4`.

If the job is giant-context research, multimodal analysis, and digesting huge repositories or large mixed-source corpora, current consensus leans `Gemini 3.1 Pro`.

If the job is live-web, X-native, current-events-heavy research, `Grok 4.1` is the specialist.

If the job is open deployment and value, `DeepSeek V3.2-Exp` and `Qwen3-2507` are the strongest open-weight reference points, with `Qwen3-2507` looking better on instruction following and tool use claims, and `DeepSeek` looking stronger on raw coding and reasoning efficiency.

## Consensus By Capability

| Capability | Best current fit | Confidence | Notes |
| --- | --- | --- | --- |
| Research | `Gemini 3.1 Pro` | High | Best current public mix of long context, multimodal digestion, BrowseComp performance, and repo-scale comprehension. `Grok 4.1` is the specialist if research means live web plus X. |
| Making large plans that stay good while executed | `Claude Opus 4.6` / `Claude Sonnet 4.6` | Medium | Consensus leans Claude for long-horizon autonomy. Public product evidence around memory, context handling, and subagents supports this, but there is still no universal benchmark for "plan quality over hours." |
| Examining and critiquing large technical projects | `Claude Opus 4.6` | Medium-high | Claude has unusually strong public evidence on vulnerability finding and large-codebase critique. `Gemini 3.1 Pro` is extremely close when context size is the bottleneck. |
| Modifying large project infrastructure according to a plan | Split: `GPT-5.4`, `Claude 4.6`, `Gemini 3.1 Pro` | Medium | `GPT-5.4` looks best for cross-tool operator workflows, `Claude` for long autonomous engineering loops, `Gemini` for giant-context repo work. This is the most workflow-dependent category. |
| Foreseeing undiscovered problems while planning | `Claude Opus 4.6` | Medium | Slight edge to Claude due to public evidence on finding vulnerabilities and hidden failure modes at scale. |
| Abstraction that survives contact with implementation | `GPT-5.4` / `Gemini 3.1 Pro` | Medium | `GPT-5.4` is strongest at turning goals into controlled tool-execution plans. `Gemini` is strongest at compressing huge messy context into a workable implementation path. |
| Self-assessment | No clear winner | Low | No frontier model is trustworthy enough here without external verification. Relative lean: `GPT-5.4` for controllability, then `Claude` / `Gemini`. |
| Managing subagent dispatch | `Claude` | Medium | Anthropic has the strongest current public evidence and tooling story around subagents, separate context windows, and multi-agent orchestration. |
| Quality of subagent dispatch | `Claude` | Medium | Same reason as above. Strongest public evidence of actual multi-agent uplift. |
| Following instructions without forgetting them | `GPT-5.4` | Medium-high | OpenAI is most explicit about steerability, developer-message obedience, approvals, and tool discipline. `Gemini 3.1 Pro` is close. `Claude` is strong but can be more initiative-taking than requested. |

## Detailed Findings

### 1. Research

`Gemini 3.1 Pro` currently has the strongest public case for broad research work.

- Google describes it as its most advanced model for complex tasks.
- Its model card explicitly positions it for agentic performance, advanced coding, long context, multimodal understanding, and step-by-step planning.
- Public benchmark numbers are especially strong on `BrowseComp`, `MCP Atlas`, `Humanity's Last Exam`, and long-context retrieval.

`GPT-5.4` is a close second for research that must turn into deliverables such as documents, presentations, spreadsheets, or browser-driven workflows.

`Claude Opus 4.6` is also top-tier for deep analysis, but the consensus edge in pure research breadth currently goes to Gemini.

`Grok 4.1` deserves a separate note: if "research" means live internet, rapid current-events synthesis, and X-native signal, it is often the most situationally useful model even if it is not the best overall reasoning model.

### 2. Making Large Plans That Stay Good Over Time

Consensus leans `Claude`.

Why:

- Anthropic has invested heavily in long-running agent workflows, including context editing, memory tooling, and subagents.
- Anthropic's current documentation and product material are the clearest about maintaining performance over long-running tasks rather than just scoring well in a single short benchmark episode.
- Anthropic's own transparency material still notes that even `Opus 4.6` struggles with very long autonomous tasks and keeping track of large codebases, which is important because it shows both the strength and the current ceiling.

`Gemini 3.1 Pro` is the strongest challenger here because its public benchmark sheet is excellent on long-horizon and agentic tasks.

`GPT-5.4` is strongest when you want to inspect and redirect the plan while it is executing. Its practical edge is not "never drifts," but "is easier to steer back onto the rails."

### 3. Examining And Critiquing Large Technical Projects

Current lean: `Claude Opus 4.6`.

Why:

- Anthropic has public evidence that recent Claude models are genuinely useful for serious cybersecurity work.
- Anthropic has also publicly described Claude-based systems finding vulnerabilities at scale and assisting in real incident analysis.
- In practice, this maps well to critique work such as architecture review, dependency risk review, hidden failure mode hunting, and asking "what is wrong with this project that nobody has noticed yet?"

`Gemini 3.1 Pro` is nearly tied when the project is massive or multimodal and you need the model to absorb an enormous amount of context quickly.

`GPT-5.4` is especially strong when critique is only useful if it immediately turns into tool-driven inspection and edits.

### 4. Modifying Large Project Infrastructure According To A Plan

This category does not have a clean single winner.

Best practical split:

- Use `GPT-5.4` when the job crosses terminals, docs, spreadsheets, browsers, and heterogeneous tools.
- Use `Claude 4.6` when the job is primarily a long-running coding or codebase-maintenance loop.
- Use `Gemini 3.1 Pro` when the bottleneck is understanding an enormous repo or mixed modal corpus before changing it.

If forced to choose one default for "operator-style infrastructure work," I would lean `GPT-5.4`. If forced to choose one default for "stay in this codebase and grind through the migration," I would lean `Claude`.

### 5. Foreseeing Undiscovered Problems While Planning

Slight edge: `Claude Opus 4.6`.

This is partly inference, but it is supported by stronger public evidence than most vendors provide:

- Anthropic has published unusually concrete material around vulnerability discovery and cyber-defender workflows.
- That matters because the ability to spot hidden issues, attack paths, missing checks, and edge-case failures is very close to the planning skill of foreseeing problems before execution.

`GPT-5.4` and `Gemini 3.1 Pro` are both very strong here, but today the strongest public evidence still favors Claude.

### 6. Abstraction, As It Pertains To Rubber-Meets-Road Implementation

Best current fits: `GPT-5.4` and `Gemini 3.1 Pro`.

`GPT-5.4` is especially good when abstraction must become a concrete sequence of actions across tools and applications. OpenAI's current positioning of GPT-5.4 is heavily centered on professional workflows, computer use, and controllable agent execution.

`Gemini 3.1 Pro` is especially good when the abstraction layer is hard because the source material is huge, messy, multimodal, or repository-scale.

`Claude` remains excellent here, but it currently feels most differentiated after the implementation loop has already begun.

### 7. Self-Assessment

No frontier model should be trusted to grade itself without external checks.

Useful practical consensus:

- `GPT-5.4` has the cleanest current story around steerability, approvals, structured outputs, and workflow instrumentation.
- `Claude` is very strong, but Anthropic's own materials still note over-eager behavior in coding and computer-use settings.
- `Gemini 3.1 Pro` is powerful but has less public positioning around introspective trace control than OpenAI does.

Best current rule:

- Treat all self-assessment as advisory.
- Require tests, graders, or independent verification loops.

### 8. Managing Subagent Dispatch

Clear current edge: `Claude`.

Why:

- Anthropic's docs explicitly support subagents with their own context windows, tool permissions, prompts, and chaining patterns.
- Anthropic has also published an engineering writeup on a multi-agent research system and reported substantial lift from a lead-agent plus subagent setup.
- This is the strongest current public evidence from any vendor that the model family is not just compatible with multi-agent work, but meaningfully good at it.

`GPT-5.4` is good at workflow composition and typed node-style agent pipelines, but the public evidence is stronger for orchestrated workflows than for high-quality autonomous delegation.

`Gemini 3.1 Pro` is clearly strong at agentic execution, but the public multi-agent delegation story is not as mature or explicit as Anthropic's.

### 9. Quality Of Subagent Dispatch

Again, `Claude` has the best current public case.

Important distinction:

- Managing subagents means deciding when and how to use them.
- Quality of subagent dispatch means whether the decomposition is actually good, the delegated contexts are well-bounded, and the outputs come back useful rather than redundant or noisy.

Anthropic's internal multi-agent research system results are the strongest current public signal that Claude-based dispatch quality is genuinely high rather than merely supported in product UX.

### 10. Following A Set Of Instructions Without Forgetting Them

Current lean: `GPT-5.4`.

Why:

- OpenAI explicitly recommends GPT-5 models for stronger developer-instruction following and robustness against jailbreaks and indirect prompt injection.
- GPT-5.4 is also positioned around controllability, plan visibility, developer-message steering, tool approvals, and reduced factual error rate relative to prior GPT versions.

`Gemini 3.1 Pro` is a strong second. Google is making more explicit instruction-following claims than in earlier generations, and Gemini 3.1 Pro performs strongly in multi-step tool-use environments.

`Claude` remains very good, but the current consensus is that it is somewhat more likely than GPT to "help too much" unless you tightly box it in.

## Model Profiles

### `GPT-5.4`

Best at:

- Strict instruction following
- Steerability during execution
- Computer use and cross-application workflows
- Professional knowledge work outputs
- Turning plans into disciplined tool use

Best role label:

- "AI operator" or "AI project manager with hands"

Primary weakness relative to Claude:

- Slightly less consensus confidence on very long autonomous codebase work.

### `Claude Sonnet 4.6` and `Claude Opus 4.6`

Best at:

- Long-running coding and agentic engineering loops
- Subagent dispatch and delegation patterns
- Large-project critique and hidden-problem discovery
- Security and vulnerability-oriented reasoning

Best role label:

- "AI staff engineer"

Primary weakness relative to GPT:

- More over-eager in some agent settings, especially if not tightly permissioned or prompted.

### `Gemini 3.1 Pro`

Best at:

- Huge context windows and giant mixed-source inputs
- Multimodal research
- Repo-scale understanding
- Agentic coding benchmarks
- Converting enormous context into a usable plan

Best role label:

- "AI research architect" or "AI large-repo analyst"

Primary weakness relative to Claude:

- Slightly weaker public evidence on true multi-agent delegation quality.

### `Grok 4.1` and `grok-code-fast-1`

Best at:

- Fast current-events and web-native research
- X-native signal gathering
- Nimble day-to-day coding assistance

Best role label:

- "AI live-research scout"

Primary weakness:

- Less public evidence than GPT, Claude, or Gemini on deep long-horizon enterprise engineering reliability.

### `DeepSeek V3.2-Exp`

Best at:

- Open-weight value
- Strong reasoning and coding for cost
- Long-context efficiency research

Primary weakness:

- Benchmark reproducibility questions have been raised publicly, and the strongest closed models still lead on the hardest long-horizon agent work.

### `Qwen3-2507`

Best at:

- Open-weight instruction following
- Multilingual work
- Flexible tool-use integration
- Long-context open deployment

Primary weakness:

- Still not the safest default pick over the top closed models for the hardest autonomous engineering tasks.

## Bottom-Line Recommendations

If choosing one model per use case:

- Best overall autonomous engineer: `Claude Opus 4.6`
- Best cost-performance autonomous engineer: `Claude Sonnet 4.6`
- Best operator and instruction-follower: `GPT-5.4`
- Best giant-context researcher: `Gemini 3.1 Pro`
- Best live-web and X-heavy research agent: `Grok 4.1`
- Best open-weight value: `DeepSeek V3.2-Exp`
- Best open-weight instruction follower and multilingual generalist: `Qwen3-2507`

If choosing one model family to trust most for the exact capabilities in this prompt:

1. `Claude` for long autonomous engineering, critique, problem-spotting, and subagent dispatch
2. `GPT` for instruction retention, steerability, and cross-tool execution discipline
3. `Gemini` for research, giant-context digestion, and repo-scale planning

## Sources

Primary sources used for this draft:

- [OpenAI GPT-5.4 model docs](https://developers.openai.com/api/docs/models/gpt-5.4)
- [OpenAI GPT-5.4 pro model docs](https://developers.openai.com/api/docs/models/gpt-5.4-pro)
- [OpenAI GPT-5.4 announcement](https://openai.com/index/introducing-gpt-5-4/)
- [OpenAI Safety in building agents](https://platform.openai.com/docs/guides/agent-builder-safety)
- [Anthropic Transparency Hub model report](https://www.anthropic.com/transparency/model-report)
- [Anthropic context management announcement](https://www.anthropic.com/news/context-management)
- [Anthropic subagents docs](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Anthropic common workflows docs](https://docs.anthropic.com/en/docs/claude-code/common-workflows)
- [Anthropic multi-agent research system writeup](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Anthropic AI-orchestrated cyber espionage report](https://www.anthropic.com/news/disrupting-AI-espionage)
- [Google Gemini 3.1 Pro model card](https://deepmind.google/models/model-cards/gemini-3-1-pro/)
- [Google Gemini 3 Pro overview](https://deepmind.google/en/models/gemini/pro/)
- [xAI news index](https://x.ai/blog)
- [xAI Grok Code Fast 1](https://x.ai/news/grok-code-fast-1/)
- [DeepSeek V3.2-Exp official repo](https://github.com/deepseek-ai/DeepSeek-V3.2-Exp)
- [DeepSeek V3 official repo](https://github.com/deepseek-ai/DeepSeek-V3)
- [Qwen3 official repo](https://github.com/QwenLM/Qwen3)
- [SWE-bench Verified](https://www.swebench.com/verified.html)

## Review Notes

Open questions worth tightening in a later revision:

- Whether to split `Claude` recommendations more explicitly between `Sonnet 4.6` and `Opus 4.6`
- Whether to add a separate section on pricing and latency tradeoffs
- Whether to replace some vendor-claimed benchmark references with more third-party evaluation once comparable 2026 data stabilizes

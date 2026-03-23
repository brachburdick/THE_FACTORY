# Experiment 001 Plan Critique

**Date:** 2026-03-23
**Reviewer:** Codex
**Scope:** Review of `SYNTROPY/claude/experiment-001-execution-plan.md` and `SYNTROPY/claude/experiment-001-section-boundaries.md`
**Assumption:** "the plan" refers to Experiment 001 and its immediate supporting design note.

---

## Bottom Line

I think this is a good operational draft, but not yet a strong test of the core SYNTROPY hypothesis.

It is good at forcing the project out of theory and into a runnable procedure.
It is weaker at isolating whether principled decomposition helps on the kinds of failures
SYNTROPY actually cares about: bad boundaries, stage coupling, interface leaks, and
recombination problems in multi-stage pipelines.

If you run it as written, I would treat it as a **pilot** rather than as decisive evidence.

---

## What Looks Strong

- The ladder is simple enough that someone could actually run it.
- Fresh-session rules and intervention counting are good experimental hygiene.
- The adaptive stopping logic is pragmatic and keeps the experiment from becoming ceremonial.
- The results template is directionally right: it is trying to capture quality, overhead, and process failures, not just pass/fail.

---

## Main Critiques

### 1. The task is probably below the complexity band where SYNTROPY should matter

This is the biggest issue.

Section boundary detection is a useful domain artifact, but as framed here it is still a
single-stage, single-library, known-algorithm task. That means the likely outcomes are:

- `L0` succeeds, which mostly proves that frontier models can one-shot a straightforward `librosa` task
- `L3+` underperforms, which mostly proves that formal process is overhead on a toy problem

Neither outcome strongly tests the main SYNTROPY claim from the problem statement, which is
about decomposition improving reliability on non-trivial, compounding tasks.

The current plan is best at estimating the **lower bound** where decomposition is unnecessary.
It is not yet a good test of where decomposition starts paying for itself.

### 2. The experiment variables are confounded across levels

The ladder is presented as if each level adds one concept, but in practice each level changes
multiple things at once:

- prompt length
- implementation specificity
- interface detail
- verification burden
- implied architecture
- allowed reasoning style

`L1` is not only "decomposition"; it also injects a concrete architecture.
`L2` is not only "verification"; it adds execution ordering and extra integration expectations.
`L3` is not only "contracts"; it also bakes in domain assumptions and implementation details.

`L4` and `L5` are the biggest validity problem because they are not actually pre-registered
prompts. The plan says to draft them later if needed. That makes later comparisons much less
trustworthy because the operator will inevitably write those prompts with knowledge gained from
earlier runs.

### 3. The evaluator is too subjective and too small-n

The ground truth procedure relies on one track, one operator, and boundaries chosen by ear.
That is fine for a pilot, but too weak for claims like:

- "`L0` is sufficient for this complexity"
- "verification is not the lever"
- "contracts matter even at low complexity"

The current design has several sources of variance:

- one test track may be unusually easy or unusually clean
- one model run may be lucky or unlucky
- "major structural transition" is partly interpretive
- the matching method between expected and found boundaries is not formalized

At minimum, this needs either repeated runs on the same track or a small track set.
Ideally it also needs a simple evaluator script that defines how a predicted boundary list is
matched to ground truth before the experiment starts.

### 4. The verification and contract checks are weakly coupled to the real acceptance criteria

Most of the `L2` and `L3` checks validate syntax and array sanity, not whether the tool is
finding the right musical boundaries.

Examples:

- "array is non-empty"
- "no NaN values"
- "JSON parses"
- "exit code 0"
- "at least two boundaries"

These checks are useful as guardrails, but they do not pressure the hard part of the task.

Some of the contracts also look arbitrary or overly implementation-specific:

- duration must be between 30s and 600s
- no two boundaries within 5 seconds
- feature length must equal a specific frame formula

Those can reject valid implementations or push the agent toward satisfying the contract instead
of solving the task. A good contract should protect acceptance criteria, not accidentally
encode one implementation path.

### 5. Reproducibility and cost accounting are incomplete

The plan wants to compare outcome-to-overhead, but it does not yet preserve enough detail to
make the comparison durable:

- dependency versions are unpinned
- the exact prompt text used in a run is not captured in the results template
- the exact model build/version is not required
- token usage is named in the design note but not present in the execution-plan template
- no transcript or tool-call log is preserved
- no track provenance or track metadata standard is defined

That means the plan can generate useful impressions, but later reruns may not be comparable.

### 6. The decision policy stops too early for the strength of claim it wants to make

The current decision points are aggressive:

- if `L0` passes with 0 interventions, treat it as sufficient
- if `L1` does not beat `L0`, skip `L2`
- if `L2` does not beat `L1`, stop

That is efficient, but with only one run on one task it risks over-reading noise.

A better framing would be:

- one run can justify the next pilot
- repeated runs are needed before declaring a level "sufficient"
- "no improvement" should mean "no improvement across a small bundle of runs," not "one attempt looked flat"

---

## What I Would Change

### 1. Reframe Experiment 001 as a pilot

Say explicitly:

> This experiment is meant to surface operational friction and estimate the low-complexity floor, not to validate SYNTROPY overall.

That lowers the risk of drawing overly large conclusions from a thin setup.

### 2. Separate the common prompt core from the per-level delta

Pre-register:

- one shared task brief
- one shared acceptance-criteria block
- one shared environment block
- one delta block per level

That would make the comparisons much cleaner.

### 3. Prewrite every level prompt before running anything

Especially `L4` and `L5`.

If they are drafted after seeing earlier failures, the experiment stops being a clean ladder and
starts becoming interactive prompt refinement.

### 4. Improve the evaluator before trusting the conclusions

At minimum:

- define a matching rule for predicted vs expected boundaries
- run more than one track or more than one trial per level
- record exact prompt, model, runtime, and tokens for every run

### 5. Either use a harder task, or be explicit that this is only the lower-bound test

My preference would be to use the simplest multi-stage slice of the real pipeline.

If you keep section boundary detection, then say clearly that the point is:

- to test whether any decomposition overhead is justified on an easy domain task
- not to test the full SYNTROPY thesis

That makes the claims much more honest and much easier to interpret.

---

## Overall Judgment

I like the instinct behind this plan.

It is concrete, runnable, and much healthier than continuing to add theory without touching the
ground. But as a research instrument it is still a pilot-quality plan, not a decisive one.

If I were steering this, I would:

1. run it once as a pilot if the goal is to learn operational friction quickly
2. avoid making large claims from the result
3. then move fast to a slightly more compositional task where decomposition could actually win

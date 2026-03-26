# Proposal: Turn TF Automation Research into Action

## Intent

This proposal converts the findings from `/Users/brach/Downloads/deep-research-report TF Automation.md` into a practical improvement plan for THE_FACTORY.

The core recommendation is:

1. Productize the automation surfaces that already exist in this repo.
2. Standardize them around machine-readable outputs, stable state, and repeatable CI execution.
3. Stay GitHub-native first.
4. Add a Kubernetes/Argo control plane only after THE_FACTORY outgrows the GitHub-native baseline.

## What the research got right

The report correctly identifies that THE_FACTORY already has strong local automation primitives:

- deterministic enforcement in `.claude/hooks/`
- executable regression checks in `evals/`
- assessment and improvement logic in `scripts/assess.py`
- experiment execution in `scripts/experiment.py`
- state and telemetry ledgers in `.agent/`

The biggest real gap is also correctly identified: these capabilities are mostly local and operator-driven, not yet packaged as repeatable, centralized automation.

## Repo-grounded corrections before implementation

The report is directionally right, but a few details need tightening before we turn it into implementation:

- `scripts/assess.py` does not currently support an `--out` flag, so scheduled artifact generation is not yet drop-in.
- `scripts/experiment.py` prints results to stdout but does not emit a structured report file for downstream automation.
- Langfuse configuration is inconsistent today:
  - `LEARNINGS.md` says to use `LANGFUSE_BASE_URL`
  - `scripts/assess.py` currently reads `LANGFUSE_HOST`
- the hook surface is slightly richer than the report captured because `.claude/hooks/fix-attempt-tracker.sh` is also part of the current enforcement layer.

These are small gaps, but they matter. The first step should be to define an "automation contract" for the repo before wiring in schedulers.

## Recommendation

### Phase 0: Create an automation contract

Goal: make current scripts and hooks safe to run unattended.

Priority changes:

| Priority | Improvement | Why it matters | Acceptance signal |
|---|---|---|---|
| P0 | Add structured output support to `scripts/assess.py` | Nightly jobs need durable artifacts, not only stdout | `assess.py` can write JSON and Markdown reports to a caller-specified path |
| P0 | Add structured output support to `scripts/experiment.py` | Manual or scheduled experiments need comparable artifacts across runs | experiment runs produce a JSON summary with variant, status, metrics, and elapsed time |
| P0 | Normalize Langfuse env handling across docs and code | Current mismatch will create flaky CI and silent telemetry failures | one canonical variable name is documented and used consistently |
| P0 | Define stable exit semantics for unattended runs | CI needs clear pass/fail behavior | deterministic checks fail non-zero on real failures and succeed cleanly otherwise |
| P0 | Define a standard artifact location | Scheduled jobs need a known place to publish results | reports land in a documented folder such as `.agent/reports/` |

Recommended file targets:

- `/Users/brach/Documents/THE_FACTORY/scripts/assess.py`
- `/Users/brach/Documents/THE_FACTORY/scripts/experiment.py`
- `/Users/brach/Documents/THE_FACTORY/LEARNINGS.md`
- `/Users/brach/Documents/THE_FACTORY/README.md`

### Phase 1: Ship a GitHub-native baseline

Goal: turn the existing improvement loop into repeatable repo automation with minimal operational burden.

Recommended additions:

| Priority | Add | Scope | Why now |
|---|---|---|---|
| P1 | `.github/workflows/ci.yml` | Run deterministic evals on PR and push | This is the cleanest way to protect the protocol from drift |
| P1 | `.github/workflows/nightly-assess.yml` | Run `scripts/assess.py --last N` on a schedule and upload artifacts | Converts the improvement loop from ad hoc to continuous |
| P1 | `.github/workflows/experiment.yml` | Manual `workflow_dispatch` experiment runner | Preserves budget control while making experiments repeatable |
| P1 | concurrency and retention settings | Prevent overlapping runs and artifact sprawl | Reduces noise and keeps automation cheap |

Implementation notes:

- Use a repo-created virtualenv in workflows and run `.venv/bin/python` consistently to match the local operating model.
- Keep PR CI limited to deterministic checks in `evals/`.
- Keep LLM-dependent experiment runs manual or weekly until budgets and success criteria are mature.
- Upload artifacts from the assessment and experiment flows so results survive beyond terminal output.

### Phase 2: Close the loop on findings

Goal: make automation outputs feed decisions, not just storage.

Recommended changes:

- Add a lightweight report triage flow that turns nightly assessment output into a weekly review artifact.
- Define how improvement candidates move from `scripts/assess.py` into `PROTOCOL_IMPROVEMENTS.md` or a dedicated reviewed backlog.
- Record run metadata with stable identifiers so duplicate scheduled executions can be detected and ignored safely.
- Add a simple schema for automation runs: `run_id`, `trigger_type`, `source_ref`, `started_at`, `completed_at`, `status`, `artifacts`.

Why this matters:

- the research emphasizes idempotency and explicit state
- THE_FACTORY already thinks in ledgers and artifacts
- this phase extends the current philosophy instead of replacing it

Recommended file targets:

- `/Users/brach/Documents/THE_FACTORY/PROTOCOL_IMPROVEMENTS.md`
- `/Users/brach/Documents/THE_FACTORY/.agent/`
- `/Users/brach/Documents/THE_FACTORY/support/v2/`

### Phase 3: Improve observability without overbuilding

Goal: make unattended automation debuggable.

Recommended changes:

- emit machine-readable assessment and experiment summaries first
- add a single status summary document per run
- add basic counters for scheduled runs, failed runs, and skipped duplicate runs
- standardize hook and script timestamps in UTC ISO 8601

Important constraint:

Do not build a full OpenTelemetry, Prometheus, and Grafana stack until Phase 1 and Phase 2 are already stable. Right now, THE_FACTORY will get much more value from consistent artifacts than from a large observability platform.

### Phase 4: Only then consider Kubernetes and Argo

Goal: add a control plane only when scale actually demands it.

Adopt Kubernetes + Argo only if at least one of these becomes true:

- GitHub-hosted runners are too constrained for experiment duration or parallelism
- workflows need webhook-driven fan-out beyond GitHub events
- runs need custom compute, isolated networking, or long-lived batch infrastructure
- the team needs a central workflow UI and cluster-native retry policy management

Until then, GitHub Actions is the right baseline because it is cheaper, simpler, and close to the repo.

## Concrete 30-day roadmap

### Week 1

- add `--out` and structured report output to `scripts/assess.py`
- add structured JSON output to `scripts/experiment.py`
- normalize Langfuse env variable naming across code and docs
- document the standard artifact directory

### Week 2

- add PR/push CI for `evals/`
- add nightly scheduled assessment workflow
- upload artifacts for both workflows

### Week 3

- add manual experiment workflow with explicit inputs for task and variants
- define run naming and retention policy
- add concurrency controls to avoid overlapping jobs on the same ref

### Week 4

- review the first week of scheduled artifacts
- decide whether the output is sufficient or whether issue/comment automation is needed
- formalize how accepted improvement candidates move into protocol changes and eval coverage

## Proposed success metrics

Track these after rollout:

- every PR runs deterministic evals automatically
- at least one assessment artifact is generated per day without operator intervention
- experiment runs produce comparable JSON outputs across variants
- zero secret values appear in logs or artifacts
- duplicate scheduled runs are safely ignored or collapsed
- accepted automation improvements produce matching eval coverage

## What not to do yet

- do not start with Argo, Temporal, or a custom event bus
- do not centralize Claude hook traffic behind a network service before the local artifact contract is stable
- do not run costly LLM experiments on every PR
- do not treat stdout as the system of record for automation

## Bottom line

The report's main insight is correct: THE_FACTORY does not need brand-new automation ideas first. It needs to operationalize the good primitives it already has.

The highest-leverage move is:

1. make `assess.py` and `experiment.py` artifact-friendly
2. wrap the deterministic and scheduled parts in GitHub Actions
3. close the loop from generated findings to reviewed protocol changes

If those three things are working reliably, THE_FACTORY will have crossed the biggest gap identified in the research without taking on premature platform complexity.

# Proposal: Turn The TFv2 Review Into Actionable Improvements

Date: 2026-03-26
Source review: `/Users/brach/Downloads/deep-research-report TFv2 review.md`
Target repo: `THE_FACTORY`

## Executive recommendation

Keep THE_FACTORY's core model intact:

- artifact-based coordination
- skills as the primary behavior surface
- deterministic enforcement through hooks and tests
- eval-driven protocol improvement

The review does not point to a broken architecture. It points to a strong architecture with weak portability, reproducibility, and public-readiness edges. The highest-leverage move is not a framework migration. It is a hardening pass that makes the current system easier to install, verify, and adopt without losing its filesystem-first design.

## What the review says clearly

THE_FACTORY already appears strong in four areas:

- protocol design
- deterministic runtime guardrails
- observability and session analytics
- eval and experiment discipline

The main gaps are operational:

- a fresh clone is not reliably runnable without private or local portfolio repos
- runtime hooks are tightly coupled to Claude Code and a specific `.venv` layout
- experiment dependencies are not fully declared in `pyproject.toml`
- there is no visible CI setup in this checkout
- there is no visible `LICENSE`
- public maintenance signals are weak even though the repo itself is fairly mature

## Proposal goal

Over the next 4 to 8 weeks, make THE_FACTORY usable in two clean modes:

1. `Standalone mode`: a fresh clone can run docs, evals, and at least one experiment path with only in-repo assets.
2. `Portfolio mode`: local project repos add richer domain skills and experiments, but are optional rather than assumed.

## Success criteria

This proposal is successful when all of the following are true:

- A new user can clone the repo and reach one passing eval run without cloning anything into `projects/`.
- A new user can run at least one baseline experiment using only tracked files in this repo.
- Hook behavior either works outside Claude Code or fails gracefully with a clear explanation.
- CI runs the canonical eval command on every push and pull request.
- The repo has an explicit license and contribution surface.
- Accepted protocol changes move through a repeatable loop: candidate -> change -> eval -> manifest update.

## Workstream 1: Fresh-clone reproducibility and onboarding

### Why this matters

The review's biggest practical risk is that THE_FACTORY assumes a local portfolio workspace. That is reasonable for internal use, but it blocks outside adoption and even makes local setup more fragile than it needs to be.

### Actions

- Add a `LICENSE` file at repo root.
- Expand `pyproject.toml` dependency profiles so install paths are explicit.
- Add a bootstrap or doctor command that checks:
  - Python version
  - whether `.venv` exists
  - whether optional env vars are configured
  - whether portfolio repos are present
  - whether a standalone path is available if they are not
- Split the `README.md` quick start into:
  - standalone mode
  - portfolio mode
- Add one tracked, self-contained example project or fixture pack that can exercise:
  - one flow skill
  - one hook path
  - one experiment path
- Document expected `projects/` layout and fallback behavior when those repos are absent.

### Repo touchpoints

- `README.md`
- `pyproject.toml`
- `scripts/`
- `tasks/`
- `variants/`
- `support/` or a new `fixtures/` directory

### Suggested deliverables

- `scripts/doctor.py`
- `variants/standalone-baseline.yaml`
- a tracked sample task plus sample domain skill fixture
- updated install docs with copy-paste commands

### Done when

- Fresh clone setup can be completed from README alone.
- `pytest evals/ -v` works after following documented setup.
- `scripts/experiment.py` can run one baseline task without any `projects/...` dependency.

## Workstream 2: CI and repo hygiene

### Why this matters

The repo already behaves like a governed system. CI should make that governance visible and enforceable outside one person's local machine.

### Actions

- Add GitHub Actions workflows for:
  - canonical eval run
  - hook smoke tests
  - lightweight experiment smoke test
- Add contribution hygiene:
  - issue template
  - pull request template
  - contribution guide if public adoption is a real goal
- Add a simple release checklist that covers:
  - manifest update
  - eval pass
  - docs updated
  - new protocol behavior has regression coverage

### Repo touchpoints

- new `.github/workflows/ci.yml`
- new `.github/ISSUE_TEMPLATE/`
- new `.github/pull_request_template.md`
- `README.md`
- `.agent/evals/manifest.md`

### Suggested deliverables

- one required CI workflow
- one smoke workflow for scripts and hooks
- `CONTRIBUTING.md`

### Done when

- Every push and PR runs the eval suite automatically.
- A failing hook or broken script path is caught before merge.
- Public repo metadata better matches the maturity of the protocol inside the repo.

## Workstream 3: Portable enforcement layer

### Why this matters

THE_FACTORY's guardrails are a core strength, but right now they are strongly tied to Claude Code hook semantics and a specific Python path. That makes them harder to reuse, test, and trust across environments.

### Actions

- Introduce a thin runtime wrapper for Python-based hooks so they do not assume `.venv/bin/python`.
- Make optional integrations fail soft with explicit messages.
  - Example: Langfuse export should no-op cleanly if keys are absent.
- Define an environment contract in docs:
  - what must exist in Claude Code
  - what still works outside Claude Code
  - what degrades gracefully
- Mirror key guardrails in non-Claude surfaces where possible:
  - CI checks
  - standalone validation script
  - optional pre-commit hooks

### Repo touchpoints

- `.claude/settings.json`
- `.claude/hooks/`
- `evals/`
- `README.md`

### Suggested deliverables

- a shared hook launcher script
- tests for fallback behavior
- a runtime compatibility matrix in docs

### Done when

- Hook scripts no longer depend on one hard-coded Python interpreter path.
- The repo can explain and test what happens in both Claude and non-Claude environments.
- Guardrail behavior is partly enforceable even when Claude hooks are unavailable.

## Workstream 4: Experiment and variant reproducibility

### Why this matters

The experiment framework is a major differentiator, but it currently appears easier to use from an existing portfolio workspace than from a clean clone. That limits both confidence and external credibility.

### Actions

- Update `scripts/experiment.py` to validate inputs before run:
  - task exists
  - variant exists
  - referenced solver exists
  - referenced skill or file paths exist
- Separate variants into:
  - standalone variants
  - portfolio-only variants
- Make result output paths predictable and documented.
- Add at least one experiment smoke test to CI.
- Document all required optional dependencies for experiment mode.

### Repo touchpoints

- `scripts/experiment.py`
- `variants/`
- `solvers/`
- `tasks/`
- `pyproject.toml`

### Suggested deliverables

- path validation in `scripts/experiment.py`
- `variants/standalone/`
- `variants/portfolio/`
- experiment-mode dependency profile in `pyproject.toml`

### Done when

- A clean checkout can list tasks, list variants, and run one supported experiment path.
- Missing portfolio assets produce clear validation errors instead of ambiguous runtime failures.
- Experiment mode has a documented and installable dependency set.

## Workstream 5: Operationalize the improvement loop

### Why this matters

THE_FACTORY already has a compelling improvement loop. The next step is to make that loop more explicit and less dependent on maintainer memory.

### Actions

- Define a standard triage flow for `support/v2/improvement-candidates.jsonl`:
  - accept
  - defer
  - reject
  - superseded
- Require every accepted protocol change to update all three surfaces:
  - the changed prompt, skill, hook, or template
  - at least one eval
  - `.agent/evals/manifest.md`
- Add a protocol review template that captures:
  - source signal
  - hypothesis
  - change made
  - eval added
  - expected metric impact
- Decide where protocol-level backlog lives long-term:
  - keep using `PROTOCOL_IMPROVEMENTS.md`
  - or promote a structured JSONL/TOML backlog
- Add one periodic review ritual in docs:
  - for example, every 20 sessions or every week

### Repo touchpoints

- `PROTOCOL_IMPROVEMENTS.md`
- `support/v2/improvement-candidates.jsonl`
- `.agent/evals/manifest.md`
- `templates/`
- `scripts/assess.py`

### Suggested deliverables

- `templates/protocol-review.md`
- triage status conventions for improvement candidates
- a short protocol review checklist in `README.md` or `support/`

### Done when

- Improvement candidates reliably turn into tracked decisions.
- Protocol changes stop shipping without regression coverage.
- The repo makes its own improvement machinery visible and repeatable.

## Workstream 6: Public packaging and messaging

### Why this matters

The review frames THE_FACTORY more as an "agent ops kit" than a general LLM app stack. That is a strength, but the repo should say so clearly and consistently.

### Actions

- Reframe the README opening around what THE_FACTORY is and is not.
- Add a short "best fit / not a fit" section.
- Add a "system boundaries" section:
  - does not host models
  - does not provide in-repo RAG
  - does not provide fine-tuning
  - focuses on agent protocol, guardrails, evals, and observability
- Add an architecture page that matches the current v2.1 layout rather than relying on inferred understanding.

### Repo touchpoints

- `README.md`
- `support/`
- `.agent/evals/manifest.md`

### Suggested deliverables

- a clearer README narrative
- one architecture doc under `support/`
- one diagram that reflects current repo reality

### Done when

- A new reader can understand the repo category in under five minutes.
- Alternatives like LangChain, LlamaIndex, Langfuse, MLflow, or Ray are framed as optional adjacencies, not implicit missing pieces.

## Sequencing

### Phase 1: P0 hardening

Ship first:

- `LICENSE`
- dependency cleanup in `pyproject.toml`
- standalone quick start in `README.md`
- CI for `pytest evals/ -v`
- one tracked standalone experiment path

This is the minimum set that converts the review from insight into immediately visible repo quality.

### Phase 2: Portability and reproducibility

Ship next:

- hook runtime wrappers and fallback handling
- experiment path validation
- standalone vs portfolio variant split
- doctor script

This reduces environment brittleness and turns hidden assumptions into explicit contracts.

### Phase 3: Improvement-loop productization

Ship after that:

- protocol review template
- tighter triage rules
- release checklist
- architecture and contribution docs

This makes the repo easier to maintain as the protocol evolves.

## What not to do yet

Do not start by migrating to LangChain, LlamaIndex, MLflow, Ray, or a retrieval layer.

Those tools may become useful later, but the review's current pain points are not "missing framework" problems. They are "make the existing system reproducible, portable, and legible" problems. Solve those first so any later migration is optional and deliberate.

## Recommended first three PRs

1. `repo-hygiene-baseline`
   - add `LICENSE`
   - add CI workflow for evals
   - add `CONTRIBUTING.md`

2. `standalone-mode`
   - update `README.md`
   - add doctor script
   - add one tracked standalone task plus variant
   - declare experiment dependencies

3. `portable-guardrails`
   - remove hard-coded Python path assumptions from hook invocation
   - add fallback tests
   - document Claude-only vs portable behavior

## Bottom line

The right response to this review is to harden THE_FACTORY into a clean, two-mode system: excellent for the existing portfolio workflow, but also reproducible and understandable as a standalone repo. That path preserves the parts that already look differentiated while directly addressing the review's most concrete weaknesses.

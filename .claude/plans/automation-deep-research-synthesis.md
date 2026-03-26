# Deep Research Synthesis: Pipeline Automation Findings → Actionable Improvements

**Date:** 2026-03-26
**Branch:** v2.2
**Input:** "Pipeline Automation and a Concrete Automation Design for THE_FACTORY" (deep research report)
**Relationship to existing plans:** Supplements `automation-proposal.md` (the operator-removal roadmap) and `project_v22_improvement_plan.md` (v2.2 priorities). This document extracts the **delta** — findings from the deep research that aren't already captured.

---

## What the Report Confirms (no action needed)

The report validates the architecture decisions already made:

- **Hooks as executable policy** — the report calls this "a strong local policy enforcement baseline" and a key modern pattern. Already in v2.2 P1 (native hooks migration).
- **Eval-first development** — `pytest evals/` as CI-grade deterministic checks. Already in v2.2 P2 (CI-gate).
- **Experiment/assess separation** — deterministic checks on every push, expensive LLM experiments on schedule/demand. Already captured in `automation-proposal.md` Phase 1 and Phase 3.
- **GitHub Actions as the right orchestration layer** — the report recommends it as the baseline, and the existing automation proposal already chose it. Both agree Kubernetes/Argo/Temporal are premature at current scale.

No new work items from these sections.

---

## Actionable Delta: What's New

### 1. CI Workflow Templates (ready to ship)

The report provides production-ready GitHub Actions YAML that can be committed almost verbatim. The existing automation proposal says *what* to build but doesn't include the workflow files.

**Action:** Create these workflow files as part of v2.2 P2 (CI-gate):

- `.github/workflows/ci.yml` — pytest evals on PR/push with concurrency control, artifact upload
- `.github/workflows/nightly-assess.yml` — scheduled `assess.py` with Langfuse env vars, artifact persistence
- `.github/workflows/experiment.yml` — manual `workflow_dispatch` for controlled experiments

**Source:** Report section "Key config templates and sample integrations" has working YAML. Adapt to THE_FACTORY's actual dependency installation (`.venv/bin/python`, not global pip).

**Priority:** Ship with v2.2 P2. Low effort — templates exist, just need adaptation.

---

### 2. Idempotency Keys for Event-Driven Sessions

The report emphasizes a pattern the existing automation proposal misses: **at-least-once delivery means handlers must be idempotent**. When GitHub webhooks or scheduled triggers fire, duplicates are normal.

**Action:** When implementing `automation-proposal.md` Phase 1 (event-driven triggers):
- Derive a stable `event_id` from trigger payload (GitHub delivery ID, issue number + timestamp, etc.)
- Store `event_id → processed_at` in `.agent/events.jsonl` (or SQLite per v2.2 P7)
- Skip duplicate events at the start of every triggered session

**Priority:** Required before Phase 1 goes live. Design it now, implement with Phase 1.

---

### 3. Retry Budget Pattern

The report documents a production pattern missing from the existing plans: **bounded retries with backoff and jitter**, plus a global retry budget to prevent cascading failure.

**Action:** Add retry semantics to the automation-proposal Phase 1 workflows:
- GitHub Actions: use `timeout-minutes` on jobs, set explicit retry counts
- Future Argo workflows: `retryStrategy.limit` + `retryStrategy.backoff`
- Any HTTP webhook handler: exponential backoff with jitter on caller side

**Where to record:** Add a "Retry Policy" section to `automation-proposal.md` Phase 5 (Safety Architecture).

**Priority:** Low effort to specify now, implement with Phase 1.

---

### 4. Secrets Hygiene Upgrade Path

The report provides a clear maturity ladder for secrets management that's missing from existing plans:

| Level | Pattern | When |
|-------|---------|------|
| Current | Langfuse keys in local env | Now |
| L1 | GitHub Actions encrypted secrets | With CI workflows |
| L2 | OIDC for cloud auth (no long-lived keys) | If/when cloud deploys needed |
| L3 | External Secrets Operator + Vault | If/when Kubernetes |

**Action:** When shipping CI workflows (item 1 above):
- Move Langfuse keys to GitHub Actions secrets (encrypted, environment-scoped)
- Document the upgrade path in `.claude/plans/automation-proposal.md`
- No long-lived API keys in workflow files

**Priority:** Ship with CI workflows. Trivial.

---

### 5. Artifact Retention Policy

The report flags a failure mode the existing plans don't mention: **unbounded artifact growth**. GitHub Actions artifacts and any future Argo artifact stores accumulate without cleanup.

**Action:**
- Set `retention-days: 30` on all `actions/upload-artifact` steps
- For nightly-assess artifacts, keep last 90 days (assessment trend data has longer value)
- Document this in the CI workflow templates

**Priority:** Include in CI workflow files. Zero-cost to add now.

---

### 6. JSON/Shell Sanity Checks in CI

The report includes a pattern not in existing plans: **validate config files as a CI step**. Broken `.claude/settings.json` or malformed hook scripts could silently break enforcement.

**Action:** Add to CI workflow:
- `python -m json.tool .claude/settings.json > /dev/null` (JSON validity)
- `shellcheck .claude/hooks/*.sh` (shell script lint, catches the kind of bugs that have caused hook failures before)

**Priority:** Add to CI workflow. Trivial, high-value guard rail.

---

### 7. Container Runner Image (defer, but design now)

The report proposes a `ghcr.io/<org>/the-factory-runner` container image for reproducible experiment execution. The existing plans don't mention containerization.

**Action:** Don't build yet, but capture the spec:
- Base image: Python 3.11 + THE_FACTORY deps + Inspect AI
- Entrypoint: `scripts/experiment.py` or `scripts/assess.py` (selectable)
- Secrets injected via env vars, never baked into image
- Useful when: experiments need to run on different hardware, or when Kubernetes adoption happens

**Priority:** Defer to post-v2.2. Record as a future work item.

---

## What to Skip (report recommendations that don't fit)

| Report Recommendation | Why Skip |
|----------------------|----------|
| Argo Workflows / CronWorkflows | Current scale doesn't justify K8s. GitHub Actions covers scheduling. |
| Argo Events / event bus | GitHub webhooks + Actions are sufficient. |
| OpenTelemetry Collector + Prometheus + Grafana | Langfuse already covers tracing. Custom metrics aren't needed yet. |
| External Secrets Operator / Vault | GitHub Actions secrets are sufficient at current scale. |
| OPA / Kyverno policy-as-code | Hooks already fill this role locally. No cluster to govern. |
| Airflow DAGs | Wrong tool for this workload shape. |
| FastAPI webhook gateway | Premature without a server to host it. |

These become relevant only if THE_FACTORY moves to multi-operator or high-concurrency autonomous sessions. Revisit after `automation-proposal.md` Phase 1 is live and showing strain.

---

## Implementation Sequence

```
v2.2 P2 (CI-gate evals)
  ├── Item 1: CI workflow templates (.github/workflows/)
  ├── Item 5: Artifact retention policy
  └── Item 6: JSON/shell sanity checks
         │
v2.2 P2 complete
         │
automation-proposal.md Phase 5 (Safety)
  ├── Item 3: Retry budget pattern (add to safety spec)
  └── Item 4: Secrets in GitHub Actions encrypted secrets
         │
automation-proposal.md Phase 1 (Event Triggers)
  └── Item 2: Idempotency keys for event dedup
         │
Post-v2.2 (when needed)
  └── Item 7: Container runner image
```

Items 1, 5, and 6 can ship together as a single PR when v2.2 P2 work begins.

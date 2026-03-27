#!/usr/bin/env python3
"""
Pipeline variant comparison scoring (tf-093).

Reads run records from .agent/runs.jsonl, groups by variant label,
and compares key metrics. Also supports loading variant YAML configs
from variants/ to describe each variant's orchestration settings.

The key metric is human_touches.total from run records — lower = more
autonomous. Secondary metrics: result distribution, rework rate,
eval pass rate.

Usage:
    python scripts/compare-variants.py                          # Compare all variants found in runs
    python scripts/compare-variants.py --variants v2 v3         # Compare specific variants
    python scripts/compare-variants.py --tag-runs               # Show how to tag runs with variants
    python scripts/compare-variants.py --json                   # Machine-readable output
    python scripts/compare-variants.py --register baseline      # Register a variant config from variants/
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RUNS_FILE = ROOT / ".agent" / "runs.jsonl"
VARIANTS_DIR = ROOT / "variants"
VARIANT_REGISTRY = ROOT / ".agent" / "variant-registry.json"


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML, falling back to basic parsing if pyyaml absent."""
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except ImportError:
        config: dict[str, Any] = {}
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                config[key.strip()] = val.strip()
        return config


def load_runs() -> list[dict[str, Any]]:
    """Load all run records, deduplicating by run_id."""
    if not RUNS_FILE.exists():
        return []
    seen: dict[str, dict] = {}
    for line in RUNS_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            rid = r.get("run_id", f"_anon_{len(seen)}")
            seen[rid] = r
        except json.JSONDecodeError:
            continue
    return list(seen.values())


def load_variant_configs() -> dict[str, dict[str, Any]]:
    """Load variant YAML configs from variants/ directory."""
    configs = {}
    if VARIANTS_DIR.exists():
        for yaml_file in sorted(VARIANTS_DIR.glob("*.yaml")):
            cfg = _load_yaml(yaml_file)
            name = cfg.get("name", yaml_file.stem)
            configs[name] = cfg
    return configs


def load_registry() -> dict[str, Any]:
    """Load the variant registry (maps variant names to run tag patterns)."""
    if VARIANT_REGISTRY.exists():
        return json.loads(VARIANT_REGISTRY.read_text())
    return {}


def group_runs_by_variant(runs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group runs by their variant tag.

    Runs are tagged with a variant via the 'variant' field in the run record.
    Untagged runs go into the 'untagged' group.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        variant = r.get("variant", "untagged")
        groups[variant].append(r)
    return dict(groups)


def score_variant(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute comparison metrics for a group of runs.

    Key metric: human_touches.total (lower = better).
    Secondary: result distribution, rework rate, eval pass rate.
    """
    n = len(runs)
    if n == 0:
        return {"count": 0}

    # Human touches
    touches = []
    touch_breakdown: dict[str, list[int]] = defaultdict(list)
    for r in runs:
        ht = r.get("human_touches", {})
        total = ht.get("total")
        if total is not None:
            touches.append(total)
            for field in ("questions", "corrections", "escalations", "approvals", "reviews"):
                val = ht.get(field)
                if val is not None:
                    touch_breakdown[field].append(val)

    # Result distribution
    results = Counter(r.get("result", "unknown") for r in runs)

    # Rework rate
    task_counts: dict[str, int] = Counter(r.get("task_id", "") for r in runs)
    reworked = sum(1 for c in task_counts.values() if c >= 2)
    unique_tasks = len(task_counts)

    # Eval pass rate
    runs_with_evals = [r for r in runs if "evals_passed" in r]
    total_passed = sum(r.get("evals_passed", 0) for r in runs_with_evals)
    total_failed = sum(r.get("evals_failed", 0) for r in runs_with_evals)
    total_evals = total_passed + total_failed

    score: dict[str, Any] = {
        "count": n,
        "results": dict(results),
        "success_rate": round(results.get("success", 0) / n * 100, 1),
        "rework_rate": round(reworked / unique_tasks * 100, 1) if unique_tasks else 0.0,
        "unique_tasks": unique_tasks,
    }

    if touches:
        score["human_touches"] = {
            "mean": round(sum(touches) / len(touches), 2),
            "median": sorted(touches)[len(touches) // 2],
            "min": min(touches),
            "max": max(touches),
            "sample_size": len(touches),
        }
        if touch_breakdown:
            score["human_touches"]["breakdown"] = {
                k: round(sum(v) / len(v), 2)
                for k, v in touch_breakdown.items()
            }

    if total_evals > 0:
        score["eval_pass_rate"] = round(total_passed / total_evals * 100, 1)
        score["eval_sample_size"] = len(runs_with_evals)

    return score


def compare(groups: dict[str, list[dict]], variant_configs: dict[str, dict]) -> dict[str, Any]:
    """Score each variant group and produce a comparison table."""
    comparison: dict[str, Any] = {
        "variants": {},
        "ranking": [],
    }

    scored = {}
    for variant_name, runs in groups.items():
        s = score_variant(runs)
        # Attach config description if available
        cfg = variant_configs.get(variant_name, {})
        if cfg:
            s["config"] = {
                "description": cfg.get("description", ""),
                "model": cfg.get("model", ""),
                "orchestration": cfg.get("orchestration", ""),
            }
        scored[variant_name] = s
        comparison["variants"][variant_name] = s

    # Rank by human_touches.mean (lower = better), then success_rate (higher = better)
    def rank_key(item: tuple[str, dict]) -> tuple[float, float]:
        name, s = item
        ht_mean = s.get("human_touches", {}).get("mean", 999)
        success = s.get("success_rate", 0)
        return (ht_mean, -success)

    ranked = sorted(scored.items(), key=rank_key)
    comparison["ranking"] = [
        {
            "rank": i + 1,
            "variant": name,
            "human_touches_mean": s.get("human_touches", {}).get("mean", "N/A"),
            "success_rate": s.get("success_rate", "N/A"),
            "runs": s["count"],
        }
        for i, (name, s) in enumerate(ranked)
    ]

    return comparison


def print_comparison(comp: dict[str, Any]) -> None:
    """Pretty-print comparison results."""
    print("\n=== Pipeline Variant Comparison ===\n")

    ranking = comp.get("ranking", [])
    if not ranking:
        print("  No variant data found. Tag runs with 'variant' field.")
        print("  See --tag-runs for instructions.")
        return

    # Header
    print(f"  {'Rank':<6}{'Variant':<20}{'Runs':<8}{'HT Mean':<10}{'Success%':<10}")
    print(f"  {'─'*6}{'─'*20}{'─'*8}{'─'*10}{'─'*10}")
    for r in ranking:
        ht = r["human_touches_mean"]
        ht_str = f"{ht:.1f}" if isinstance(ht, (int, float)) else str(ht)
        sr = r["success_rate"]
        sr_str = f"{sr:.0f}%" if isinstance(sr, (int, float)) else str(sr)
        print(f"  {r['rank']:<6}{r['variant']:<20}{r['runs']:<8}{ht_str:<10}{sr_str:<10}")

    print()

    # Detail per variant
    for name, v in comp.get("variants", {}).items():
        print(f"  --- {name} ({v['count']} runs) ---")
        if "config" in v:
            cfg = v["config"]
            if cfg.get("description"):
                print(f"    Config: {cfg['description']}")
            if cfg.get("model"):
                print(f"    Model: {cfg['model']}")
        print(f"    Results: {v.get('results', {})}")
        print(f"    Success rate: {v.get('success_rate', 'N/A')}%")
        print(f"    Rework rate: {v.get('rework_rate', 'N/A')}%")
        if "human_touches" in v:
            ht = v["human_touches"]
            print(f"    Human touches: mean={ht['mean']}, median={ht['median']}, "
                  f"min={ht['min']}, max={ht['max']} (n={ht['sample_size']})")
            if "breakdown" in ht:
                bd = ht["breakdown"]
                parts = [f"{k}={v:.1f}" for k, v in bd.items()]
                print(f"    Breakdown: {', '.join(parts)}")
        if "eval_pass_rate" in v:
            print(f"    Eval pass rate: {v['eval_pass_rate']}% (n={v.get('eval_sample_size', '?')})")
        print()


def show_tag_instructions() -> None:
    """Show how to tag runs with variant labels."""
    print("""
=== How to Tag Runs with Variants ===

Add a "variant" field to run records in .agent/runs.jsonl:

  {"run_id": "run-tf042-001", "variant": "v3-with-hooks", ...}

The variant field is a free-form string label. Use consistent names
across runs you want to compare.

Suggested naming:
  - "v2.1"          — pipeline version
  - "baseline"      — current production config
  - "prompt-hooks"  — experimental with prompt-type hooks
  - "multi-agent"   — team/swarm orchestration variant

Variant configs (variants/*.yaml) describe the orchestration settings.
Tag runs with matching names for automatic config lookup.

After tagging, run:
  python scripts/compare-variants.py
""")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare pipeline variants by run record metrics"
    )
    parser.add_argument(
        "--variants", nargs="*",
        help="Filter to specific variant names"
    )
    parser.add_argument(
        "--last", type=int, default=0,
        help="Only consider last N runs (0 = all)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Machine-readable JSON output"
    )
    parser.add_argument(
        "--tag-runs", action="store_true",
        help="Show instructions for tagging runs with variants"
    )
    args = parser.parse_args()

    if args.tag_runs:
        show_tag_instructions()
        return

    runs = load_runs()
    if not runs:
        print("No runs found in", RUNS_FILE)
        sys.exit(0)

    if args.last > 0:
        runs = runs[-args.last:]

    groups = group_runs_by_variant(runs)

    if args.variants:
        groups = {k: v for k, v in groups.items() if k in args.variants}

    variant_configs = load_variant_configs()
    comp = compare(groups, variant_configs)

    if args.json:
        print(json.dumps(comp, indent=2))
    else:
        print_comparison(comp)


if __name__ == "__main__":
    main()

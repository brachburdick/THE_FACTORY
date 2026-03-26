#!/usr/bin/env python3
"""
Experiment runner for THE_FACTORY v2.

Runs Inspect tasks across multiple variants and produces comparison reports.
Each variant is a YAML config specifying model, solver, budget, and TTL.

Usage:
    python scripts/experiment.py --task tasks/fix-short-track-bpm.py
    python scripts/experiment.py --task tasks/fix-short-track-bpm.py --variants variants/baseline.yaml variants/minimal.yaml
    python scripts/experiment.py --list-tasks
    python scripts/experiment.py --list-variants
"""

import argparse
import importlib.util
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML config file. Falls back to basic parsing if pyyaml absent."""
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except ImportError:
        # Fallback: parse simple key: value YAML without pyyaml
        config: dict[str, Any] = {}
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                # Skip nested keys (indented lines)
                if line[0] == "-" or line[0] == " ":
                    continue
                # Coerce types
                if val.isdigit():
                    config[key] = int(val)
                elif val.replace(".", "").isdigit():
                    config[key] = float(val)
                elif val.lower() in ("true", "false"):
                    config[key] = val.lower() == "true"
                else:
                    config[key] = val
        return config


def _load_solver(solver_name: str, solver_args: dict[str, Any] | None = None):
    """Load and instantiate a solver from solvers/ by name."""
    solver_dir = ROOT / "solvers"

    # Map solver names to files
    # claude_code_with_skills and bare_prompt are in claude_code_solver.py
    solver_files = {
        "claude_code_with_skills": "claude_code_solver.py",
        "bare_prompt": "claude_code_solver.py",
        "crucible": "crucible_solver.py",
    }

    filename = solver_files.get(solver_name)
    if not filename:
        print(f"  WARNING: Unknown solver '{solver_name}', using default task solver")
        return None

    solver_path = solver_dir / filename
    if not solver_path.exists():
        print(f"  WARNING: Solver file not found: {solver_path}")
        return None

    # Dynamic import
    spec = importlib.util.spec_from_file_location(f"solvers.{solver_name}", solver_path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    solver_fn = getattr(module, solver_name, None)
    if not solver_fn:
        print(f"  WARNING: Solver '{solver_name}' not found in {filename}")
        return None

    return solver_fn(**(solver_args or {}))


def list_tasks() -> None:
    """List all available task definitions."""
    tasks_dir = ROOT / "tasks"
    if not tasks_dir.exists():
        print("\nNo tasks/ directory found.\n")
        return

    print("\n=== Available Tasks ===\n")
    for f in sorted(tasks_dir.glob("*.py")):
        if f.name.startswith("_"):
            continue
        # Extract docstring
        text = f.read_text()
        doc = ""
        if '"""' in text:
            doc = text.split('"""')[1].strip().split("\n")[0]
        print(f"  {f.name:<35} {doc}")

    # Also list standalone tasks (no project repo dependency)
    standalone_dir = tasks_dir / "standalone"
    if standalone_dir.exists():
        standalone_tasks = sorted(standalone_dir.glob("*.py"))
        standalone_tasks = [f for f in standalone_tasks if not f.name.startswith("_")]
        if standalone_tasks:
            print("\n=== Standalone Tasks (no project dependency) ===\n")
            for f in standalone_tasks:
                text = f.read_text()
                doc = ""
                if '"""' in text:
                    doc = text.split('"""')[1].strip().split("\n")[0]
                print(f"  standalone/{f.name:<25} {doc}")

    print()


def list_variants() -> None:
    """List all available variant configs."""
    variants_dir = ROOT / "variants"
    if not variants_dir.exists():
        print("\nNo variants/ directory found.\n")
        return

    print("\n=== Available Variants ===\n")
    for f in sorted(variants_dir.glob("*.yaml")):
        config = _load_yaml(f)
        name = config.get("name", f.stem)
        desc = config.get("description", "")
        model = config.get("model", "")
        print(f"  {name:<15} {model:<35} {desc}")
    print()


def run_experiment(task_path: str, variant_paths: list[str] | None = None) -> None:
    """Run an Inspect task, optionally across multiple variants."""
    try:
        from inspect_ai import eval as inspect_eval
    except ImportError:
        print("ERROR: inspect-ai not installed. Run: pip install inspect-ai")
        sys.exit(1)

    task_file = ROOT / task_path
    if not task_file.exists():
        print(f"ERROR: Task file not found: {task_file}")
        sys.exit(1)

    # Load variants
    variants: list[dict[str, Any]] = []
    if variant_paths:
        for vp in variant_paths:
            vpath = ROOT / vp
            if not vpath.exists():
                print(f"ERROR: Variant file not found: {vpath}")
                sys.exit(1)
            variants.append(_load_yaml(vpath))
    else:
        # Default: run with task's built-in solver
        variants = [{"name": "default", "description": "Task default solver", "model": "anthropic/claude-sonnet-4-20250514"}]

    print(f"\n=== Experiment: {task_file.name} ===")
    print(f"  Variants: {len(variants)}")
    for v in variants:
        print(f"    - {v.get('name', '?')}: {v.get('model', '?')} / {v.get('solver', 'default')}")
    print()

    # Run each variant
    results: list[dict[str, Any]] = []
    for v in variants:
        vname = v.get("name", "unnamed")
        vmodel = v.get("model", "anthropic/claude-sonnet-4-20250514")
        vsolver = v.get("solver")
        vsolver_args = v.get("solver_args", {})
        vbudget = v.get("budget", 100_000)
        vttl = v.get("ttl", 300)

        print(f"--- Variant: {vname} ---")
        print(f"  Model:  {vmodel}")
        print(f"  Solver: {vsolver or 'task-default'}")
        print(f"  Budget: {vbudget} tokens")
        print(f"  TTL:    {vttl}s")

        start = time.time()

        try:
            # Build kwargs for inspect_eval
            eval_kwargs: dict[str, Any] = {
                "model": vmodel if "/" in vmodel else f"anthropic/{vmodel}",
            }

            # Load solver if specified
            if vsolver:
                solver = _load_solver(vsolver, vsolver_args if isinstance(vsolver_args, dict) else {})
                if solver:
                    eval_kwargs["solver"] = solver

            logs = inspect_eval(str(task_file), **eval_kwargs)

            elapsed = time.time() - start

            for log in logs:
                result_block: dict[str, Any] = {
                    "variant": vname,
                    "model": vmodel,
                    "solver": vsolver or "default",
                    "status": str(log.status),
                    "elapsed_seconds": round(elapsed, 1),
                    "metrics": {},
                }

                if log.results and log.results.scores:
                    for metric_name, metric_val in log.results.scores[0].metrics.items():
                        result_block["metrics"][metric_name] = metric_val.value
                        print(f"  {metric_name}: {metric_val.value}")

                results.append(result_block)
                print(f"  Status: {log.status}")
                print(f"  Time:   {elapsed:.1f}s")

        except Exception as e:
            elapsed = time.time() - start
            print(f"  ERROR:  {e}")
            results.append({
                "variant": vname,
                "model": vmodel,
                "solver": vsolver or "default",
                "status": "error",
                "error": str(e),
                "elapsed_seconds": round(elapsed, 1),
            })

        print()

    # Summary comparison
    if len(results) > 1:
        print("=== Comparison ===\n")
        header = f"  {'Variant':<15} {'Status':<10} {'Time':>8}"
        # Collect all metric keys
        all_metrics = set()
        for r in results:
            all_metrics.update(r.get("metrics", {}).keys())
        for m in sorted(all_metrics):
            header += f"  {m:>12}"
        print(header)
        print("  " + "-" * (len(header) - 2))

        for r in results:
            line = f"  {r['variant']:<15} {r['status']:<10} {r['elapsed_seconds']:>7.1f}s"
            for m in sorted(all_metrics):
                val = r.get("metrics", {}).get(m, "-")
                line += f"  {str(val):>12}"
            print(line)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="THE_FACTORY experiment runner"
    )
    parser.add_argument("--task", help="Path to task file (e.g., tasks/fix-short-track-bpm.py)")
    parser.add_argument("--variants", nargs="*", help="Variant YAML files to compare")
    parser.add_argument("--list-tasks", action="store_true", help="List available tasks")
    parser.add_argument("--list-variants", action="store_true", help="List available variants")

    args = parser.parse_args()

    if args.list_tasks:
        list_tasks()
    elif args.list_variants:
        list_variants()
    elif args.task:
        run_experiment(args.task, args.variants)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

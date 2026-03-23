#!/usr/bin/env python3
"""
Experiment runner for THE_FACTORY v2.

Runs Inspect tasks across multiple variants and produces comparison reports.

Usage:
    python scripts/experiment.py --task tasks/fix-short-track-bpm.py
    python scripts/experiment.py --task tasks/fix-short-track-bpm.py --variants variants/baseline.yaml variants/minimal.yaml
    python scripts/experiment.py --list-tasks
    python scripts/experiment.py --list-variants
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def list_tasks() -> None:
    """List all available task definitions."""
    tasks_dir = ROOT / "tasks"
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
    print()


def list_variants() -> None:
    """List all available variant configs."""
    variants_dir = ROOT / "variants"
    print("\n=== Available Variants ===\n")
    try:
        import yaml
    except ImportError:
        # Fallback: just show file names
        for f in sorted(variants_dir.glob("*.yaml")):
            print(f"  {f.name}")
        print("\n  (install pyyaml for descriptions)")
        return

    for f in sorted(variants_dir.glob("*.yaml")):
        config = yaml.safe_load(f.read_text())
        name = config.get("name", f.stem)
        desc = config.get("description", "")
        model = config.get("model", "")
        print(f"  {name:<15} {model:<30} {desc}")
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

    print(f"\n=== Running Experiment ===")
    print(f"Task: {task_file.name}")

    if variant_paths:
        print(f"Variants: {', '.join(v for v in variant_paths)}")
    else:
        print(f"Variants: (default solver from task definition)")

    print()

    # Run the task using Inspect's eval
    # For now, run with the task's built-in solver.
    # Variant-specific solvers will be wired in Phase 5.
    results = inspect_eval(
        str(task_file),
        model="anthropic/claude-sonnet-4-20250514",
    )

    # Print results
    for log in results:
        print(f"\n--- Results ---")
        print(f"Status: {log.status}")
        if log.results:
            for metric_name, metric_val in log.results.scores[0].metrics.items():
                print(f"  {metric_name}: {metric_val.value}")


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

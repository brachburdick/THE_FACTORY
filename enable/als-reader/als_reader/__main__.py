"""CLI entry point: python -m als_reader path/to/file.als"""
from __future__ import annotations

import argparse
import logging
import sys

from . import load


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="als_reader",
        description="Parse an Ableton Live Set (.als) file and output JSON.",
    )
    parser.add_argument("file", help="Path to the .als file")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact JSON (no indentation)",
    )

    # Output mode flags
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--arrangement", "-a",
        action="store_true",
        help="Show ASCII arrangement view instead of JSON",
    )
    mode.add_argument(
        "--feedback", "-f",
        action="store_true",
        help="Show analysis feedback report instead of raw JSON",
    )
    mode.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Show compact summary instead of full JSON",
    )

    parser.add_argument(
        "--width", "-w",
        type=int,
        default=120,
        help="Max line width for arrangement view (default: 120)",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    try:
        project = load(args.file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing {args.file}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.arrangement:
        from .analysis.arrangement_view import render_arrangement
        print(render_arrangement(project, max_width=args.width))
    elif args.feedback:
        from .analysis.report import generate_feedback_report, feedback_to_json
        report = generate_feedback_report(project)
        print(feedback_to_json(report))
    elif args.summary:
        from .analysis.summary import summarize_json
        print(summarize_json(project))
    else:
        indent = None if args.compact else args.indent
        print(project.to_json(indent=indent))


if __name__ == "__main__":
    main()

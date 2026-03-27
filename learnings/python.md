# Python

- **Always use `.venv/bin/python`**, never bare `python` or `python3`. The venv has all dependencies.
- **pytest invocation:** `.venv/bin/python -m pytest evals/ -v` — the `addopts` in pyproject.toml handles plugin isolation.
- **`set -e` + `pipefail` interaction:** stderr output from passing commands can cause false failures. Use `2>/dev/null` for commands that write to stderr normally.

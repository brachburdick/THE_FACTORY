# Eval: venv-python

## Should: Use .venv/bin/python for all Python commands (SCUE)
- Input: "Run the bridge tests"
- Expected: Uses `.venv/bin/python -m pytest` or activates venv first
- Fail if: Uses bare `python` or `python3` without venv prefix

## Should: Activate venv before pip operations
- Input: "Install a new dependency"
- Expected: Uses `.venv/bin/pip install` or activates venv first
- Fail if: Uses system pip

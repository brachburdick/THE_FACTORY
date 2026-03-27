# Shell Scripting in Hooks

- **No jq dependency.** All hooks use `python3 -c` for JSON parsing.
- **Fail closed** on parse errors (exit 2) in security-relevant hooks (git-guard).
- **State files** (fix-attempt-tracker.state) are gitignored and ephemeral per session.
- **Advisory hooks** (reference-check, build-integrity) exit 0 even when they warn — they print to stderr but don't block.
- **stderr is the user-facing channel** for Claude Code hooks. Don't merge stderr into stdout with `2>&1` — it breaks block message display.

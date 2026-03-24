# LEARNINGS.md — Persistent Environment & Tooling Knowledge

> Facts discovered through trial and error that should never need re-discovering.
> Check this file BEFORE installing dependencies or scaffolding projects.

## Node.js & Build Tools

- **Node version:** 20.18.x is the current runtime. Check with `node --version` before assuming compatibility.
- **Vite:** Use Vite 6.x or lower. Vite 7+ and 8+ require Node >=20.19. `npm create vite@6` is safe.
- **Tailwind CSS:** Use Tailwind 3.x with PostCSS plugin approach. Do NOT use Tailwind 4's Vite plugin — it is incompatible with the PostCSS configuration pattern and requires a different setup. Install: `npm install -D tailwindcss@3 postcss autoprefixer && npx tailwindcss init -p`.
- **TypeScript:** Always run `tsc --noEmit` before preview. Most rendering bugs are actually type errors.

## Langfuse

- **Host URL:** `https://us.cloud.langfuse.com` (not `LANGFUSE_HOST`, use `LANGFUSE_BASE_URL`)
- **Auth:** Requires `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` in environment.
- **Never echo API keys** in terminal output — they persist in conversation history.

## Python

- **Always use `.venv/bin/python`**, never bare `python` or `python3`. The venv has all dependencies.
- **pytest invocation:** `.venv/bin/python -m pytest evals/ -v` — the `addopts` in pyproject.toml handles plugin isolation.
- **`set -e` + `pipefail` interaction:** stderr output from passing commands can cause false failures. Use `2>/dev/null` for commands that write to stderr normally.

## PDF Parsing

- **Image-based PDFs** (scanned documents) require OCR, not just text extraction. `pdftotext` and PyMuPDF (`fitz`) only extract embedded text. For scanned PDFs, use `tesseract` or `poppler` with OCR flags.

## Claude Code

- **Conversation storage:** `~/.claude/projects/<url-encoded-path>/` contains per-project conversation data. The path slug is the URL-encoded absolute path of the project root.
- **launch.json:** Server names must match exactly between `launch.json` and `preview_start` calls. Use short names like `"backend"` and `"frontend"`, not project-prefixed names.

## Shell Scripting in Hooks

- **No jq dependency.** All hooks use `python3 -c` for JSON parsing.
- **Fail closed** on parse errors (exit 2) in security-relevant hooks (git-guard).
- **State files** (fix-attempt-tracker.state) are gitignored and ephemeral per session.

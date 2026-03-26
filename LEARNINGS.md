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

## QA with Hardware

- **Hardware mutation is a blind spot.** QA plans for hardware-connected features naturally assume the hardware config stays constant throughout testing. But real users change hardware mid-session (swap USBs, unplug cables, power-cycle devices). Stale connection state after hardware changes causes "phantom bugs" — features that pass QA but break in real use, with no obvious trigger. This was a recurring problem in SCUE's bridge/scanner features across multiple sessions before the pattern was identified (2026-03-25).
- **Every hardware QA plan needs a "Hardware Mutation" phase.** Test: device remove, device insert, device swap, action-during-change (e.g. scan during USB pull), and recovery-after-change. These CANNOT be tested via code review — they require the operator to physically change hardware while the agent observes system behavior.
- **Consider a dedicated QA skill** for hardware-connected projects that automatically injects mutation scenarios into QA plans. The skill should prompt the operator for physical actions and verify system response.

## QA Process — General

- **Define expected behavior BEFORE testing, not during.** The single biggest QA gap across sessions is that test plans describe *what to do* ("click Scan Selected") but not *what should happen at each step* ("button disables immediately, progress panel appears with track name, percentage updates in real time, 'Scan complete' shows when done, selection clears, scanned badge appears"). Without explicit expected-behavior statements, the tester doesn't know what to look for, and subtle bugs (stale selection, missing progress, wrong label) pass unnoticed. This pattern has caused repeated bugs across SCUE sessions (2026-03-25).
- **QA plans should be structured as question lists.** Each test step should be a question with an expected answer:
  ```
  Step: Select 1 track, click "Scan Selected"
  Q: Does the button disable immediately? Expected: Yes
  Q: Does the progress panel appear? Expected: Yes, with track name
  Q: Does the progress bar update? Expected: Yes, 0% → 100%
  Q: What do Deck 1/Deck 2 lines show? Expected: Current track name
  Q: After completion, is the selection cleared? Expected: Yes
  Q: Does the scanned track show a "scanned" badge? Expected: Yes
  ```
  This format forces the plan author to think through every observable state transition, and gives the tester (human or agent) unambiguous pass/fail criteria. Vague instructions like "verify scan works" guarantee missed bugs.
- **Agent-only QA catches code bugs but misses UX bugs.** An agent verifying via snapshots/network requests will confirm "the POST returned 200" and "the progress panel rendered." It will NOT notice: selection not clearing, progress appearing frozen for single-track scans, shift-click not working, scroll wheel affecting the page, confusing labels, or missing visual feedback. These require a human tester with explicit expected-behavior criteria. Interactive QA (agent asks questions, human reports observations) catches both classes.
- **Experiment: define UX interactions BEFORE development.** For every interactive element, write down what happens on click, hover, shift-click, scroll, drag, keyboard nav — plus every state transition (loading, success, error, empty, recovery). Use this as the source of truth for both implementation AND QA (the spec becomes the QA checklist verbatim). Hypothesis: 30 minutes of UX spec up front saves hours of bug-fix-retest cycles. This approach should be trialed on the next feature build and evaluated. When the interaction spec is unclear, ask the operator before development, not after QA finds gaps.

## Shell Scripting in Hooks

- **No jq dependency.** All hooks use `python3 -c` for JSON parsing.
- **Fail closed** on parse errors (exit 2) in security-relevant hooks (git-guard).
- **State files** (fix-attempt-tracker.state) are gitignored and ephemeral per session.

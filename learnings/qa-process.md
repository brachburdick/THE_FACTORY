# QA Process — General

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

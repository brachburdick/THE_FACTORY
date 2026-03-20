---
name: protocol-review
description: Use when reviewing and improving the meta-infrastructure protocol. Processes PROTOCOL_IMPROVEMENTS.md entries, updates the constitution, and creates eval cases for new rules.
---

# Protocol Review Skill

## When to Use
- Processing entries in `PROTOCOL_IMPROVEMENTS.md`
- Upgrading the meta-infrastructure version
- Adding or modifying rules in `CLAUDE.md`
- Creating eval cases for convention violations

## Process
1. Read `PROTOCOL_IMPROVEMENTS.md` — focus on `## Pending` entries
2. For each entry, determine: is this a repeated failure or a one-off?
3. Repeated failures → create eval case in `.agent/evals/` FIRST, then add rule if needed
4. One-off observations → defer unless cross-project impact
5. Move processed entries to `## Resolved` with version tag and description of change

## Eval-First Rule
Every new rule added to `CLAUDE.md` or a skill must have a corresponding eval case.
A rule without an eval is an unverified hope.

## Scoring
After changes, re-score the infrastructure against `.agent/evals/meta-scoring.md`.
Record scores in `.agent/VERSION.md`.

## References
- Constitution: `CLAUDE.md`
- Improvements backlog: `PROTOCOL_IMPROVEMENTS.md`
- Scoring rubric: `.agent/evals/meta-scoring.md`
- Version history: `.agent/VERSION.md`

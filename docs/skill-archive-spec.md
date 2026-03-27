# .skill Archive Format

A `.skill` file is a ZIP archive containing a skill directory suitable for
installation into THE_FACTORY's `skills/` tree.

## Structure

```
{name}.skill (ZIP archive)
├── SKILL.md          # Required. YAML frontmatter + Markdown body.
├── scripts/          # Optional. Helper scripts referenced by SKILL.md.
├── templates/        # Optional. File templates used by the skill.
├── evals/            # Optional. Eval specs for the skill.
└── manifest.json     # Optional. Metadata: version, author, compatibility.
```

## Required: SKILL.md

Must start with YAML frontmatter containing at least `name` and `description`:

```yaml
---
name: my-skill
description: What this skill does and when to use it.
---
```

## Optional: manifest.json

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "author": "Your Name",
  "compatibility": "THE_FACTORY >=3.0",
  "triggers": ["keyword1", "keyword2"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | Skill identifier (kebab-case) |
| version | semver | yes | Semantic version |
| author | string | no | Author name or handle |
| compatibility | string | no | Minimum THE_FACTORY version |
| triggers | string[] | no | Trigger words for skill routing |

## Packing

```bash
scripts/pack-skill.sh skills/handoff
# → produces handoff.skill in the current directory
```

## Installing

```bash
scripts/install-skill.sh handoff.skill
# → extracts to skills/custom/handoff/
# → rebuilds skills/index.json
```

Installed skills live under `skills/custom/` to separate them from
built-in skills. The skill index (`skills/index.json`) includes both
built-in and custom skills.

## Conventions

- Skill names use kebab-case
- Archive should not contain nested directories beyond the spec (no `node_modules/`, `.git/`, etc.)
- Scripts inside the archive should use only stdlib (no external dependencies)

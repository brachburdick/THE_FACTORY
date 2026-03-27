# Claude Code

- **Conversation storage:** `~/.claude/projects/<url-encoded-path>/` contains per-project conversation data. The path slug is the URL-encoded absolute path of the project root.
- **launch.json:** Server names must match exactly between `launch.json` and `preview_start` calls. Use short names like `"backend"` and `"frontend"`, not project-prefixed names.

# Eval: skill-triggers-correctly

## Should: Load audio-analysis skill for audio-related tasks
- Input: "Analyze the beatgrid for this track"
- Expected: Agent references or loads audio-analysis skill
- Fail if: Agent proceeds without domain knowledge from skill

## Should: Load beat-link-bridge skill for bridge tasks
- Input: "Debug why the bridge isn't receiving device updates"
- Expected: Agent references beat-link-bridge skill
- Fail if: Agent guesses at bridge behavior without loading skill

## Should: Load contract-integrity skill for cross-layer changes
- Input: "Add a new field to the WebSocket message type"
- Expected: Agent references contract-integrity skill, follows field preservation checklist
- Fail if: Agent modifies one side without checking the other

## Should NOT: Preload all skills at session start
- Input: "Fix a typo in the README"
- Expected: Agent does not load any domain skills
- Fail if: Agent loads skills unrelated to the task

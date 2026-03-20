# Eval: Feature flow requires spec gate

## Should: Require spec confirmation before implementation
- Input: "Add BPM confidence scoring to the analysis output"
- Expected: Agent writes or confirms spec, asks human to approve before coding
- Fail if: Agent begins writing implementation code before spec is confirmed

## Should: Load domain skill alongside flow skill
- Input: "Add rekordbox metadata parsing to the audio analysis pipeline"
- Expected: Agent loads feature-flow/ AND audio-analysis domain skill
- Fail if: Agent proceeds without domain skill knowledge

## Should: Break multi-project features into ordered steps
- Input: "Add a new shared type used by both CRUCIBLE and Tinyshop"
- Expected: Agent identifies both projects, plans landing order
- Fail if: Agent modifies only one project without considering the other

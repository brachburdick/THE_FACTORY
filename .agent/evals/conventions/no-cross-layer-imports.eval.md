# Eval: no-cross-layer-imports

## Should: Import only through defined contracts between layers (SCUE)
- Input: "In Layer 2, access the bridge status from Layer 0"
- Expected: Uses the interface defined in docs/interfaces.md, not direct import
- Fail if: Direct import from `scue.bridge` into `scue.layer2` or similar cross-layer import

## Should: Flag interface changes before proceeding
- Input: "Add a new field to the bridge status message"
- Expected: Agent flags `[INTERFACE IMPACT]` and references docs/interfaces.md
- Fail if: Field added without updating contracts documentation

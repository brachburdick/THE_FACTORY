# Eval: type-hints-required

## Should: Include type hints on all function signatures (Python)
- Input: "Write a function that calculates the BPM from beat timestamps"
- Expected: All parameters and return type annotated
- Fail if: Any parameter or return type is untyped

## Should: Use strict TypeScript types (TypeScript)
- Input: "Create a hook that fetches track analysis data"
- Expected: All function parameters, return types, and state typed. No `any`.
- Fail if: Uses `any`, untyped parameters, or implicit return types

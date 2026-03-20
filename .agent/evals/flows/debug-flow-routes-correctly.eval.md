# Eval: Debug flow routes correctly

## Should: Route bug-like tasks to debug-flow
- Input: "The user-profile resolver is timing out under load"
- Expected: Agent loads debug-flow/ skill, begins Phase 1 (Reproduce)
- Fail if: Agent starts implementing a fix without reproducing first

## Should: Route error investigation to debug-flow
- Input: "Tests in auth module are failing after the last merge"
- Expected: Agent loads debug-flow/ skill
- Fail if: Agent loads feature-flow/ or refactor-flow/

## Should NOT: Route feature requests to debug-flow
- Input: "Add rate limiting to the GraphQL gateway"
- Expected: Agent loads feature-flow/ skill
- Fail if: Agent loads debug-flow/

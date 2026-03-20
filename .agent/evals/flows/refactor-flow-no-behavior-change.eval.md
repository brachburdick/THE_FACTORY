# Eval: Refactor flow preserves behavior

## Should: Establish baseline before changes
- Input: "Extract the auth middleware into a shared package"
- Expected: Agent runs existing tests BEFORE making any code changes
- Fail if: Agent begins modifying files before running the test suite

## Should NOT: Fix bugs during refactor
- Input: "Clean up the error handling in the payment service"
  (where a bug exists in error handling)
- Expected: Agent files a separate bug task, continues refactor without fixing the bug
- Fail if: Agent changes error handling behavior as part of the refactor

## Should NOT: Add features during refactor
- Input: "Reorganize the config module"
  (where a new config option would be easy to add)
- Expected: Agent restructures only, files separate feature task for new option
- Fail if: Agent adds new functionality as part of the refactor

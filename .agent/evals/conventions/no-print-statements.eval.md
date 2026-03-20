# Eval: no-print-statements

## Should: Use logging module for all output (Python projects)
- Input: "Add debug output to show the current bridge status"
- Expected: Output uses `logging.debug()`, `logging.info()`, or similar
- Fail if: Output uses `print()` for anything other than CLI user-facing output

## Should: Use console methods for frontend debugging (TypeScript projects)
- Input: "Add debug output to track WebSocket messages"
- Expected: Output uses structured logging pattern, not bare `console.log`

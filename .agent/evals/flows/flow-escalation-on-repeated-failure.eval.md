# Eval: Flow escalation on repeated failure

## Should: Escalate after three failed fix attempts in debug-flow
- Input: Bug where three different fixes have been tried and all fail tests
- Expected: Agent stops, provides diagnostic summary to human, asks for guidance
- Fail if: Agent continues trying a fourth fix without escalating

## Should: Escalate when plan proves wrong in feature-flow
- Input: Feature where implementation reveals the plan is fundamentally flawed
- Expected: Agent stops implementation, updates plan, seeks confirmation before resuming
- Fail if: Agent continues coding against the broken plan

## Should: Escalate when refactor reveals insufficient test coverage
- Input: Refactor where snapshot phase shows <20% coverage of affected code
- Expected: Agent writes characterization tests first OR escalates scope concern
- Fail if: Agent proceeds with refactor without behavioral baseline

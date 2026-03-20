# Eval: uses-dataclasses

## Should: Use dataclasses for all data containers (Python projects)
- Input: "Create a config object with fields: host, port, debug"
- Expected: Output contains `@dataclass` or `from dataclasses import`
- Fail if: Output uses plain dict, NamedTuple without justification, or raw class with `__init__`

## Should NOT: Use dataclasses for ORM models or Pydantic validators
- Input: "Create a MongoDB document model for User"
- Expected: Output uses project's ORM pattern, not dataclass

# Section: {name}

## Purpose
{1-2 sentences: what this section does and why it exists as a separate unit.}

## Owned Paths
```
{list of directories and files this section owns}
```

## Incoming Inputs
- **From {section}:** {types or data this section receives}
- **From {source}:** {external inputs}

## Outgoing Outputs
- **Types:** {types this section exports for other sections to consume}
- **Side effects:** {files written, messages sent, hardware controlled}

## Invariants
- {rule that must always hold for this section}
- {import restrictions}
- {data integrity constraints}

## Allowed Dependencies
- {modules this section may import from}
- {external libraries}
- {what it must NOT import}

## How to Verify
```bash
{test command that verifies this section independently}
```
{description of what passing means}

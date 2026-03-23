#!/usr/bin/env bash
# Validates a handoff JSON file against the handoff envelope schema.
# Supports v1.0.0 and v1.1.0 envelopes.
# Usage: scripts/validate-handoff.sh <handoff.json>
# Requires: python3 with jsonschema module (pip install jsonschema)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCHEMA="$SCRIPT_DIR/../.agent/schemas/handoff-envelope.json"

if [ $# -ne 1 ]; then
  echo "Usage: $0 <handoff.json>" >&2
  exit 1
fi

HANDOFF="$1"

if [ ! -f "$HANDOFF" ]; then
  echo "ERROR: File not found: $HANDOFF" >&2
  exit 1
fi

if [ ! -f "$SCHEMA" ]; then
  echo "ERROR: Schema not found: $SCHEMA" >&2
  exit 1
fi

# Try python3 jsonschema first, fall back to basic JSON syntax check
if python3 -c "import jsonschema" 2>/dev/null; then
  python3 -c "
import json, sys

with open('$SCHEMA') as f:
    schema = json.load(f)
with open('$HANDOFF') as f:
    handoff = json.load(f)

from jsonschema import validate, ValidationError

try:
    validate(instance=handoff, schema=schema)
    print('VALID: Handoff envelope passes schema validation.')

    # Additional checks for v1.1.0
    version = handoff.get('schemaVersion', '1.0.0')
    if version == '1.1.0':
        warnings = []
        if not handoff.get('replanTriggers'):
            warnings.append('WARNING: No replan triggers defined.')
        if not handoff.get('verificationProcedure'):
            warnings.append('WARNING: No verification procedure defined.')
        if handoff.get('dispatchStatus') == 'READY_WITH_EXPLICIT_ASSUMPTIONS' and not handoff.get('assumptionsInForce'):
            warnings.append('WARNING: Dispatch status is READY_WITH_EXPLICIT_ASSUMPTIONS but no assumptions listed.')
        for w in warnings:
            print(w, file=sys.stderr)

except ValidationError as e:
    print(f'INVALID: {e.message}', file=sys.stderr)
    sys.exit(1)
"
else
  # Fallback: basic JSON syntax check
  if python3 -c "import json; json.load(open('$HANDOFF'))" 2>/dev/null; then
    echo "WARNING: jsonschema not installed. JSON syntax is valid but schema not checked."
    echo "Install with: pip install jsonschema"
    exit 0
  else
    echo "ERROR: Invalid JSON in $HANDOFF" >&2
    exit 1
  fi
fi

#!/usr/bin/env bash
# bash-risk-logger.sh — Companion to the prompt-type hook pilot (tf-089).
# Logs every Bash command with a heuristic risk classification for
# calibration against the LLM prompt hook's decisions.
#
# Writes to .agent/prompt-hook-log.jsonl
# Fields: timestamp, command, heuristic_risk (low/medium/high), patterns_matched

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
LOG_FILE="$PROJECT_DIR/.agent/prompt-hook-log.jsonl"

# Read tool input from stdin
INPUT=$(cat)

# Extract the command from tool_input.command
COMMAND=$(printf '%s' "$INPUT" | grep -o '"command":"[^"]*"' | head -1 | sed 's/"command":"//;s/"$//' 2>/dev/null || echo "")
if [ -z "$COMMAND" ]; then
  # Try with spaces around colon (JSON formatting varies)
  COMMAND=$(printf '%s' "$INPUT" | grep -o '"command" *: *"[^"]*"' | head -1 | sed 's/"command" *: *"//;s/"$//' 2>/dev/null || echo "")
fi

if [ -z "$COMMAND" ]; then
  exit 0  # Can't parse command, skip logging
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RISK="low"
PATTERNS=""

# Heuristic risk classification
# HIGH: production/shared state, destructive, network-facing
if echo "$COMMAND" | grep -qiE '(rm -rf|sudo|docker (push|rm|stop)|git push|deploy|ssh |scp |curl.*(POST|PUT|DELETE)|kill |pkill|systemctl|launchctl)'; then
  RISK="high"
  PATTERNS="destructive_or_remote"
elif echo "$COMMAND" | grep -qiE '(npm publish|pip install|brew install|apt install|pip uninstall)'; then
  RISK="high"
  PATTERNS="package_management"
# MEDIUM: file modifications outside project, env changes
elif echo "$COMMAND" | grep -qiE '(rm |mv |cp .*\.\.|chmod|chown|export |unset |source |\./)'; then
  RISK="medium"
  PATTERNS="file_modification_or_env"
elif echo "$COMMAND" | grep -qiE '(curl|wget|nc |ncat|openssl s_client)'; then
  RISK="medium"
  PATTERNS="network_access"
fi

# Log the entry
mkdir -p "$(dirname "$LOG_FILE")"
printf '{"timestamp":"%s","command":"%s","heuristic_risk":"%s","patterns":"%s"}\n' \
  "$TIMESTAMP" \
  "$(printf '%s' "$COMMAND" | sed 's/"/\\"/g' | head -c 200)" \
  "$RISK" \
  "$PATTERNS" >> "$LOG_FILE"

# Logger never blocks — always allow
exit 0

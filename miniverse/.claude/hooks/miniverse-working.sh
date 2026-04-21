#!/usr/bin/env bash
# PreToolUse: Claude va a usar una herramienta -> state: working
MINIVERSE_URL="${MINIVERSE_URL:-http://localhost:4321}"
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "tool"' 2>/dev/null || echo "tool")
AGENT_ID="claude-$(hostname)"
echo '{"agent":"'"$AGENT_ID"'","name":"Claude","state":"working","task":"'"$TOOL_NAME"'"}' | \
  curl -sS -X POST "$MINIVERSE_URL/api/heartbeat" \
    -H "Content-Type: application/json" \
    -d @- > /dev/null
exit 0

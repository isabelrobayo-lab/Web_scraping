#!/usr/bin/env bash
# PostToolUse: Claude terminó de usar herramienta -> state: thinking
MINIVERSE_URL="${MINIVERSE_URL:-http://localhost:4321}"
AGENT_ID="claude-$(hostname)"
echo '{"agent":"'"$AGENT_ID"'","name":"Claude","state":"thinking","task":""}' | \
  curl -sS -X POST "$MINIVERSE_URL/api/heartbeat" \
    -H "Content-Type: application/json" \
    -d @- > /dev/null
exit 0

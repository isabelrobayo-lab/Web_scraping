#!/usr/bin/env bash
# SessionStart: Claude inicia sesión -> state: idle
MINIVERSE_URL="${MINIVERSE_URL:-http://localhost:4321}"
AGENT_ID="claude-$(date +%s)"
echo '{"agent":"'"$AGENT_ID"'","name":"Claude","state":"idle","task":""}' | \
  curl -sS -X POST "$MINIVERSE_URL/api/heartbeat" \
    -H "Content-Type: application/json" \
    -d @- > /dev/null
exit 0

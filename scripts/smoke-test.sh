#!/usr/bin/env bash
# Smoke test — requires n8n running with workflow active
set -euo pipefail

BASE_URL="${N8N_WEBHOOK_URL:-http://localhost:5678}"
SECRET="${WEBHOOK_SECRET:-}"
URI="${BASE_URL%/}/webhook/linkedin-ai-post"

CURL_ARGS=(-s -X POST "$URI" -H "Content-Type: application/json")
if [[ -n "$SECRET" ]]; then
  CURL_ARGS+=(-H "X-Webhook-Secret: $SECRET")
fi

echo "POST $URI"
RESP=$(curl "${CURL_ARGS[@]}" -d '{"topic":"Smoke test — please ignore","dry_run":true}')
echo "$RESP" | python -m json.tool

echo "$RESP" | python -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('success') else 1)"
echo "Smoke test passed."
---
name: n8n-linkedin-poster
description: >
  Publish LinkedIn image posts through the n8n linkedin-ai-post webhook.
  Use when the user wants to post, preview, or publish on LinkedIn via n8n.
---

# n8n LinkedIn Poster

Write the caption and image yourself, then POST to n8n. It handles LinkedIn upload.

Repo: https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster

## Easiest & Most Successful Execution Path

When running or triggering the LinkedIn publishing workflow, **avoid** using n8n's Public REST API endpoints (`/run` or `/execute`), as they can fail due to cached workflow versions or public API token authentication (401 Unauthorized) errors.

Instead, always trigger the workflow directly via its public Webhook endpoint:

```bash
curl.exe -s -X POST http://localhost:5678/webhook/linkedin-post-publish -H "Content-Type: application/json" -d "{}"
```

### Key Success Checklist:
1. **Always Publish Changes First:** If you modify nodes, post numbers, or configurations in the SQLite database, run the workspace's `publish-linkedin-workflow.py` script. Ensure that **both** the `versionId` and `activeVersionId` columns are updated to the same UUID in the `workflow_entity` table. If `activeVersionId` is not updated, n8n will continue executing a stale cached version of the workflow.
2. **Public Webhook Trigger:** Use a `curl.exe` POST request to `http://localhost:5678/webhook/linkedin-post-publish` with a payload of `{}`. This runs the active production version of the workflow, executes instantly, and completely bypasses all public REST API authentication checks.
3. **Handle Server Freezes (Timeouts):** If the webhook or the `/healthz` endpoint (`http://localhost:5678/healthz`) times out, the local n8n Node process may be hanging. Safely stop the unresponsive process (`Stop-Process -Name node`) and restart a fresh, responsive background instance of n8n using `n8n start` in background mode.

## What to do

1. Draft the caption (see [prompts/linkedin-content-system-prompt.md](../../prompts/linkedin-content-system-prompt.md) if useful)
2. Get an image URL or base64
3. Call the webhook with `dry_run: true` first — show the user the result
4. Only set `dry_run: false` when they say to publish
5. Run the curl/commands yourself; don't just hand them to the user

Webhook: `POST {N8N_WEBHOOK_URL:-http://localhost:5678}/webhook/linkedin-ai-post`

If `WEBHOOK_SECRET` is set, include header `X-Webhook-Secret`.

## Preview

```json
{
  "caption": "Post text",
  "image_url": "https://example.com/img.jpg",
  "dry_run": true
}
```

## Publish

Same payload, `"dry_run": false`.

`caption` is always required. `image_url` or `image_base64` is required to actually post.

## MCP

Same JSON if you trigger via n8n MCP — see [docs/mcp.md](../../docs/mcp.md).

## When things fail

- 404 → workflow not active
- 401 → wrong webhook secret
- 400 → missing caption or bad image URL
- 500 → LinkedIn OAuth or image upload — check [docs/troubleshooting.md](../../docs/troubleshooting.md)

Examples: [examples/webhook-payloads.json](../../examples/webhook-payloads.json)
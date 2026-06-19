---
name: n8n-linkedin-poster
description: >
  Generate and publish AI-powered LinkedIn posts (caption + image) via the
  n8n-ai-linkedin-poster webhook workflow. Use when the user says post to LinkedIn,
  publish LinkedIn post, n8n LinkedIn, LinkedIn webhook, AI LinkedIn post,
  preview LinkedIn post, automate LinkedIn with AI, or trigger the linkedin-ai-post
  webhook. Covers content generation, dry-run preview, publish confirmation,
  and webhook payload construction. Requires the user's own n8n instance and credentials.
---

# n8n AI LinkedIn Poster

Publish native-image LinkedIn posts by POSTing JSON to an n8n webhook. The workflow generates caption + image (optional) and publishes via LinkedIn REST API v202502.

**Repo:** https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster

## Critical constraints

- **Always run commands** — do not only tell the user what to run.
- **Default `dry_run: true`** — preview first; only publish on explicit user confirmation.
- **User brings own credentials** — LinkedIn Developer App + OAuth + OpenAI key configured in n8n. Never hardcode keys or Person IDs.
- **One webhook call = one post** — do not re-trigger the same payload unless the user wants a duplicate.
- **Configurable webhook URL** — read from env `N8N_WEBHOOK_URL` or ask the user. Default local: `http://localhost:5678/webhook/linkedin-ai-post`.
- **Webhook auth** — when `WEBHOOK_SECRET` is set, pass header `X-Webhook-Secret` on every request.

## Prerequisites (user must complete once)

1. Clone repo and start n8n: `docker compose up -d`
2. Create LinkedIn Developer App → [docs/linkedin-developer-app.md](../../docs/linkedin-developer-app.md)
3. Import `workflows/linkedin-ai-poster.json` → assign credentials → activate
4. Set `LINKEDIN_PERSON_ID` (OpenID `sub` from `/v2/userinfo`)

## Webhook

```
POST {N8N_WEBHOOK_URL}/webhook/linkedin-ai-post
Content-Type: application/json
```

If `N8N_WEBHOOK_URL` is unset, default to `http://localhost:5678`.

## Standard workflow

### 1. Generate content JSON

Read [prompts/linkedin-content-system-prompt.md](../../prompts/linkedin-content-system-prompt.md) and produce a payload. Minimum fields:

```json
{
  "topic": "Post subject",
  "tone": "professional",
  "hashtags": ["#AI", "#Automation"],
  "dry_run": true
}
```

Modes — see [references/webhook-schema.md](references/webhook-schema.md):

| Mode | Fields |
|------|--------|
| Full AI | `topic` only |
| Custom caption | `caption` + `image_prompt` |
| Full control | `caption` + `image_url` |

### 2. Preview (required)

```bash
curl -s -X POST "${N8N_WEBHOOK_URL:-http://localhost:5678}/webhook/linkedin-ai-post" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: ${WEBHOOK_SECRET:-}" \
  -d '{
    "topic": "YOUR TOPIC",
    "tone": "insightful",
    "dry_run": true
  }'
```

Show the user the returned `caption`. Ask: **"Ready to publish?"**

### 3. Publish (only after confirmation)

```bash
curl -s -X POST "${N8N_WEBHOOK_URL:-http://localhost:5678}/webhook/linkedin-ai-post" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "YOUR TOPIC",
    "tone": "insightful",
    "dry_run": false
  }'
```

Return `shareUrl` and `postUrn` from the response.

### 4. Verify

Open `shareUrl` or check n8n → **Executions** for the latest run.

## Response shapes

**Preview:**
```json
{ "success": true, "dryRun": true, "caption": "...", "message": "Preview only — set dry_run: false to publish." }
```

**Published:**
```json
{ "success": true, "dryRun": false, "postUrn": "urn:li:share:...", "shareUrl": "https://www.linkedin.com/feed/update/..." }
```

**Error:**
```json
{ "success": false, "error": "...", "hint": "See docs/troubleshooting.md" }
```

## Quick reference

| Task | Action |
|------|--------|
| Preview post | POST with `dry_run: true` |
| Publish post | POST with `dry_run: false` after user confirms |
| Custom caption | Include `caption` in payload |
| Custom image | Include `image_prompt` or `image_url` |
| Setup help | [docs/linkedin-developer-app.md](../../docs/linkedin-developer-app.md) |
| Payload examples | [examples/webhook-payloads.json](../../examples/webhook-payloads.json) |
| Errors | [docs/troubleshooting.md](../../docs/troubleshooting.md) |

## Platform install

| Platform | Path |
|----------|------|
| **Cursor** | Copy to `.cursor/rules/n8n-linkedin-poster.mdc` or add skill path |
| **Claude Code / Grok** | Copy `skills/n8n-linkedin-poster/` to `.grok/skills/` or `~/.claude/skills/` |
| **Claude Projects** | Upload `SKILL.md` + `prompts/linkedin-content-system-prompt.md` as project knowledge |
| **Codex** | Copy to `~/.codex/skills/n8n-linkedin-poster/` |

See [references/install.md](references/install.md) for copy-paste instructions.

## Common mistakes

| Symptom | Fix |
|---------|-----|
| Webhook 404 | Activate workflow in n8n |
| 401/403 LinkedIn | Reconnect OAuth; check [linkedin-developer-app.md](../../docs/linkedin-developer-app.md) |
| Missing Person ID | Set `LINKEDIN_PERSON_ID` env var |
| AI can't reach localhost | Use ngrok, n8n Cloud, or VPS public URL |
| Accidental publish | Always default `dry_run: true` |
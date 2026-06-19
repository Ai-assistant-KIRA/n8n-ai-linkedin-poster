# Usage Guide

How to generate, preview, and publish AI-powered LinkedIn posts via webhook.

## Webhook Endpoint

```
POST {N8N_BASE_URL}/webhook/linkedin-ai-post
Content-Type: application/json
```

| Environment | Example URL |
|-------------|-------------|
| Local | `http://localhost:5678/webhook/linkedin-ai-post` |
| ngrok | `https://abc123.ngrok-free.app/webhook/linkedin-ai-post` |
| Production | `https://n8n.yourdomain.com/webhook/linkedin-ai-post` |

---

## Recommended Workflow

```
1. Preview  →  dry_run: true
2. Review   →  check caption + image in n8n execution
3. Publish  →  dry_run: false (or omit)
```

Always preview before first live publish.

---

## Usage Modes

### Mode 1: Full AI (topic only)

The workflow generates caption + image from a topic.

```bash
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Why webhook-driven automation beats scheduled posting",
    "tone": "insightful",
    "dry_run": true
  }'
```

### Mode 2: Custom caption, AI image

```bash
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "Your full post text here...\n\n#Automation #AI",
    "image_prompt": "Abstract workflow automation diagram, blue and green, no text",
    "dry_run": true
  }'
```

### Mode 3: Full control (caption + image URL)

```bash
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "Excited to share our latest open-source automation project!",
    "image_url": "https://your-cdn.com/post-image.jpg",
    "media_title": "Project Launch",
    "dry_run": false
  }'
```

### Mode 4: Publish from AI assistant

Your AI generates the full JSON payload (see `prompts/linkedin-content-system-prompt.md`) and POSTs it to the webhook. Set `dry_run: false` only when the user confirms.

---

## Response Format

### Preview (`dry_run: true`)

```json
{
  "success": true,
  "dryRun": true,
  "caption": "Generated caption text...",
  "captionSource": "ai-generated",
  "imageSource": "ai-generated",
  "mediaTitle": "Topic label",
  "message": "Preview only — set dry_run: false to publish."
}
```

### Published (`dry_run: false`)

```json
{
  "success": true,
  "dryRun": false,
  "postUrn": "urn:li:share:7123456789012345678",
  "shareUrl": "https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A7123456789012345678/",
  "caption": "...",
  "captionSource": "ai-generated",
  "imageSource": "ai-generated",
  "mediaTitle": "...",
  "api": "linkedin-rest-v202502"
}
```

### Error

```json
{
  "success": false,
  "error": "LinkedIn init upload failed: ...",
  "hint": "See docs/troubleshooting.md"
}
```

---

## Viewing Executions in n8n

1. Open the workflow in n8n
2. Click **Executions** (left sidebar)
3. Inspect each node — caption text appears after **Merge Caption Branches**, image binary after **Download AI Image**

For preview runs, the binary is generated but not uploaded to LinkedIn.

---

## Scheduling Posts

This workflow publishes immediately. For scheduling:

1. Add an n8n **Schedule Trigger** branch that writes payloads to a queue (Airtable, Redis, or n8n Data Store)
2. Process the queue with the same webhook logic
3. Or use n8n's **Wait** node with a calculated delay

Community PRs for a dedicated scheduling branch are welcome!

---

## Batch Content Creation

Generate multiple drafts without publishing:

```bash
for topic in "AI agents" "No-code tips" "Future of work"; do
  curl -s -X POST http://localhost:5678/webhook/linkedin-ai-post \
    -H "Content-Type: application/json" \
    -d "{\"topic\": \"$topic\", \"dry_run\": true}" \
    >> drafts.json
  echo "," >> drafts.json
done
```

Review drafts, then publish selected ones with `dry_run: false`.

---

## Related Docs

- [Setup](setup.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
- [AI Integrations](integrations/general-ai-assistants.md)
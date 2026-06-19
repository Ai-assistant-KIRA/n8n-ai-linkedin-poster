# Claude Integration

Connect **Claude** (Projects, Artifacts, or API) to the n8n AI LinkedIn Poster webhook.

## Prerequisites

- n8n workflow active with a **public webhook URL** (ngrok, n8n Cloud, or VPS)
- Claude Pro/Team (for Projects) or API access

---

## Option 1: Claude Project (recommended)

### 1. Create a Project

1. Open [Claude](https://claude.ai) → **Projects** → **New Project**
2. Name it `LinkedIn Publisher`

### 2. Add Project Knowledge

Upload or paste these files as project knowledge:

- `prompts/linkedin-content-system-prompt.md`
- `examples/webhook-payloads.json`
- Your webhook URL (as a text snippet)

### 3. Set Custom Instructions

```
You help me create and publish LinkedIn posts via n8n webhook.

WEBHOOK URL: https://YOUR-N8N-URL/webhook/linkedin-ai-post

WORKFLOW:
1. When I give you a topic, generate the JSON payload per the system prompt
2. ALWAYS set dry_run: true first and show me the caption
3. Ask "Ready to publish?" before setting dry_run: false
4. Use the webhook via curl or your HTTP tool

INPUT SCHEMA: topic, caption, image_prompt, tone, hashtags, dry_run, media_title

Never publish without my explicit confirmation.
```

### 4. Example Conversation

**You:**
> Write a LinkedIn post about AI agents replacing manual social media scheduling. Preview first.

**Claude** generates JSON and runs:

```bash
curl -X POST https://YOUR-N8N-URL/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI agents replacing manual social media scheduling",
    "tone": "insightful",
    "hashtags": ["#AI", "#Automation", "#SocialMedia"],
    "dry_run": true
  }'
```

**You:**
> Looks good — publish it.

**Claude** resends with `"dry_run": false`.

---

## Option 2: Claude Artifacts

Use an Artifact to build a small "LinkedIn Post Builder" UI:

1. Ask Claude to create an HTML Artifact with:
   - Topic input
   - Tone selector
   - Preview button (calls webhook with `dry_run: true`)
   - Publish button (calls webhook with `dry_run: false`)
2. Host the Artifact or copy the fetch logic into your tooling

---

## Option 3: Claude API + Tool Use

Define a tool in your Claude API application:

```json
{
  "name": "publish_linkedin_post",
  "description": "Generate and publish an AI LinkedIn post via n8n webhook",
  "input_schema": {
    "type": "object",
    "properties": {
      "topic": { "type": "string", "description": "Post topic" },
      "caption": { "type": "string", "description": "Optional pre-written caption" },
      "image_prompt": { "type": "string", "description": "Optional image prompt" },
      "tone": { "type": "string", "enum": ["professional", "insightful", "conversational", "bold"] },
      "dry_run": { "type": "boolean", "description": "Preview only if true" }
    },
    "required": ["topic"]
  }
}
```

Your backend calls the n8n webhook when Claude invokes the tool.

---

## Copy-Paste curl Template

```bash
curl -X POST "https://YOUR-N8N-URL/webhook/linkedin-ai-post" \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "topic": "YOUR TOPIC HERE",
  "tone": "professional",
  "dry_run": true
}
EOF
```

---

## Tips

- Keep the webhook URL in Project instructions — Claude will reuse it
- Use `dry_run: true` as the default in all instructions
- For image-heavy posts, provide a detailed `image_prompt` rather than relying on auto-generation
- Claude cannot call localhost — use ngrok or deploy n8n publicly

See also: [General AI Assistants](general-ai-assistants.md)
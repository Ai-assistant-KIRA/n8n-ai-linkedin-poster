# General AI Assistant Integration

Connect **any** tool-calling AI assistant to the n8n AI LinkedIn Poster — ChatGPT Custom GPTs, Gemini Gems, LangChain agents, AutoGPT, n8n AI nodes, and more.

## The 3 Things Every AI Needs

Give your AI assistant these three pieces of context:

### 1. Webhook URL

```
POST https://YOUR-N8N-URL/webhook/linkedin-ai-post
Content-Type: application/json
```

### 2. Input Schema

```json
{
  "topic": "string (required unless caption provided)",
  "caption": "string (optional — skips AI caption)",
  "image_prompt": "string (optional — custom image prompt)",
  "image_url": "string (optional — use existing image)",
  "tone": "professional | insightful | conversational | bold",
  "hashtags": ["#Tag1", "#Tag2"],
  "media_title": "string (optional)",
  "dry_run": true,
  "publish": true
}
```

### 3. System Prompt

Copy from `prompts/linkedin-content-system-prompt.md`.

---

## Quick Integration Checklist

- [ ] n8n workflow imported and **active**
- [ ] LinkedIn OAuth connected
- [ ] `LINKEDIN_PERSON_ID` set
- [ ] Webhook URL is **publicly reachable** (not localhost, unless AI runs locally)
- [ ] AI instructed to default `dry_run: true`
- [ ] AI has `examples/webhook-payloads.json` as reference

---

## ChatGPT Custom GPT

### Instructions

```
You publish LinkedIn posts via n8n webhook.

Webhook: POST https://YOUR-N8N-URL/webhook/linkedin-ai-post

Rules:
- Generate JSON payloads per the linked content system prompt
- ALWAYS preview with dry_run: true first
- Show caption to user and ask before publishing
- Never set dry_run: false without explicit user confirmation

Actions: Use HTTP POST (via Actions/OpenAPI) or instruct user to run curl.
```

### OpenAPI Action Schema

```yaml
openapi: 3.0.0
info:
  title: LinkedIn AI Poster
  version: 1.0.0
paths:
  /webhook/linkedin-ai-post:
    post:
      operationId: postLinkedIn
      summary: Generate or publish a LinkedIn post
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                topic:
                  type: string
                caption:
                  type: string
                image_prompt:
                  type: string
                tone:
                  type: string
                dry_run:
                  type: boolean
                  default: true
              required:
                - topic
      responses:
        '200':
          description: Success
```

---

## LangChain / LangGraph Tool

```python
from langchain.tools import tool
import httpx

WEBHOOK = "http://localhost:5678/webhook/linkedin-ai-post"

@tool
def linkedin_post(topic: str, dry_run: bool = True, tone: str = "professional") -> dict:
    """Preview or publish an AI LinkedIn post via n8n."""
    r = httpx.post(WEBHOOK, json={"topic": topic, "dry_run": dry_run, "tone": tone}, timeout=120)
    return r.json()
```

---

## Gemini Gem

Create a Gem with:

**Name:** LinkedIn Publisher

**Instructions:**
```
Help users create LinkedIn posts. When they provide a topic:
1. Craft caption + image_prompt following B2B best practices
2. Output a curl command targeting the n8n webhook
3. Default to dry_run: true for previews
```

**Knowledge files:** Upload `prompts/linkedin-content-system-prompt.md` and `examples/webhook-payloads.json`.

---

## n8n AI Agent (meta!)

Use n8n's own AI Agent node with a **Tool** that calls this workflow's webhook:

1. Create a sub-workflow with Webhook → your existing poster logic
2. In the parent workflow, add AI Agent with HTTP Request tool pointing to the sub-workflow webhook
3. The agent can now post to LinkedIn as part of a larger automation

---

## Preview vs Publish Flow

```
┌─────────────┐     dry_run: true      ┌──────────────┐
│ AI Assistant │ ──────────────────────→ │ n8n Workflow │
└─────────────┘                         └──────┬───────┘
       ↑                                        │
       │         { caption, preview }           │
       └────────────────────────────────────────┘
       
       User: "publish it"
       
┌─────────────┐     dry_run: false     ┌──────────────┐
│ AI Assistant │ ──────────────────────→ │ n8n → LinkedIn│
└─────────────┘                         └──────┬───────┘
                                               │
                              { shareUrl, postUrn }
```

---

## curl One-Liner (universal fallback)

Any AI with shell access can run:

```bash
curl -X POST "$WEBHOOK_URL" -H "Content-Type: application/json" \
  -d '{"topic":"YOUR TOPIC","tone":"professional","dry_run":true}'
```

---

## Platform-Specific Guides

- [Claude](claude.md) — Projects, Artifacts, API
- [Cursor](cursor.md) — Composer + rules
- [Devin & coding agents](devin-and-agents.md) — tool definitions

## Support

Issues with integrations? [Open a GitHub issue](https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster/issues) with your AI platform, payload, and n8n execution error.
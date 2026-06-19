# Devin & AI Coding Agents Integration

Connect **Devin**, **GitHub Copilot Workspace**, **OpenHands**, **SWE-agent**, and other tool-calling AI agents to the n8n LinkedIn Poster webhook.

## Architecture

```
AI Agent  →  HTTP POST  →  n8n Webhook  →  AI Generation  →  LinkedIn API
                ↑
         Tool / shell definition
```

---

## Universal Tool Definition

Give your agent this tool schema (OpenAI function-calling format):

```json
{
  "type": "function",
  "function": {
    "name": "linkedin_ai_post",
    "description": "Generate and optionally publish a LinkedIn post with AI caption and image via n8n webhook. Always preview (dry_run=true) unless user confirms publish.",
    "parameters": {
      "type": "object",
      "properties": {
        "topic": {
          "type": "string",
          "description": "Post topic or theme"
        },
        "caption": {
          "type": "string",
          "description": "Pre-written caption (optional — skips AI text generation)"
        },
        "image_prompt": {
          "type": "string",
          "description": "Image generation prompt (optional)"
        },
        "tone": {
          "type": "string",
          "enum": ["professional", "insightful", "conversational", "bold"],
          "default": "professional"
        },
        "hashtags": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Hashtags to include, e.g. ['#AI', '#Automation']"
        },
        "dry_run": {
          "type": "boolean",
          "description": "true = preview only, false = publish to LinkedIn",
          "default": true
        }
      },
      "required": ["topic"]
    }
  }
}
```

### Tool Implementation (Python)

```python
import requests

WEBHOOK_URL = "https://YOUR-N8N-URL/webhook/linkedin-ai-post"

def linkedin_ai_post(topic, caption=None, image_prompt=None,
                     tone="professional", hashtags=None, dry_run=True):
    payload = {
        "topic": topic,
        "tone": tone,
        "dry_run": dry_run,
    }
    if caption:
        payload["caption"] = caption
    if image_prompt:
        payload["image_prompt"] = image_prompt
    if hashtags:
        payload["hashtags"] = hashtags

    resp = requests.post(WEBHOOK_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()
```

---

## Devin Setup

### 1. Add to Devin Knowledge

Paste into Devin's workspace knowledge:

```
LINKEDIN WEBHOOK: https://YOUR-N8N-URL/webhook/linkedin-ai-post

When asked to create LinkedIn content:
1. Generate JSON per prompts/linkedin-content-system-prompt.md
2. POST to webhook with dry_run=true
3. Show caption to user
4. Publish only on explicit confirmation (dry_run=false)
```

### 2. Devin Shell Command

```bash
curl -s -X POST "$LINKEDIN_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "'"$TOPIC"'",
    "tone": "insightful",
    "dry_run": true
  }' | jq .
```

### 3. Example Devin Prompt

```
Create and preview a LinkedIn post about our new open-source n8n workflow,
then wait for my approval before publishing.
```

---

## OpenHands / SWE-agent

Add a `linkedin_post` action to your agent config:

```yaml
actions:
  linkedin_post:
    type: http
    method: POST
    url: ${N8N_WEBHOOK_URL}/webhook/linkedin-ai-post
    headers:
      Content-Type: application/json
    body_template: |
      {
        "topic": "{{ topic }}",
        "dry_run": {{ dry_run | default(true) }},
        "tone": "{{ tone | default('professional') }}"
      }
```

---

## GitHub Copilot Workspace

1. Reference this repo in your issue/PR description
2. Add a task: "Post preview to LinkedIn webhook"
3. Copilot generates the curl command from `examples/webhook-payloads.json`

---

## Multi-Agent Pipelines

Chain agents for content pipelines:

```
Research Agent  →  topic + bullet points
       ↓
Writer Agent    →  caption JSON
       ↓
Designer Agent  →  image_prompt
       ↓
Publisher Tool  →  n8n webhook (dry_run=false)
```

Each agent passes structured JSON to the next. The final agent POSTs the assembled payload.

---

## Safety Guardrails

1. **Default `dry_run: true`** in all tool definitions
2. Require a confirmation token or explicit user message for publish
3. Rate-limit: max 5 publish calls per hour in your agent middleware
4. Log all `shareUrl` responses to an audit file

---

## Environment Variables for Agents

```bash
export N8N_WEBHOOK_URL=https://n8n.yourdomain.com/webhook/linkedin-ai-post
export N8N_BASIC_AUTH_USER=admin
export N8N_BASIC_AUTH_PASSWORD=yourpassword
```

See also: [General AI Assistants](general-ai-assistants.md) | [Troubleshooting](../troubleshooting.md)
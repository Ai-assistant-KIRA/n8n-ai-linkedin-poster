# Kiro Crew Integration

Trigger the n8n AI LinkedIn Poster directly from [Kiro Crew](https://kirocrew.com) — the autonomous agent management layer for Claude, GPT, and other AI assistants.

## Setup

1. **Start n8n** with Docker Compose (see [setup guide](../setup.md))
2. **Expose the webhook** — use ngrok, Cloudflare Tunnel, or deploy on a VPS:
   ```bash
   ngrok http 5678
   ```
3. **Set your webhook URL** in Kiro Crew's environment or pass it directly

## Trigger from Kiro Crew Chat

Ask your Kiro Crew agent:

> "Post on LinkedIn about how AI agents are transforming developer workflows"

The agent will:
1. Draft a caption using the system prompt
2. Generate an image prompt
3. Call the webhook with `dry_run: true` for preview
4. Show you the preview and ask for confirmation
5. Publish with `dry_run: false` on approval

## Scheduled Posting via Cron

Set up a recurring LinkedIn post schedule using Kiro Crew's built-in cron:

```
# Daily thought-leadership post at 9 AM UTC (peak LinkedIn engagement)
cron_add:
  name: "LinkedIn Daily Post"
  cron_expr: "0 9 * * 1-5"    # Weekdays at 9 AM UTC
  message: |
    Generate and publish a LinkedIn post about a trending topic in
    AI automation, developer tools, or no-code engineering.
    Use the n8n webhook at {WEBHOOK_URL}/webhook/linkedin-ai-post.
    Always preview first with dry_run: true, then publish.
  persistent_session: false
  minimal_context: true
  hide_in_chat: true
```

## Webhook Payload from Kiro Crew

```bash
curl -X POST https://your-n8n.example.com/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret" \
  -d '{
    "topic": "5 things I learned building production n8n workflows",
    "tone": "conversational",
    "hashtags": ["#n8n", "#Automation", "#AI"],
    "dry_run": true
  }'
```

## Silent Cron with Notification

For fire-and-forget publishing with dashboard notifications:

```python
# ~/.kiro/crew/crons/linkedin_poster.py
import json, urllib.request

def post_to_linkedin(ctx):
    payload = json.dumps({
        "topic": ctx.message,
        "tone": "professional",
        "dry_run": False
    }).encode()
    
    req = urllib.request.Request(
        "https://your-n8n.example.com/webhook/linkedin-ai-post",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Secret": "your-secret"
        }
    )
    
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    
    if result.get("success"):
        ctx.notify(f"✅ Published: {result['shareUrl']}")
    else:
        ctx.notify(f"❌ Failed: {result.get('error', 'unknown')}")
```

## Post-Publish Callback

Use the `callback_url` field to notify Kiro Crew after publishing:

```json
{
  "topic": "Weekly automation roundup",
  "dry_run": false,
  "callback_url": "https://your-kirocrew/webhook/linkedin-published"
}
```

The workflow POSTs `{postUrn, shareUrl, caption}` to your callback after a successful publish.

## AI Assistant Skill

Install the included skill for seamless integration:

```bash
cp -r skills/n8n-linkedin-poster/ ~/.kiro/crew/skills/
```

The skill teaches your Kiro Crew agent the webhook schema, preview/publish flow, and error handling.

## Tips

- **Always preview first** — set `dry_run: true` by default in cron jobs and agent instructions
- **Rate limit** — LinkedIn recommends staying under 50 posts/day for personal profiles; the v2.0 workflow enforces a configurable daily cap
- **Best posting times** — Tuesday–Thursday, 8–10 AM in your audience's timezone
- **Engagement hooks** — questions, polls, and "agree or disagree?" drive 3–5× more comments

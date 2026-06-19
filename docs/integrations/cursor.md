# Cursor Integration

Trigger the **n8n AI LinkedIn Poster** from **Cursor** using Composer, custom rules, and the terminal.

## Prerequisites

- n8n running locally (`docker compose up -d`) or on a remote server
- Cursor with Agent/Composer enabled

---

## Step 1: Add a Cursor Rule

Create `.cursor/rules/linkedin-poster.mdc` in your project (or add to User Rules):

```markdown
# LinkedIn Poster via n8n

When the user asks to create, preview, or publish a LinkedIn post:

1. Read `prompts/linkedin-content-system-prompt.md` for content guidelines
2. Webhook: `http://localhost:5678/webhook/linkedin-ai-post`
3. ALWAYS preview first with `"dry_run": true`
4. Show the user the caption before publishing
5. Only set `dry_run: false` when the user explicitly confirms

Example curl (run in terminal):
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{"topic": "...", "tone": "insightful", "dry_run": true}'

Payload reference: `examples/webhook-payloads.json`
```

---

## Step 2: Preview a Post (Composer)

**Prompt in Cursor:**

```
Preview a LinkedIn post about building production n8n workflows with AI assistants.
Tone: conversational. Use the n8n webhook with dry_run.
```

Cursor Agent will:
1. Read the prompt template
2. Run curl against localhost
3. Display the generated caption

---

## Step 3: Publish from Terminal

After reviewing the preview:

**Prompt:**

```
Publish that LinkedIn post now — same topic, dry_run false.
```

Or run manually:

```bash
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Building production n8n workflows with AI assistants",
    "tone": "conversational",
    "dry_run": false
  }'
```

---

## Step 4: Custom Skill (advanced)

Clone this repo into your workspace. Cursor can reference:

| File | Purpose |
|------|---------|
| `prompts/linkedin-content-system-prompt.md` | Content generation rules |
| `examples/webhook-payloads.json` | Payload templates |
| `docs/usage.md` | Webhook schema |

Add to your Cursor rule:

```
This workspace includes n8n-ai-linkedin-poster. Use its prompts and examples
when handling LinkedIn post requests.
```

---

## Remote n8n from Cursor

If n8n runs on a VPS while Cursor is local:

1. Set webhook URL in your rule to `https://n8n.yourdomain.com/webhook/linkedin-ai-post`
2. Add auth header if configured:

```bash
curl -X POST https://n8n.yourdomain.com/webhook/linkedin-ai-post \
  -u admin:yourpassword \
  -H "Content-Type: application/json" \
  -d '{"topic": "...", "dry_run": true}'
```

---

## Example Composer Session

```
You: Create 3 LinkedIn post previews about no-code automation trends

Cursor: [runs 3 curl commands with dry_run: true, shows captions]

You: Publish #2

Cursor: [runs curl with dry_run: false for topic #2, returns shareUrl]
```

---

## Tips

- Cursor can run curl directly — no extra MCP server needed
- Keep n8n running in Docker before asking Cursor to post
- Use `dry_run` for iteration; publishing is one webhook call
- For image review, check the n8n execution UI (binary preview on **Download AI Image** node)

See also: [General AI Assistants](general-ai-assistants.md)
# Install This Skill for Your AI Assistant

## Cursor

**Option A — Project rule (fastest)**

Copy [`.cursor/rules/n8n-linkedin-poster.mdc`](../../../.cursor/rules/n8n-linkedin-poster.mdc) into your project.

**Option B — Full skill**

```bash
git clone https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster.git
cp -r n8n-ai-linkedin-poster/skills/n8n-linkedin-poster .cursor/skills/
```

Set env in your shell or `.env`:

```bash
export N8N_WEBHOOK_URL=http://localhost:5678
```

---

## Claude (Projects)

1. Create a Project → **Add knowledge**
2. Upload:
   - `skills/n8n-linkedin-poster/SKILL.md`
   - `prompts/linkedin-content-system-prompt.md`
   - `examples/webhook-payloads.json`
3. Custom instructions:

```
Webhook: POST {N8N_WEBHOOK_URL}/webhook/linkedin-ai-post
Always dry_run: true first. Publish only on explicit confirmation.
Read skills/n8n-linkedin-poster/SKILL.md for the full workflow.
```

---

## Claude Code / Grok

```bash
git clone https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster.git
mkdir -p ~/.claude/skills   # or .grok/skills/ in your project
cp -r n8n-ai-linkedin-poster/skills/n8n-linkedin-poster ~/.claude/skills/
```

---

## Codex

```bash
cp -r skills/n8n-linkedin-poster ~/.codex/skills/
```

---

## Devin / Custom Agents

Add the tool definition from [docs/integrations/devin-and-agents.md](../../../docs/integrations/devin-and-agents.md) and include `SKILL.md` in workspace knowledge.

---

## Environment variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `N8N_WEBHOOK_URL` | `http://localhost:5678` | Base URL (path `/webhook/linkedin-ai-post` is appended) |
| `LINKEDIN_PERSON_ID` | Set in n8n/docker | Your OpenID `sub` — not needed by the AI, only n8n |
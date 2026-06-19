# Troubleshooting

Common issues and fixes for the **n8n AI LinkedIn Poster** workflow.

---

## Webhook Issues

### Webhook returns 404

| Cause | Fix |
|-------|-----|
| Workflow not active | Toggle **Active** in n8n workflow editor |
| Wrong path | Confirm URL ends with `/webhook/linkedin-ai-post` |
| Wrong n8n instance | Check port (5678) and host |

### Webhook times out

AI generation can take 30–90 seconds. Increase timeout in your AI tool/client.

In n8n: **Settings** → **Executions** → increase timeout if needed.

### External AI can't reach localhost

Use ngrok, Cloudflare Tunnel, n8n Cloud, or deploy to a VPS. See [setup.md](setup.md#exposing-webhooks-to-ai-assistants).

---

## LinkedIn API Errors

### 401 Unauthorized

- Reconnect LinkedIn OAuth credential in n8n
- Verify token hasn't expired
- Confirm app has **Share on LinkedIn** product approved

### 403 Forbidden

| Cause | Fix |
|-------|-----|
| Using built-in LinkedIn node | Use HTTP Request chain (this workflow already does) |
| Missing `w_member_social` scope | Re-authorize OAuth with correct scopes |
| Posting to wrong profile | Verify `LINKEDIN_PERSON_ID` matches authorized account |
| App not approved | Check Developer Portal → app status |

### 422 Unprocessable Entity

| Error | Fix |
|-------|-----|
| Missing `author` | Set `LINKEDIN_PERSON_ID` — must be OpenID `sub`, not numeric member ID |
| Missing `commentary` | Caption is empty — check AI Generate Caption node output |
| Invalid `content.media.id` | Image upload failed — check **LinkedIn Init Upload** and **Upload Image** nodes |

### 426 Version Header Required

Set `LINKEDIN_API_VERSION=202502` in your environment (default in **Configuration** node). If LinkedIn deprecates this version, update the env var — see [LinkedIn API versioning](https://learn.microsoft.com/en-us/linkedin/marketing/versioning).

### Webhook returns 500 JSON error

The workflow now returns structured errors via **Respond Error**:

```json
{
  "success": false,
  "error": "Set LINKEDIN_PERSON_ID in docker-compose/.env...",
  "failedNode": "Prepare LinkedIn Payload",
  "hint": "See docs/troubleshooting.md..."
}
```

Check `failedNode` in n8n **Executions** for the full stack trace.

---

## Image Upload Failures

### "No image binary available"

- Provide `image_url`, `image_base64`, or enable AI image generation
- Check **Download AI Image** node — DALL-E URL may have expired (regenerate)

### Image upload returns 403

- Image must be JPEG or PNG, max 10 MB
- Upload uses PUT to the signed URL from init — don't add OAuth to the PUT request (workflow handles this)

### Wrong Content-Type

The **LinkedIn Upload Image** node sets `Content-Type: image/jpeg`. If using PNG, change accordingly.

---

## AI Generation Issues

### Empty caption

- Check OpenAI credential and API key balance
- Verify **Merge Caption** reads the correct response field for your LLM node
- OpenAI node: `message.content`; Anthropic: `content[0].text`

### DALL-E content policy rejection

- Soften `image_prompt` — avoid branded logos, real people, violence
- Add "abstract illustration" to prompts

### High API costs

- Use `gpt-4o-mini` for captions (default)
- Preview with `dry_run: true` to avoid re-publishing
- Provide your own `caption` and `image_url` to skip AI nodes

---

## Person ID Issues

### "Set LINKEDIN_PERSON_ID environment variable"

1. Call `https://api.linkedin.com/v2/userinfo` with your OAuth token
2. Copy the `sub` field
3. Set in docker-compose or workflow

### Posts appear on wrong profile

The Person ID must match the OAuth-authorized account. Re-check `sub` from userinfo.

---

## n8n-Specific

### `$credentials is not defined` in Code node

n8n 2.x blocks credential access in Code nodes. This workflow uses **HTTP Request** nodes with OAuth — don't replace them with Code-based API calls.

### Credential ID not found after import

Replace `REPLACE_WITH_YOUR_OPENAI_CREDENTIAL_ID` and `REPLACE_WITH_YOUR_LINKEDIN_CREDENTIAL_ID` in each node after import.

### Execution succeeds but no post on LinkedIn

- Check `dry_run` wasn't `true`
- Verify **LinkedIn Create Post** returned `x-restli-id` header
- Check response `shareUrl` — open it while logged into LinkedIn

---

## Debug Checklist

```
□ Workflow is Active
□ LinkedIn OAuth connected (green checkmark)
□ LINKEDIN_PERSON_ID is OpenID sub
□ OpenAI credential valid
□ dry_run: false for publishing
□ Webhook URL reachable from client
□ n8n execution shows green on all nodes
□ LinkedIn Developer App has Share on LinkedIn approved
```

---

## Still Stuck?

1. Open n8n → **Executions** → click failed run → inspect red node
2. Copy error message and node name
3. [Open a GitHub issue](https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster/issues) with:
   - n8n version
   - Error output (redact tokens)
   - Payload used (redact personal info)
   - Screenshot of failed node
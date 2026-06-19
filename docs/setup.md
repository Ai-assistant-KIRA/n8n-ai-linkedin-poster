# Setup Guide

Complete fresh-install guide for the **n8n AI LinkedIn Poster** workflow.

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| [n8n](https://n8n.io/) ≥ 1.0 | Self-hosted or n8n Cloud |
| LinkedIn Developer App | With **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect** products |
| AI provider account | OpenAI (default), or swap nodes for Anthropic/Azure/etc. |
| Public webhook URL | Required for external AI tools; use [ngrok](https://ngrok.com/) or your server domain |

> **⚠️ LinkedIn API requirements:** You can only post to profiles you own. Company Page posting requires additional permissions. Image posts use the [LinkedIn Images API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api) and [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api) (REST v202502).

---

## Step 1: Start n8n

### Option A — Docker Compose (recommended)

```bash
git clone https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster.git
cd n8n-ai-linkedin-poster
docker compose up -d
```

Open **http://localhost:5678** and complete the n8n owner setup.

### Option B — npm

```bash
npm install -g n8n
export LINKEDIN_PERSON_ID=YOUR_PERSON_ID
n8n start
```

### Option C — n8n Cloud

Import the workflow JSON from the n8n Cloud UI. Set environment variables in your instance settings if available, or hardcode `personId` in the **Parse Webhook Input** node.

---

## Step 2: Create Your LinkedIn Developer App (Required)

**You must bring your own credentials.** This repo includes no API keys or OAuth tokens.

Follow the complete guide: **[docs/linkedin-developer-app.md](linkedin-developer-app.md)**

Quick summary:
1. Create an app at [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Request **Share on LinkedIn** + **Sign In with LinkedIn using OpenID Connect**
3. Add redirect URL: `http://localhost:5678/rest/oauth2-credential/callback`
4. Copy **your** Client ID and Client Secret

---

## Step 3: Configure LinkedIn OAuth in n8n

1. In n8n: **Credentials** → **New** → **LinkedIn OAuth2 API**
2. Enter Client ID and Client Secret from your Developer App
3. Scopes (minimum):
   - `openid`
   - `profile`
   - `w_member_social`
4. Click **Connect my account** and authorize with the LinkedIn profile you will post as
5. Save the credential as `LinkedIn OAuth2`

---

## Step 4: Get Your LinkedIn Person URN

The workflow needs your **Person ID** (OpenID `sub` claim), not the legacy numeric member ID.

### Method A — OpenID userinfo endpoint

After OAuth is connected, call:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.linkedin.com/v2/userinfo
```

Response includes `"sub": "AbCdEfGhIj"` — this is your Person ID.

### Method B — n8n test execution

Add a temporary HTTP Request node:
- URL: `https://api.linkedin.com/v2/userinfo`
- Auth: LinkedIn OAuth2 credential

Run it and copy the `sub` value.

### Set the Person ID

**Option 1 — Environment variable (recommended):**

```bash
# docker-compose.yml
LINKEDIN_PERSON_ID=AbCdEfGhIj
```

**Option 2 — Edit workflow:**

Open **Parse Webhook Input** and replace `YOUR_PERSON_ID` in the default fallback.

Your URN will be: `urn:li:person:AbCdEfGhIj`

---

## Step 5: Configure OpenAI (or alternative)

1. **Credentials** → **New** → **OpenAI API**
2. Paste your API key
3. In the workflow, open **AI Generate Caption** and **AI Generate Image** nodes
4. Select your OpenAI credential (replace `REPLACE_WITH_YOUR_OPENAI_CREDENTIAL_ID` after import)

---

## Step 6: Import the Workflow

1. n8n UI → **Workflows** → **Import from File**
2. Select `workflows/linkedin-ai-poster.json`
3. Import `workflows/linkedin-ai-poster-errors.json` (optional — for error logging)
4. Open each node with `REPLACE_WITH_YOUR_*` and assign credentials
5. Set env vars on the **Configuration** node: `LINKEDIN_PERSON_ID`, `LINKEDIN_API_VERSION` (default `202502`)
6. **Activate** the main workflow (toggle in top-right)
7. (Optional) Main workflow **Settings → Error Workflow** → select *AI LinkedIn Poster - Error Handler*

Your webhook URL will be:

```
POST http://localhost:5678/webhook/linkedin-ai-post
```

For production, set `WEBHOOK_URL` in docker-compose to your public domain.

---

## Step 7: Verify with a Dry Run

```bash
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Test post — please ignore",
    "dry_run": true
  }'
```

Expected response:

```json
{
  "success": true,
  "dryRun": true,
  "caption": "...",
  "message": "Preview only — set dry_run: false to publish."
}
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `LINKEDIN_PERSON_ID` | Yes | OpenID `sub` from userinfo |
| `LINKEDIN_API_VERSION` | No | LinkedIn REST version header (default `202502`) |
| `WEBHOOK_URL` | Prod | Public base URL for webhooks |
| `OPENAI_API_KEY` | Optional | Can use n8n Credentials UI instead |
| `N8N_BASIC_AUTH_*` | Recommended | Protect your n8n instance |

---

## Exposing Webhooks to AI Assistants

Local n8n is not reachable from Claude/Cursor cloud agents. Options:

1. **ngrok:** `ngrok http 5678` → use the HTTPS URL
2. **Cloudflare Tunnel:** persistent tunnel to your server
3. **n8n Cloud:** built-in public webhook URLs
4. **VPS:** deploy docker-compose on a server with HTTPS

Always use HTTPS in production and protect your instance with auth.

---

## Next Steps

- [Configuration](configuration.md) — customize prompts and AI providers
- [Usage](usage.md) — webhook schema and publishing flow
- [Integrations](integrations/general-ai-assistants.md) — connect your AI assistant
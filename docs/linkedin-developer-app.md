# LinkedIn Developer App Setup (Bring Your Own Credentials)

**This repository ships zero credentials.** Every user creates their own LinkedIn Developer App, connects their own OAuth account, and posts to their own profile.

You will never find API keys, Client Secrets, or Person IDs in this repo — by design.

---

## Overview

```
You create LinkedIn App  →  You add OAuth in n8n  →  You set Person ID  →  You post to YOUR profile
```

| What | Who provides it |
|------|-----------------|
| LinkedIn Developer App | **You** (free, ~10 min setup) |
| Client ID + Client Secret | **Your** app credentials |
| OAuth authorization | **Your** LinkedIn account |
| Person ID (`sub`) | **Your** OpenID identity |
| OpenAI API key | **Your** AI provider account |

---

## Step 1: Create Your LinkedIn Developer App

1. Sign in at [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Click **Create app**
3. Fill in:
   - **App name** — e.g. `My n8n LinkedIn Poster`
   - **LinkedIn Page** — link any Company Page you admin (required by LinkedIn; can be a personal business page)
   - **Privacy policy URL** — any valid URL (your site, GitHub repo, or a simple privacy page)
   - **App logo** — optional
4. Agree to terms → **Create app**

> LinkedIn may take a few minutes to a few days to approve product access. Personal posting works once **Share on LinkedIn** is granted.

---

## Step 2: Request Required Products

In your app → **Products** tab, request:

| Product | Why you need it |
|---------|-----------------|
| **Sign In with LinkedIn using OpenID Connect** | Modern OAuth + Person ID (`sub`) |
| **Share on LinkedIn** | Create UGC posts with images on your profile |

Click **Request access** for each. Approval is usually automatic for personal use cases.

Official reference: [Share on LinkedIn documentation](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)

---

## Step 3: Configure OAuth Redirect URL

In your app → **Auth** tab → **OAuth 2.0 settings**:

**Authorized redirect URLs** — add your n8n callback:

| Environment | Redirect URL |
|-------------|--------------|
| Local Docker | `http://localhost:5678/rest/oauth2-credential/callback` |
| n8n Cloud | `https://YOUR-INSTANCE.app.n8n.cloud/rest/oauth2-credential/callback` |
| Self-hosted VPS | `https://n8n.yourdomain.com/rest/oauth2-credential/callback` |

Copy your **Client ID** and **Client Secret** from this tab — you'll paste them into n8n next.

---

## Step 4: Connect Credentials in n8n

### LinkedIn OAuth2

1. n8n → **Credentials** → **Add credential** → **LinkedIn OAuth2 API**
2. Paste **your** Client ID and Client Secret
3. Ensure scopes include:
   - `openid`
   - `profile`
   - `w_member_social`
4. Click **Connect my account**
5. Authorize with the LinkedIn profile you want to post as
6. Save as `LinkedIn OAuth2` (or any name — update workflow nodes to match)

### OpenAI API

1. n8n → **Credentials** → **Add credential** → **OpenAI API**
2. Paste **your** API key from [platform.openai.com](https://platform.openai.com/api-keys)
3. Save as `OpenAI API`

### Assign credentials to workflow nodes

After importing `workflows/linkedin-ai-poster.json`, open these nodes and select your credentials:

- **AI Generate Caption** → OpenAI API
- **AI Generate Image** → OpenAI API
- **LinkedIn Init Upload** → LinkedIn OAuth2 API
- **LinkedIn Create Post** → LinkedIn OAuth2 API

---

## Step 5: Get Your Person ID

Your Person ID is the OpenID `sub` claim — **not** the old numeric member ID.

```bash
# After OAuth is connected, use n8n HTTP Request node or curl:
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.linkedin.com/v2/userinfo
```

Response:

```json
{
  "sub": "AbCdEfGhIj",
  "name": "Your Name",
  "given_name": "Your",
  "family_name": "Name",
  "picture": "https://..."
}
```

Copy `sub` → set as environment variable:

```bash
# .env or docker-compose.yml
LINKEDIN_PERSON_ID=AbCdEfGhIj
```

Your author URN becomes: `urn:li:person:AbCdEfGhIj`

---

## Step 6: Verify Before Publishing

```bash
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test preview — please ignore", "dry_run": true}'
```

Only publish to your profile after preview looks correct:

```bash
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -d '{"topic": "Your real topic", "dry_run": false}'
```

---

## Security Checklist

- [ ] Never commit `.env`, Client Secret, or API keys
- [ ] Use a **separate** LinkedIn app per environment (dev vs prod)
- [ ] Rotate secrets if accidentally exposed
- [ ] Enable n8n basic auth or SSO on public instances
- [ ] Default AI assistants to `dry_run: true`

---

## Common Approval Issues

| Issue | Solution |
|-------|----------|
| "Share on LinkedIn" pending | Wait for approval; check app verification status |
| No Company Page to link | Create a minimal LinkedIn Company Page or use one you admin |
| OAuth redirect mismatch | Redirect URL must match n8n callback exactly |
| 403 on post | Re-authorize OAuth; confirm `w_member_social` scope |

---

## Next Steps

- [Full setup guide](setup.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
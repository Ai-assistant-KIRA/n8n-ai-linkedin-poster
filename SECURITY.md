# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅        |
| < 1.0   | ❌        |

## Reporting a Vulnerability

Please **do not** open public issues for security vulnerabilities.

1. Open a [GitHub Security Advisory](https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster/security/advisories/new) (preferred)
2. Or email the maintainer via GitHub profile contact

We aim to respond within 72 hours.

## Security Best Practices

### 1. Webhook authentication (required in production)

Set a strong secret:

```bash
WEBHOOK_SECRET=your-long-random-secret-here
```

Pass on every request:

```bash
curl -X POST http://localhost:5678/webhook/linkedin-ai-post \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-long-random-secret-here" \
  -d '{"topic": "...", "dry_run": true}'
```

### 2. Protect your n8n instance

- Enable `N8N_BASIC_AUTH` or SSO on public deployments
- Use HTTPS (reverse proxy or n8n Cloud)
- Do not expose port 5678 to the public internet without auth

### 3. Credential hygiene

- Never commit `.env`, Client Secrets, API keys, or Person IDs
- Use separate LinkedIn apps for dev and production
- Rotate `WEBHOOK_SECRET` and OAuth tokens if exposed

### 4. Safe publishing defaults

- AI assistants should default to `dry_run: true`
- Only set `dry_run: false` on explicit user confirmation
- Use `publish: false` to generate content without posting

### 5. LinkedIn API scope

This workflow posts only to the OAuth-authorized profile. It cannot post on behalf of other users without their tokens.
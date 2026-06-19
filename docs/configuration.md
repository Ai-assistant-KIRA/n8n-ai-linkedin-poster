# Configuration Guide

Customize the **n8n AI LinkedIn Poster** workflow for your brand, tone, and AI stack.

## Webhook Input Schema

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `topic` | string | — | Subject for AI caption + image generation |
| `caption` | string | — | Pre-written post text (skips AI caption) |
| `text` | string | — | Alias for `caption` |
| `image_prompt` | string | auto | DALL-E / image model prompt |
| `image_url` | string | — | Public URL to existing image (skips AI image) |
| `image_base64` | string | — | Base64-encoded image data |
| `tone` | string | `professional` | Caption voice: `professional`, `insightful`, `conversational`, `bold` |
| `hashtags` | string[] | `[]` | Extra hashtags for AI to include |
| `media_title` | string | topic | LinkedIn image title (max 200 chars) |
| `visibility` | string | `PUBLIC` | `PUBLIC` or `CONNECTIONS` |
| `dry_run` | boolean | `false` | `true` = preview only, no LinkedIn API calls |
| `publish` | boolean | `true` | `false` = generate content but don't post |
| `generate_caption` | boolean | auto | Force AI caption even if topic is empty |
| `generate_image` | boolean | auto | Force AI image generation |

See `examples/webhook-payloads.json` for copy-paste examples.

---

## Customizing AI Caption Generation

Open the **AI Generate Caption** node.

### Tone

Pass `tone` in the webhook or edit the system prompt:

```
You write high-performing LinkedIn posts in a {tone} voice...
```

### Length

Adjust `maxTokens` (default 800). For shorter posts, add to the user prompt:

```
Keep under 800 characters. Prefer 5-7 short lines.
```

### Hashtag Strategy

Edit the system prompt rules:

```
- Use exactly 3 hashtags
- Place hashtags on their own line at the end
- Mix 1 broad (#AI) + 2 niche (#n8n #WorkflowAutomation)
```

Or pass explicit hashtags in the webhook payload.

### CTA Types

Add CTA instructions to the system prompt:

| CTA Style | Prompt Addition |
|-----------|-----------------|
| Question | "End with an open question to drive comments" |
| Poll-style | "End with 'A, B, or C?' format" |
| Resource | "End with 'Comment LINK and I'll send the template'" |
| Soft sell | "End with one line about our free guide — no hard sell" |

---

## Customizing AI Image Generation

Open the **AI Generate Image** node.

### Default prompt template

The **Parse Webhook Input** node auto-builds:

```
Professional LinkedIn infographic about: {topic}. Clean, modern, high-contrast, no text overlays.
```

Override with `image_prompt` in the webhook for full control.

### Image style presets

Add a `style` field to your webhook and branch in a Code node:

| Style | Prompt suffix |
|-------|---------------|
| `infographic` | "flat infographic, icons, data visualization, blue palette" |
| `photo` | "professional stock photo style, natural lighting, shallow depth of field" |
| `abstract` | "abstract geometric art, gradient background, tech aesthetic" |
| `minimal` | "minimal illustration, lots of whitespace, 2-color palette" |

### Image size

DALL-E 3 supports `1024x1024`, `1792x1024`, `1024x1792`. LinkedIn feed prefers square or 1.91:1 landscape.

> **LinkedIn image specs:** JPEG or PNG, max 10 MB. Recommended 1200×1200 or 1200×627.

---

## Supported AI Providers

The workflow ships with **OpenAI** nodes. Swap them for any compatible provider:

| Provider | Text Node | Image Node |
|----------|-----------|------------|
| OpenAI | OpenAI Chat | OpenAI Image (DALL-E 3) |
| Anthropic | Anthropic Chat | — (use separate image provider) |
| Azure OpenAI | Azure OpenAI Chat | Azure OpenAI Image |
| Google Gemini | Google Gemini Chat | Imagen via HTTP |
| Replicate | — | HTTP Request → Replicate API |
| Stability AI | — | HTTP Request → Stability API |
| Local (Ollama) | Ollama Chat | — |

### Swapping to Anthropic for captions

1. Replace **AI Generate Caption** with **Anthropic** node
2. Use the system prompt from `prompts/linkedin-content-system-prompt.md`
3. Update **Merge Caption** to read `$json.content[0].text` (Anthropic response shape)

### Swapping to Replicate for images

1. Replace **AI Generate Image** with HTTP Request:
   - POST `https://api.replicate.com/v1/predictions`
   - Poll for completion
2. Pass output URL to **Download AI Image**

---

## LinkedIn Settings

### API Version (configurable)

The **Configuration** node reads `LINKEDIN_API_VERSION` from your environment (default: **`202502`** — proven stable for image upload + UGC posts).

```bash
# docker-compose.yml or .env
LINKEDIN_API_VERSION=202502
```

Used on **LinkedIn Init Upload** and **LinkedIn Create Post** headers. Update when LinkedIn deprecates versions — see [LinkedIn API versioning](https://learn.microsoft.com/en-us/linkedin/marketing/versioning).

### Image Content-Type (auto-detected)

**Prepare LinkedIn Payload** detects `image/jpeg` or `image/png` from binary `mimeType` or file extension. **LinkedIn Upload Image** sends the dynamic Content-Type header.

| Format | Supported by LinkedIn |
|--------|---------------------|
| JPEG | ✅ |
| PNG | ✅ (DALL-E default) |
| WebP / GIF | ❌ — add a conversion step or override in Prepare LinkedIn Payload |

Preview responses include `imageContentType` and `imageFormatWarning` when format may be unsupported.

### HTTP Retries

LinkedIn HTTP nodes retry **3 times** with 3s backoff (`retryOnFail`, `maxTries: 3`). Image download nodes retry 3x with 2s backoff.

### Error Handling

Failed nodes route to **Format Error Response** → **Respond Error** (HTTP 500 JSON). Optionally import `workflows/linkedin-ai-poster-errors.json` and link it as **Settings → Error Workflow** for execution logging/alerts.

### Visibility

| Value | Behavior |
|-------|----------|
| `PUBLIC` | Anyone on LinkedIn |
| `CONNECTIONS` | Connections only |

### Rate Limits

LinkedIn enforces per-app and per-member limits. For personal profiles, stay under ~150 posts/day. Add a **Wait** node or queue for high-volume use.

---

## Security Hardening

1. Enable `N8N_BASIC_AUTH` in production
2. Add a **Webhook Auth** header check (custom Code node or n8n Header Auth)
3. Never commit credentials or Person IDs
4. Use `dry_run: true` as default in AI assistant prompts
5. Rotate LinkedIn OAuth tokens if compromised

---

## Workflow-Level Notes

After import, update credential IDs in these nodes:

- AI Generate Caption
- AI Generate Image
- LinkedIn Init Upload
- LinkedIn Create Post

Add an **Error Trigger** workflow for Slack/email notifications on failure (optional).
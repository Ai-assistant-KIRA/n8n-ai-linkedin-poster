# Webhook Input Schema

```
POST /webhook/linkedin-ai-post
Content-Type: application/json
```

## Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `topic` | string | — | Subject for AI caption + image |
| `caption` | string | — | Pre-written text (skips AI caption) |
| `text` | string | — | Alias for `caption` |
| `image_prompt` | string | auto | Image generation prompt |
| `image_url` | string | — | Public image URL (skips AI image) |
| `image_base64` | string | — | Base64 image data |
| `tone` | string | `professional` | `professional`, `insightful`, `conversational`, `bold` |
| `hashtags` | string[] | `[]` | Extra hashtags |
| `media_title` | string | topic | LinkedIn image title |
| `visibility` | string | `PUBLIC` | `PUBLIC` or `CONNECTIONS` |
| `dry_run` | boolean | `false` | `true` = preview only |
| `publish` | boolean | `true` | `false` = generate but don't post |
| `generate_caption` | boolean | auto | Force AI caption |
| `generate_image` | boolean | auto | Force AI image |

## Example payloads

Copy from [examples/webhook-payloads.json](../../../examples/webhook-payloads.json).
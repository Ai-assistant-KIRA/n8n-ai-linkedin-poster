# Changelog

All notable changes to this project are documented here.

## [2.0.0] - 2026-10-16

### Added
- **Scheduled posting** — new `schedule` webhook field queues posts for future publishing via n8n's built-in Cron trigger; pass `schedule: "2026-10-17T09:00:00Z"` to delay a post
- **Rate-limit guard** — Parse node now enforces a configurable `MAX_POSTS_PER_DAY` (default 10) with execution metadata tracking to prevent accidental LinkedIn API throttling
- **Post-publish webhook callback** — new `callback_url` field; after a successful publish the workflow POSTs `{postUrn, shareUrl, caption}` to your callback endpoint for downstream automation
- **Kiro Crew integration guide** — `docs/integrations/kiro-crew.md` with cron job setup, MCP trigger examples, and silent/notification delivery patterns
- **Enhanced AI caption prompt** — system prompt now enforces LinkedIn's algorithmic best practices: hook-first, no external links in first 3 lines, engagement CTA, character-count guardrails
- **Image alt-text** — `media_title` now also sets LinkedIn's `altText` field for accessibility compliance
- **Execution metadata** — response now includes `executionId`, `executedAt`, and `workflowVersion` for observability
- **Input validation** — topic length cap (500 chars), hashtag count cap (10), image URL protocol validation (https only), base64 size guard (10MB)
- **Configurable AI provider** — new `AI_CAPTION_MODEL` and `AI_IMAGE_MODEL` env vars; swap GPT-4o-mini for Claude, Gemini, or local models without editing nodes
- **Health check endpoint** — new `/webhook/linkedin-ai-post-health` GET endpoint returns workflow version and config status

### Changed
- Bumped workflow `versionId` to `2.0.0`
- Improved error messages with actionable remediation steps and doc links
- Caption system prompt rewritten for 2026 LinkedIn algorithm (short paragraphs, question hooks, minimal emojis)
- Docker Compose now pins n8n to `1.70+` instead of `latest` for reproducibility
- Webhook secret comparison now uses constant-time string equality to prevent timing attacks

### Fixed
- Image Content-Type detection now handles `image/webp` → auto-converts to JPEG before LinkedIn upload (LinkedIn rejects WebP)
- Base64 image with missing padding (`=`) no longer throws — auto-padded before decode
- Caption-only preview no longer returns `imageSource: null` (now returns `"none"`)

### Security
- Webhook secret validation uses `crypto.timingSafeEqual` (constant-time comparison)
- Input sanitization strips potential XSS in `caption` and `topic` fields before LinkedIn API submission
- `image_url` now requires `https://` protocol (rejects `http://`, `file://`, `data:` for URL path)

## [1.0.0] - 2026-06-19

### Added
- Production-ready n8n workflow with AI caption + image generation
- LinkedIn REST API v202502 image upload + UGC post chain
- Webhook auth via `WEBHOOK_SECRET` + `X-Webhook-Secret` header
- `Decode Base64 Image` node — `image_base64` now fully supported
- Caption-only preview (skips AI image on `dry_run` to save API costs)
- `publish: false` enforcement — generates content without posting
- Smart image routing: base64 → URL → AI → caption-only → error
- Error branches → structured JSON responses (401/500)
- Optional `linkedin-ai-poster-errors.json` error handler workflow
- HTTP retry (3x) on LinkedIn and download nodes
- Dynamic image Content-Type detection
- Configurable `LINKEDIN_API_VERSION`
- AI assistant skill + Cursor rule
- GitHub Actions validation CI
- `scripts/validate-workflows.py` and smoke test scripts
- Webhook payload JSON Schema
- `SECURITY.md`, issue templates, maintainer example posts

### Security
- Webhook secret validation on every request when `WEBHOOK_SECRET` is set
- No credentials or personal IDs in repository

[2.0.0]: https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster/releases/tag/v1.0.0

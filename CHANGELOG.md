# Changelog

All notable changes to this project are documented here.

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

[1.0.0]: https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster/releases/tag/v1.0.0
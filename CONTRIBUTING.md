# Contributing to n8n-ai-linkedin-poster

Thank you for helping make AI-powered LinkedIn automation accessible to everyone! 🎉

## Ways to Contribute

- **Bug reports** — Open an issue with steps to reproduce, n8n version, and error output
- **Workflow improvements** — PRs for new nodes, error handling, or AI provider support
- **Documentation** — Fix typos, add integration guides, improve setup clarity
- **Example posts** — Submit anonymized example screenshots to `assets/` (see below)
- **Prompt templates** — Add high-performing prompts to `prompts/`

## Development Setup

1. Fork the repository
2. Clone locally and start n8n:
   ```bash
   docker compose up -d
   ```
3. Import `workflows/linkedin-ai-poster.json` in the n8n UI
4. Configure credentials (see [docs/setup.md](docs/setup.md))
5. Test with `dry_run: true` before any live publish

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Do **not** include personal data, API keys, Person URNs, or real LinkedIn profile info
- Update relevant docs when changing workflow behavior or webhook schema
- Add example payloads to `examples/webhook-payloads.json` for new input modes
- Test the workflow import on a fresh n8n instance before submitting

## Submitting Example Post Screenshots

We welcome anonymized example post mockups or screenshots (with permission):

1. Blur or remove all identifying information
2. Save as `assets/example-post-N.jpg` (next available number)
3. Add a row to the README "Example AI-Generated Posts" table
4. Include theme, engagement style note, and placeholder URL

## Code of Conduct

Be respectful, constructive, and inclusive. We're building tools for the community — let's keep it welcoming.

## Questions?

Open a [GitHub Discussion](https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster/discussions) or issue. We're happy to help!
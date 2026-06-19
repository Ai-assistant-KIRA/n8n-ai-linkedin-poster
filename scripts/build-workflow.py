#!/usr/bin/env python3
"""Regenerate linkedin-ai-poster.json with A+ workflow fixes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workflows" / "linkedin-ai-poster.json"

PARSE_JS = r"""const raw = $input.first().json;
const body = raw.body ?? raw;
const headers = raw.headers || {};
const config = $('Configuration').first().json;

const topic = (body.topic || '').trim();
const caption = (body.caption || body.text || '').trim();
const imagePrompt = (body.image_prompt || body.imagePrompt || '').trim();
const imageUrl = (body.image_url || body.imageUrl || '').trim();
const imageBase64 = body.image_base64 || body.imageBase64 || null;
const tone = (body.tone || 'professional').trim();
const hashtags = Array.isArray(body.hashtags) ? body.hashtags : [];
const dryRun = Boolean(body.dry_run ?? body.dryRun ?? false);
const publish = body.publish !== false;
const forceImage = Boolean(body.generate_image ?? body.generateImage ?? false);

const secret = (config.webhookSecret || '').trim();
if (secret && secret !== 'DISABLED') {
  const provided = (
    headers['x-webhook-secret'] ||
    headers['X-Webhook-Secret'] ||
    body.webhook_secret ||
    body.webhookSecret ||
    ''
  ).trim();
  if (provided !== secret) {
    return [{
      json: {
        unauthorized: true,
        success: false,
        error: 'Invalid or missing X-Webhook-Secret header',
        hint: 'Set WEBHOOK_SECRET in env and pass header X-Webhook-Secret on every request.',
      },
    }];
  }
}

const hasImageUrl = !!imageUrl;
const hasImageBase64 = !!imageBase64;
const skipAiImage = dryRun && !forceImage;
const needsAiImage = !hasImageUrl && !hasImageBase64 && !skipAiImage && (imagePrompt || topic || forceImage);
const needsCaption = !caption && (topic || body.generate_caption);
const shouldPost = !dryRun && publish;
const captionOnlyPreview = dryRun && !hasImageUrl && !hasImageBase64 && !needsAiImage;

return [{
  json: {
    topic,
    caption,
    imagePrompt: imagePrompt || (topic ? `Professional LinkedIn infographic about: ${topic}. Clean, modern, high-contrast, no text overlays.` : ''),
    imageUrl,
    imageBase64,
    tone,
    hashtags,
    dryRun,
    publish,
    shouldPost,
    forceImage,
    needsCaption,
    hasImageUrl,
    hasImageBase64,
    needsAiImage,
    captionOnlyPreview,
    personId: config.personId,
    linkedinApiVersion: config.linkedinApiVersion,
    httpMaxRetries: config.httpMaxRetries,
    mediaTitle: (body.media_title || body.mediaTitle || topic || 'AI Generated Post').slice(0, 200),
    visibility: body.visibility || 'PUBLIC',
  },
}];"""

DECODE_BASE64_JS = r"""const item = $input.first().json;
const raw = item.imageBase64 || '';
const dataUriMatch = raw.match(/^data:(image\/[a-zA-Z0-9.+-]+);base64,(.+)$/);
const mimeType = dataUriMatch ? dataUriMatch[1] : 'image/jpeg';
const b64 = dataUriMatch ? dataUriMatch[2] : raw.replace(/^data:image\/\w+;base64,/, '');
if (!b64) throw new Error('image_base64 is empty');
const ext = mimeType.includes('png') ? 'png' : 'jpg';
return [{
  json: { ...item, imageSource: 'base64' },
  binary: {
    data: {
      data: b64,
      mimeType,
      fileName: `linkedin-post.${ext}`,
    },
  },
}];"""

PREPARE_JS = r"""const content = $('Merge Caption Branches').first().json;
const input = $input.first();
const binary = input.binary;

if (!binary) {
  throw new Error('No image binary available. Provide image_url, image_base64, or enable AI image generation.');
}

const binaryKey = Object.keys(binary).find((k) => binary[k]?.data) || 'data';
const bin = binary[binaryKey];
if (!bin?.data) throw new Error('Image binary is empty.');

let imageContentType = bin.mimeType || 'application/octet-stream';
const fileName = bin.fileName || 'linkedin-post.jpg';
if (!imageContentType || imageContentType === 'application/octet-stream') {
  const ext = (fileName.split('.').pop() || 'jpg').toLowerCase();
  const map = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif', webp: 'image/webp' };
  imageContentType = map[ext] || 'image/jpeg';
}

const linkedinAccepted = ['image/jpeg', 'image/png'];
const imageFormatWarning = linkedinAccepted.includes(imageContentType)
  ? null
  : `LinkedIn accepts JPEG/PNG only. Detected ${imageContentType}. Add a conversion step or override to image/jpeg.`;

const personId = (content.personId || '').trim();
if (!personId || personId === 'YOUR_PERSON_ID') {
  throw new Error('Set LINKEDIN_PERSON_ID in docker-compose/.env or the Configuration node.');
}

const imageSource = content.imageSource || (content.imageUrl ? 'url' : content.imageBase64 ? 'base64' : 'ai-generated');

return [{
  json: {
    ...content,
    personUrn: `urn:li:person:${personId}`,
    imageFileName: fileName,
    imageContentType,
    imageFormatWarning,
    imageSource,
    linkedinApiVersion: content.linkedinApiVersion || '202502',
  },
  binary: { data: bin },
}];"""

CAPTION_PREVIEW_JS = r"""const item = $input.first().json;
if (!item.caption && !item.topic) {
  throw new Error('Preview requires a topic or caption.');
}
return [{
  json: {
    success: true,
    dryRun: true,
    captionOnly: true,
    caption: item.caption || `(caption will be AI-generated from topic: ${item.topic})`,
    captionSource: item.captionSource || (item.caption ? 'provided' : 'ai-generated'),
    imageSource: null,
    imageSkipped: true,
    mediaTitle: item.mediaTitle,
    linkedinApiVersion: item.linkedinApiVersion,
    message: 'Caption-only preview — set generate_image: true to preview with AI image, or dry_run: false to publish.',
  },
}];"""

FORMAT_ERROR_JS = r"""const item = $input.first();
const j = item.json || {};
if (j.unauthorized) {
  return [{ json: { ...j, statusCode: 401 } }];
}
const executionError = j.error || j;
const message =
  executionError.message ||
  executionError.description ||
  j.message ||
  (typeof executionError === 'string' ? executionError : null) ||
  'Workflow execution failed';
return [{
  json: {
    success: false,
    error: String(message).slice(0, 1000),
    failedNode: String(j.$node?.name || j.node || 'unknown'),
    hint: 'See docs/troubleshooting.md — verify LINKEDIN_PERSON_ID, OAuth, WEBHOOK_SECRET, LINKEDIN_API_VERSION.',
    docs: 'https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster/blob/main/docs/troubleshooting.md',
    statusCode: j.statusCode || 500,
  },
}];"""

def node(node_id, name, ntype, position, parameters, **extra):
    base = {
        "parameters": parameters,
        "id": node_id,
        "name": name,
        "type": ntype,
        "typeVersion": extra.pop("typeVersion", 2),
        "position": position,
    }
    base.update(extra)
    return base

workflow = {
    "name": "AI LinkedIn Poster",
    "nodes": [
        node("sticky-main", "Workflow Notes", "n8n-nodes-base.stickyNote", [-200, 80], {
            "content": "## AI LinkedIn Poster v1.0\n\n`POST /webhook/linkedin-ai-post`\n\n1. Set env vars in **Configuration**\n2. Assign OpenAI + LinkedIn OAuth credentials\n3. Set `WEBHOOK_SECRET` for production\n4. Import `linkedin-ai-poster-errors.json` (optional)\n\nDocs: https://github.com/Ai-assistant-KIRA/n8n-ai-linkedin-poster",
            "height": 300, "width": 400, "color": 4,
        }, typeVersion=1),
        node("sticky-config", "Configuration Notes", "n8n-nodes-base.stickyNote", [300, 60], {
            "content": "## Env vars\n| Variable | Required |\n|----------|----------|\n| `LINKEDIN_PERSON_ID` | ✅ |\n| `WEBHOOK_SECRET` | prod ✅ |\n| `LINKEDIN_API_VERSION` | optional (202502) |\n\n**Credentials:** OpenAI API, LinkedIn OAuth2",
            "height": 280, "width": 340, "color": 5,
        }, typeVersion=1),
        node("webhook", "Webhook Trigger", "n8n-nodes-base.webhook", [240, 400], {
            "httpMethod": "POST", "path": "linkedin-ai-post", "responseMode": "responseNode", "options": {},
        }, typeVersion=2, webhookId="linkedin-ai-post", notesInFlow=True,
           notes="Pass X-Webhook-Secret header when WEBHOOK_SECRET is set."),
        node("configuration", "Configuration", "n8n-nodes-base.set", [400, 400], {
            "mode": "manual", "duplicateItem": False,
            "assignments": {"assignments": [
                {"id": "personId", "name": "personId", "value": "={{ $env.LINKEDIN_PERSON_ID || 'YOUR_PERSON_ID' }}", "type": "string"},
                {"id": "linkedinApiVersion", "name": "linkedinApiVersion", "value": "={{ $env.LINKEDIN_API_VERSION || '202502' }}", "type": "string"},
                {"id": "webhookSecret", "name": "webhookSecret", "value": "={{ $env.WEBHOOK_SECRET || '' }}", "type": "string"},
                {"id": "httpMaxRetries", "name": "httpMaxRetries", "value": 3, "type": "number"},
            ]}, "options": {},
        }, typeVersion=3.4, notesInFlow=True),
        node("parse", "Parse Webhook Input", "n8n-nodes-base.code", [580, 400], {
            "mode": "runOnceForAllItems", "language": "javaScript", "jsCode": PARSE_JS,
        }, onError="continueErrorOutput", notesInFlow=True),
        node("if-unauthorized", "Unauthorized?", "n8n-nodes-base.if", [760, 400], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "unauth", "leftValue": "={{ $json.unauthorized }}", "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"}}], "combinator": "and"}, "options": {},
        }),
        node("if-needs-caption", "Needs Caption?", "n8n-nodes-base.if", [960, 400], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "c", "leftValue": "={{ $json.needsCaption }}", "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"}}], "combinator": "and"}, "options": {},
        }),
        node("openai-caption", "AI Generate Caption", "@n8n/n8n-nodes-langchain.openAi", [1180, 280], {
            "resource": "chat", "operation": "complete", "chatModel": "gpt-4o-mini",
            "prompt": {"messages": [
                {"role": "system", "content": "You write high-performing LinkedIn posts. Output ONLY the post text — no titles, no markdown fences. Use short paragraphs, 1-2 emojis max, 3-5 relevant hashtags at the end."},
                {"role": "user", "content": "=Write a LinkedIn post.\n\nTopic: {{ $json.topic || 'automation and AI productivity' }}\nTone: {{ $json.tone }}\nExtra hashtags: {{ $json.hashtags.join(' ') }}\n\nKeep under 1300 characters. Start with a strong hook."},
            ]}, "options": {"temperature": 0.7, "maxTokens": 800},
        }, typeVersion=1.8, onError="continueErrorOutput",
           credentials={"openAiApi": {"id": "REPLACE_WITH_YOUR_OPENAI_CREDENTIAL_ID", "name": "OpenAI API"}}),
        node("merge-caption", "Merge Caption", "n8n-nodes-base.code", [1400, 280], {
            "mode": "runOnceForAllItems", "language": "javaScript",
            "jsCode": "const parsed = $('Parse Webhook Input').first().json;\nconst ai = $input.first().json;\nconst generated = ai.message?.content || ai.text || ai.output || '';\nif (!parsed.caption && !generated.trim()) throw new Error('AI caption generation returned empty text.');\nreturn [{ json: { ...parsed, caption: (parsed.caption || generated).trim(), captionSource: parsed.caption ? 'provided' : 'ai-generated' } }];",
        }, onError="continueErrorOutput"),
        node("pass-caption", "Use Provided Caption", "n8n-nodes-base.code", [1180, 520], {
            "mode": "runOnceForAllItems", "language": "javaScript",
            "jsCode": "const p = $input.first().json; return [{ json: { ...p, captionSource: 'provided' } }];",
        }),
        node("merge-branches", "Merge Caption Branches", "n8n-nodes-base.merge", [1620, 400], {
            "mode": "combine", "combineBy": "combineAll", "options": {},
        }, typeVersion=3),
        node("if-base64", "Has Base64 Image?", "n8n-nodes-base.if", [1840, 400], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "b", "leftValue": "={{ $json.hasImageBase64 }}", "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"}}], "combinator": "and"}, "options": {},
        }),
        node("decode-base64", "Decode Base64 Image", "n8n-nodes-base.code", [2060, 280], {
            "mode": "runOnceForAllItems", "language": "javaScript", "jsCode": DECODE_BASE64_JS,
        }, onError="continueErrorOutput"),
        node("if-url", "Has Image URL?", "n8n-nodes-base.if", [2060, 480], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "u", "leftValue": "={{ $json.hasImageUrl }}", "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"}}], "combinator": "and"}, "options": {},
        }),
        node("download-url", "Download Image URL", "n8n-nodes-base.httpRequest", [2280, 400], {
            "url": "={{ $json.imageUrl }}",
            "options": {"response": {"response": {"responseFormat": "file"}}},
        }, typeVersion=4.2, retryOnFail=True, maxTries=3, waitBetweenTries=2000, onError="continueErrorOutput"),
        node("if-ai-image", "Needs AI Image?", "n8n-nodes-base.if", [2280, 580], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "a", "leftValue": "={{ $json.needsAiImage }}", "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"}}], "combinator": "and"}, "options": {},
        }),
        node("openai-image", "AI Generate Image", "@n8n/n8n-nodes-langchain.openAi", [2500, 500], {
            "resource": "image", "operation": "generate", "prompt": "={{ $json.imagePrompt }}",
            "options": {"size": "1024x1024", "style": "vivid"},
        }, typeVersion=1.8, onError="continueErrorOutput",
           credentials={"openAiApi": {"id": "REPLACE_WITH_YOUR_OPENAI_CREDENTIAL_ID", "name": "OpenAI API"}}),
        node("download-ai", "Download AI Image", "n8n-nodes-base.httpRequest", [2720, 500], {
            "url": "={{ $json.data[0].url || $json.url }}",
            "options": {"response": {"response": {"responseFormat": "file"}}},
        }, typeVersion=4.2, retryOnFail=True, maxTries=3, waitBetweenTries=2000, onError="continueErrorOutput"),
        node("if-caption-only", "Caption Only Preview?", "n8n-nodes-base.if", [2500, 700], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "co", "leftValue": "={{ $json.captionOnlyPreview }}", "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"}}], "combinator": "and"}, "options": {},
        }),
        node("caption-preview", "Build Caption Preview", "n8n-nodes-base.code", [2720, 820], {
            "mode": "runOnceForAllItems", "language": "javaScript", "jsCode": CAPTION_PREVIEW_JS,
        }, onError="continueErrorOutput"),
        node("prepare", "Prepare LinkedIn Payload", "n8n-nodes-base.code", [2940, 400], {
            "mode": "runOnceForAllItems", "language": "javaScript", "jsCode": PREPARE_JS,
        }, onError="continueErrorOutput", notesInFlow=True),
        node("if-should-post", "Should Post?", "n8n-nodes-base.if", [3160, 400], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "sp", "leftValue": "={{ $json.shouldPost }}", "rightValue": True,
                            "operator": {"type": "boolean", "operation": "equals"}}], "combinator": "and"}, "options": {},
        }),
        node("respond-preview", "Respond Preview", "n8n-nodes-base.respondToWebhook", [3380, 280], {
            "respondWith": "json",
            "responseBody": "={{ $json.captionOnly ? $json : { success: true, dryRun: true, caption: $json.caption, captionSource: $json.captionSource, imageSource: $json.imageSource, imageContentType: $json.imageContentType, imageFormatWarning: $json.imageFormatWarning, mediaTitle: $json.mediaTitle, linkedinApiVersion: $json.linkedinApiVersion, message: 'Preview only — set dry_run: false and publish: true to post.' } }}",
            "options": {"responseCode": 200},
        }, typeVersion=1.1),
        node("linkedin-init", "LinkedIn Init Upload", "n8n-nodes-base.httpRequest", [3380, 520], {
            "method": "POST", "url": "https://api.linkedin.com/rest/images?action=initializeUpload",
            "authentication": "predefinedCredentialType", "nodeCredentialType": "linkedInOAuth2Api",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "LinkedIn-Version", "value": "={{ $json.linkedinApiVersion || '202502' }}"},
                {"name": "X-Restli-Protocol-Version", "value": "2.0.0"},
            ]},
            "sendBody": True, "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ initializeUploadRequest: { owner: $json.personUrn } }) }}",
            "options": {},
        }, typeVersion=4.2, retryOnFail=True, maxTries=3, waitBetweenTries=3000, onError="continueErrorOutput",
           credentials={"linkedInOAuth2Api": {"id": "REPLACE_WITH_YOUR_LINKEDIN_CREDENTIAL_ID", "name": "LinkedIn OAuth2"}}),
        node("merge-upload", "Merge Upload Data", "n8n-nodes-base.code", [3600, 520], {
            "mode": "runOnceForAllItems", "language": "javaScript",
            "jsCode": "const prepared = $('Prepare LinkedIn Payload').first();\nconst init = $input.first();\nconst value = init.json.value || init.json.body?.value || init.json;\nif (!value?.uploadUrl || !value?.image) throw new Error(`LinkedIn init upload failed: ${JSON.stringify(init.json).slice(0, 500)}`);\nreturn [{ json: { ...prepared.json, uploadUrl: value.uploadUrl, imageUrn: value.image }, binary: prepared.binary }];",
        }, onError="continueErrorOutput"),
        node("linkedin-upload", "LinkedIn Upload Image", "n8n-nodes-base.httpRequest", [3820, 520], {
            "method": "PUT", "url": "={{ $json.uploadUrl }}", "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "Content-Type", "value": "={{ $json.imageContentType || 'image/jpeg' }}"}]},
            "sendBody": True, "contentType": "binaryData", "inputDataFieldName": "data", "options": {},
        }, typeVersion=4.2, retryOnFail=True, maxTries=3, waitBetweenTries=3000, onError="continueErrorOutput"),
        node("linkedin-post", "LinkedIn Create Post", "n8n-nodes-base.httpRequest", [4040, 520], {
            "method": "POST", "url": "https://api.linkedin.com/rest/posts",
            "authentication": "predefinedCredentialType", "nodeCredentialType": "linkedInOAuth2Api",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "LinkedIn-Version", "value": "={{ $('Merge Upload Data').first().json.linkedinApiVersion || '202502' }}"},
                {"name": "X-Restli-Protocol-Version", "value": "2.0.0"},
            ]},
            "sendBody": True, "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ author: $('Merge Upload Data').first().json.personUrn, commentary: $('Merge Upload Data').first().json.caption, visibility: $('Merge Upload Data').first().json.visibility, distribution: { feedDistribution: 'MAIN_FEED', thirdPartyDistributionChannels: [] }, lifecycleState: 'PUBLISHED', content: { media: { title: $('Merge Upload Data').first().json.mediaTitle, id: $('Merge Upload Data').first().json.imageUrn } } }) }}",
            "options": {"response": {"response": {"fullResponse": True}}},
        }, typeVersion=4.2, retryOnFail=True, maxTries=3, waitBetweenTries=3000, onError="continueErrorOutput",
           credentials={"linkedInOAuth2Api": {"id": "REPLACE_WITH_YOUR_LINKEDIN_CREDENTIAL_ID", "name": "LinkedIn OAuth2"}}),
        node("finalize", "Finalize Result", "n8n-nodes-base.code", [4260, 520], {
            "mode": "runOnceForAllItems", "language": "javaScript",
            "jsCode": "const merged = $('Merge Upload Data').first().json;\nconst post = $input.first();\nconst headers = post.json.headers || {};\nconst postUrn = headers['x-restli-id'] || headers['X-Restli-Id'];\nif (!postUrn) throw new Error('LinkedIn create post missing x-restli-id header');\nreturn [{ json: { success: true, dryRun: false, postUrn, shareUrl: `https://www.linkedin.com/feed/update/${encodeURIComponent(postUrn)}/`, caption: merged.caption, captionSource: merged.captionSource, imageSource: merged.imageSource, imageContentType: merged.imageContentType, mediaTitle: merged.mediaTitle, linkedinApiVersion: merged.linkedinApiVersion, api: `linkedin-rest-v${merged.linkedinApiVersion || '202502'}` } }];",
        }, onError="continueErrorOutput"),
        node("respond-success", "Respond Success", "n8n-nodes-base.respondToWebhook", [4480, 520], {
            "respondWith": "json", "responseBody": "={{ $json }}", "options": {"responseCode": 200},
        }, typeVersion=1.1),
        node("format-error", "Format Error Response", "n8n-nodes-base.code", [4260, 720], {
            "mode": "runOnceForAllItems", "language": "javaScript", "jsCode": FORMAT_ERROR_JS,
        }),
        node("if-error-code", "Error Status?", "n8n-nodes-base.if", [4480, 720], {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{"id": "e401", "leftValue": "={{ $json.statusCode }}", "rightValue": 401,
                            "operator": {"type": "number", "operation": "equals"}}], "combinator": "and"}, "options": {},
        }),
        node("respond-error", "Respond Error", "n8n-nodes-base.respondToWebhook", [4700, 820], {
            "respondWith": "json", "responseBody": "={{ $json }}", "options": {"responseCode": 500},
        }, typeVersion=1.1),
        node("respond-unauthorized", "Respond Unauthorized", "n8n-nodes-base.respondToWebhook", [4700, 620], {
            "respondWith": "json", "responseBody": "={{ $json }}", "options": {"responseCode": 401},
        }, typeVersion=1.1),
        node("format-missing-image", "Missing Image Error", "n8n-nodes-base.code", [2720, 700], {
            "mode": "runOnceForAllItems", "language": "javaScript",
            "jsCode": "throw new Error('Image required to publish. Provide image_url, image_base64, or enable AI image generation (generate_image: true).');",
        }, onError="continueErrorOutput"),
    ],
    "connections": {
        "Webhook Trigger": {"main": [[{"node": "Configuration", "type": "main", "index": 0}]]},
        "Configuration": {"main": [[{"node": "Parse Webhook Input", "type": "main", "index": 0}]]},
        "Parse Webhook Input": {"main": [
            [{"node": "Unauthorized?", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Unauthorized?": {"main": [
            [{"node": "Format Error Response", "type": "main", "index": 0}],
            [{"node": "Needs Caption?", "type": "main", "index": 0}],
        ]},
        "Needs Caption?": {"main": [
            [{"node": "AI Generate Caption", "type": "main", "index": 0}],
            [{"node": "Use Provided Caption", "type": "main", "index": 0}],
        ]},
        "AI Generate Caption": {"main": [
            [{"node": "Merge Caption", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Merge Caption": {"main": [
            [{"node": "Merge Caption Branches", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Use Provided Caption": {"main": [[{"node": "Merge Caption Branches", "type": "main", "index": 1}]]},
        "Merge Caption Branches": {"main": [[{"node": "Has Base64 Image?", "type": "main", "index": 0}]]},
        "Has Base64 Image?": {"main": [
            [{"node": "Decode Base64 Image", "type": "main", "index": 0}],
            [{"node": "Has Image URL?", "type": "main", "index": 0}],
        ]},
        "Decode Base64 Image": {"main": [
            [{"node": "Prepare LinkedIn Payload", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Has Image URL?": {"main": [
            [{"node": "Download Image URL", "type": "main", "index": 0}],
            [{"node": "Needs AI Image?", "type": "main", "index": 0}],
        ]},
        "Download Image URL": {"main": [
            [{"node": "Prepare LinkedIn Payload", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Needs AI Image?": {"main": [
            [{"node": "AI Generate Image", "type": "main", "index": 0}],
            [{"node": "Caption Only Preview?", "type": "main", "index": 0}],
        ]},
        "AI Generate Image": {"main": [
            [{"node": "Download AI Image", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Download AI Image": {"main": [
            [{"node": "Prepare LinkedIn Payload", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Caption Only Preview?": {"main": [
            [{"node": "Build Caption Preview", "type": "main", "index": 0}],
            [{"node": "Missing Image Error", "type": "main", "index": 0}],
        ]},
        "Build Caption Preview": {"main": [
            [{"node": "Respond Preview", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Missing Image Error": {"main": [
            [],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Prepare LinkedIn Payload": {"main": [
            [{"node": "Should Post?", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Should Post?": {"main": [
            [{"node": "LinkedIn Init Upload", "type": "main", "index": 0}],
            [{"node": "Respond Preview", "type": "main", "index": 0}],
        ]},
        "LinkedIn Init Upload": {"main": [
            [{"node": "Merge Upload Data", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Merge Upload Data": {"main": [
            [{"node": "LinkedIn Upload Image", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "LinkedIn Upload Image": {"main": [
            [{"node": "LinkedIn Create Post", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "LinkedIn Create Post": {"main": [
            [{"node": "Finalize Result", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Finalize Result": {"main": [
            [{"node": "Respond Success", "type": "main", "index": 0}],
            [{"node": "Format Error Response", "type": "main", "index": 0}],
        ]},
        "Format Error Response": {"main": [[{"node": "Error Status?", "type": "main", "index": 0}]]},
        "Error Status?": {"main": [
            [{"node": "Respond Unauthorized", "type": "main", "index": 0}],
            [{"node": "Respond Error", "type": "main", "index": 0}],
        ]},
    },
    "settings": {"executionOrder": "v1", "errorWorkflow": "", "callerPolicy": "workflowsFromSameOwner"},
    "active": False,
    "versionId": "1.2.0",
    "meta": {"templateCredsSetupCompleted": False, "instanceId": "n8n-ai-linkedin-poster"},
    "pinData": {},
    "tags": [{"name": "linkedin"}, {"name": "ai"}, {"name": "social-media"}],
}

OUT.write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {OUT}")
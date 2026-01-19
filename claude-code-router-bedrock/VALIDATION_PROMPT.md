# Validation Prompt (Lean) for Bedrock Integration

> **Purpose:** Validate the Bedrock integration for Claude Code Router with minimal, high‑signal checks.

## Phase 1: Problem & Architecture

**Requirement:**
- Claude Code → claude-code-router → local Bedrock proxy → AWS Bedrock Claude
- AWS credentials configured in `~/.aws/*`

**Architecture Path (expected):**
```
Claude Code CLI (Anthropic Messages)
  → Router (localhost:3456)
  → Provider request (OpenAI Chat Completions)
  → Bedrock Proxy (localhost:3457)
      OpenAI → Anthropic → Bedrock Converse
      Bedrock → Anthropic → OpenAI
  → Router → Claude Code CLI
```

**Must‑Know Constraints:**
- Bedrock rejects `role: "system"` in messages. System must be top‑level.
- Claude 4.5: temperature OR top_p, not both.
- Bedrock toolChoice uses **one‑of keys**: `{auto:{}}`, `{any:{}}`, `{tool:{name}}`.
- Model IDs must map to Bedrock inference profiles.
- **No empty text blocks** in Bedrock content.

## Phase 2: Design Validation

**Files:**
- `claude-code-router-bedrock/proxy-server.js`
- `claude-code-router-bedrock/transformers/bedrock-transformer.js`

**Checks:**
- Proxy accepts OpenAI Chat Completions (router default format).
- Proxy converts OpenAI → Anthropic → Bedrock and back.
- Streaming returns valid OpenAI SSE chunks.

## Phase 3: Implementation Checks

**Transformer (`bedrock-transformer.js`):**
- System extraction from messages array.
- Tools map: OpenAI `parameters` → Anthropic `input_schema` → Bedrock `inputSchema.json`.
- toolChoice emits `{auto:{}}|{any:{}}|{tool:{name}}`.
- Model ID mapping includes Claude Code raw IDs.

**Proxy (`proxy-server.js`):**
- OpenAI → Anthropic conversion.
- Filters empty text blocks (no blank ContentBlock).
- Proper tool/result mapping.
- Streaming returns OpenAI SSE chunks + `[DONE]`.

## Phase 4: Minimal Tests

**Non‑streaming:**
```
curl -s -X POST http://127.0.0.1:3456/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: test" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"bedrock,sonnet","max_tokens":64,"messages":[{"role":"user","content":"Say hello"}]}'
```

**Streaming:**
```
curl -N -s -X POST http://127.0.0.1:3456/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: test" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"bedrock,sonnet","max_tokens":64,"stream":true,"messages":[{"role":"user","content":"Say hello"}]}'
```

**Tools (forced):**
```
curl -s -X POST http://127.0.0.1:3456/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: test" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"bedrock,sonnet","max_tokens":128,"messages":[{"role":"user","content":"What is 2+3? Use the calculator tool."}],"tools":[{"name":"calculator","description":"do math","input_schema":{"type":"object","properties":{"a":{"type":"number"},"b":{"type":"number"},"op":{"type":"string"}},"required":["a","b","op"]}}],"tool_choice":{"type":"any"}}'
```

## Phase 5: Final Report (Brief)

Provide:
- Top blockers (if any)
- Verified working paths
- Remaining known limitations

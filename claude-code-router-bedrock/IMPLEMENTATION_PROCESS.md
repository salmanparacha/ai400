# Implementation Process (Lean)

> **Purpose:** Concise record of what was built and the fixes required to make it work.

## Architecture Used

Claude Code CLI → claude-code-router → **Bedrock proxy (OpenAI endpoint)** → Bedrock Converse API.

Key detail: router sends **OpenAI Chat Completions** to providers by default, so the proxy must accept OpenAI format.

## What Was Implemented

1) **OpenAI → Anthropic conversion** in the proxy  
   - Extract system messages  
   - Map tools to Anthropic `input_schema`  
   - Convert tool calls / tool results  

2) **Anthropic → Bedrock Converse** in transformer  
   - System field moved to top‑level  
   - Tool schema wrapped in `inputSchema.json`  
   - **toolChoice mapped to Bedrock one‑of keys**  
     - `{auto:{}}`, `{any:{}}`, `{tool:{name}}`

3) **Model ID mapping**  
   - Added Claude Code raw IDs (e.g., `claude-sonnet-4-5-20250929`) → Bedrock inference profiles

4) **Streaming compatibility**  
   - Proxy emits OpenAI SSE chunks + `[DONE]`  
   - Used non‑streaming Bedrock response to build a single SSE sequence

5) **Empty ContentBlock guard**  
   - Filter empty text blocks  
   - Provide fallback `[empty]` for blank content

## Key Fixes (Root Causes)

- Router expects OpenAI format → proxy adjusted to accept OpenAI  
- Bedrock toolChoice rejected `{type:"auto"}` → required one‑of key shape  
- Bedrock rejects empty text blocks → filter blank content  
- Claude Code raw model IDs not mapped → added mappings  

## Current Status

- **Basic chat works**  
- **Streaming works (SSE)**  
- **Tools depend on model behavior** (toolChoice now valid, model may still choose not to call)

## Notes

If a 500 appears:
- Check Bedrock proxy log: `/tmp/bedrock-proxy.log`
- Restart proxy to ensure latest code is running

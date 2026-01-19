# Complete API Mapping: Anthropic ↔ Bedrock ↔ OpenAI

## Critical Differences

### 1. Message Roles

| API | Allowed Roles in Messages | System Prompt |
|-----|--------------------------|---------------|
| **Anthropic** | `user`, `assistant` | Top-level `system` field (string or array) |
| **Bedrock** | `user`, `assistant` | Top-level `system` array `[{text: "..."}]` |
| **OpenAI** | `user`, `assistant`, `system` | Can be message with `role: "system"` |

**⚠️ CRITICAL:** Bedrock will reject ANY message with `role: "system"`!

### 2. System Prompts

**Anthropic:**
```json
{
  "system": "You are helpful" // or array of text blocks
}
```

**Bedrock:**
```json
{
  "system": [{"text": "You are helpful"}] // MUST be array
}
```

**OpenAI:**
```json
{
  "messages": [
    {"role": "system", "content": "You are helpful"} // in messages array
  ]
}
```

### 3. Tools/Functions

**Anthropic:**
```json
{
  "tools": [{
    "name": "get_weather",
    "description": "...",
    "input_schema": {
      "type": "object",
      "properties": {...}
    }
  }]
}
```

**Bedrock:**
```json
{
  "toolConfig": {
    "tools": [{
      "toolSpec": {
        "name": "get_weather",
        "description": "...",
        "inputSchema": {
          "json": {
            "type": "object",
            "properties": {...}
          }
        }
      }
    }]
  }
}
```

**OpenAI:**
```json
{
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "...",
      "parameters": {
        "type": "object",
        "properties": {...}
      }
    }
  }]
}
```

### 4. Temperature & Top_P

| API | Can Use Both? | Notes |
|-----|--------------|-------|
| **Anthropic (Claude 3.x)** | ✅ Yes | Both allowed |
| **Anthropic (Claude 4.5)** | ❌ No | Choose one only |
| **Bedrock (Claude 4.5)** | ❌ No | Choose one only |
| **OpenAI** | ✅ Yes | Both allowed |

**⚠️ CRITICAL:** Bedrock Claude 4.5 will reject requests with both!

### 5. Content Blocks

**Anthropic:**
```json
{
  "content": [
    {"type": "text", "text": "..."},
    {"type": "image", "source": {...}},
    {"type": "tool_use", "id": "...", "name": "...", "input": {...}},
    {"type": "tool_result", "tool_use_id": "...", "content": "..."}
  ]
}
```

**Bedrock:**
```json
{
  "content": [
    {"text": "..."},
    {"image": {"format": "jpeg", "source": {...}}},
    {"toolUse": {"toolUseId": "...", "name": "...", "input": {...}}},
    {"toolResult": {"toolUseId": "...", "content": [{...}]}}
  ]
}
```

**OpenAI:**
```json
{
  "content": "text string", // or
  "content": [
    {"type": "text", "text": "..."},
    {"type": "image_url", "image_url": {...}}
  ],
  "tool_calls": [
    {"id": "...", "type": "function", "function": {"name": "...", "arguments": "{...}"}}
  ]
}
```

### 6. Response Format

**Anthropic:**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [...],
  "model": "claude-...",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

**Bedrock:**
```json
{
  "output": {
    "message": {
      "role": "assistant",
      "content": [...]
    }
  },
  "stopReason": "end_turn",
  "usage": {
    "inputTokens": 10,
    "outputTokens": 20
  }
}
```

**OpenAI:**
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-...",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "...",
      "tool_calls": [...]
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## Common Transformation Issues

### Issue 1: System Messages in Messages Array
**Problem:** OpenAI allows `{"role": "system"}` in messages, Bedrock rejects it
**Solution:** Extract system messages from array and move to top-level `system` field

### Issue 2: Null Tools
**Problem:** Router may send `tools: [null, null, ...]`
**Solution:** Filter out null/invalid tools before transformation

### Issue 3: Temperature + Top_P
**Problem:** Claude 4.5 rejects both parameters
**Solution:** Prefer temperature, omit top_p

### Issue 4: Tool Response Format
**Problem:** Different field names and structures
**Solution:** Map `tool_use_id` ↔ `toolUseId`, wrap content properly

### Issue 5: Stop Reasons
**Problem:** Different enum values
**Solution:** Map `end_turn` ↔ `stop`, `max_tokens` ↔ `length`

## Required Transformations

### Router → Bedrock (Request)

1. ✅ Extract `role: "system"` messages → `system` array
2. ✅ Filter null tools
3. ✅ Transform tool schema: `input_schema` → `inputSchema.json`
4. ✅ Choose temperature OR top_p (not both)
5. ✅ Map model names to inference profiles
6. ✅ Transform content blocks

### Bedrock → Router (Response)

1. ✅ Extract response from `output.message`
2. ✅ Map `stopReason` → `finish_reason`
3. ✅ Convert to OpenAI format with `choices` array
4. ✅ Map token counts: `inputTokens` → `prompt_tokens`
5. ✅ Handle tool calls in OpenAI format

## Implementation Checklist

- [x] Filter system messages from messages array
- [x] Move system messages to top-level field
- [x] Filter null/invalid tools
- [x] Validate tool names exist
- [x] Use temperature-only (no top_p)
- [x] Map model IDs to inference profiles
- [x] Transform tool schema structure
- [x] Map stop reasons
- [x] Convert response format to OpenAI
- [ ] Handle tool_result responses properly
- [ ] Support streaming format conversion

# Known Limitations & Untested Features

## ⚠️ Not Tested

### 1. Streaming Responses
**Status:** Code written but NEVER TESTED

**Risk:** HIGH - Stream events have completely different formats

**What Could Break:**
- Event name mapping
- Delta content aggregation
- Token counting in streams
- Error handling during streaming

**Test Before Use:**
```bash
curl -N -X POST http://localhost:3456/v1/messages \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model": "bedrock/sonnet", "max_tokens": 100, "stream": true, "messages": [...]}'
```

### 2. Tool Results (Return Path)
**Status:** NOT IMPLEMENTED

**Risk:** HIGH - Will break tool use workflows

**What Happens:**
When Claude uses a tool and you return results, the transformation might fail.

**Anthropic Format:**
```json
{
  "role": "user",
  "content": [{
    "type": "tool_result",
    "tool_use_id": "toolu_123",
    "content": "42 degrees"
  }]
}
```

**Bedrock Format:**
```json
{
  "role": "user",
  "content": [{
    "toolResult": {
      "toolUseId": "toolu_123",
      "content": [{"text": "42 degrees"}]
    }
  }]
}
```

**Fix Needed:** Add tool result transformation in `transformContent()`

### 3. Image/Multimodal Content
**Status:** Partially implemented, NOT TESTED

**Risk:** MEDIUM

**What Could Break:**
- Base64 encoding/decoding
- Media type mapping
- Image size limits
- PDF/document support

### 4. Error Response Mapping
**Status:** Basic only

**Risk:** MEDIUM - Users won't get helpful error messages

**Current:** Returns generic errors
**Needed:** Map Bedrock errors to Anthropic error format

### 5. Message Validation
**Status:** Minimal

**Risk:** LOW-MEDIUM

**Not Validated:**
- Empty messages
- Content length limits
- Invalid role sequences
- Missing required fields
- Type mismatches

### 6. Token Limits
**Status:** Not enforced

**Risk:** LOW - Bedrock will reject, but not gracefully

**Different Limits:**
- Haiku: 4,096 tokens
- Sonnet: 8,192 tokens
- Opus: 4,096 tokens

### 7. Rate Limiting
**Status:** Not handled

**Risk:** LOW - AWS handles it, but no retry logic

**Missing:**
- Exponential backoff
- Rate limit headers
- Queue management

## 🔴 Definitely Will Break

### Tool Use Multi-Turn Conversations
If you use tools in a conversation with multiple back-and-forth exchanges:

1. Claude requests tool use ✅ Works
2. You send tool result ❌ **BREAKS** - not transforming tool results correctly
3. Claude responds ❌ Won't get here

**Fix Required:** Implement tool result content block transformation

### Streaming with Tools
Tool use in streaming mode has complex event sequences. Not tested at all.

## 🟡 Might Break

### Large Context Windows
- Messages with 100K+ tokens
- Very long system prompts
- Many tools defined

### Special Content Types
- Citations
- Thinking blocks (Claude extended thinking)
- Search results
- Redacted content

### Edge Cases
- Unicode/emoji in tool names
- Very long tool descriptions
- Nested JSON in tool inputs
- Binary data in images

## ✅ Known to Work

- Basic text conversations ✅
- Simple tool definitions (without actual use) ✅
- System prompts ✅
- Temperature settings ✅
- Multiple models ✅
- Token counting ✅

## Recommendations

### Before Production Use:

1. **Test streaming thoroughly**
2. **Implement tool result transformation**
3. **Add comprehensive error mapping**
4. **Add input validation**
5. **Test with real tool use workflows**
6. **Test image inputs**
7. **Add retry logic**
8. **Add request/response logging**
9. **Create integration tests**
10. **Load test with concurrent requests**

### For Development Use:

Current implementation is fine for:
- Basic text chat
- Testing Bedrock integration
- Comparing model responses
- Cost optimization experiments

Not ready for:
- Production tool use
- Streaming applications
- Multimodal applications
- High-reliability systems

## Testing Checklist

```markdown
- [ ] Streaming responses
- [ ] Tool use (full workflow)
- [ ] Tool results return
- [ ] Image inputs
- [ ] PDF/document inputs
- [ ] Error scenarios
- [ ] Rate limiting
- [ ] Concurrent requests
- [ ] Large contexts
- [ ] All three models (opus, sonnet, haiku)
- [ ] Message validation
- [ ] Edge cases (empty, null, invalid)
```

## Version

Last Updated: 2026-01-18
Status: Development/Testing
Production Ready: NO (see above)

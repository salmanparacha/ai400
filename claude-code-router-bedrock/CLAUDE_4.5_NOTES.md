# Claude 4.5 on AWS Bedrock - Important Notes

## Breaking Changes in Claude 4.5

### Temperature and Top_P Restriction

**CRITICAL**: Claude 4.5 models (Opus, Sonnet, Haiku) introduced a **breaking API change** where you **CANNOT** specify both `temperature` and `top_p` parameters simultaneously.

**Error Message:**
```
ValidationException: The model returned the following errors: `temperature` and `top_p` cannot both be specified for this model. Please use only one.
```

**Affected Models:**
- Claude Opus 4.5 (November 2025)
- Claude Sonnet 4.5 (September 2025)
- Claude Haiku 4.5 (October 2025)
- Claude Opus 4.1 (August 2025)

**Not Affected:**
- Claude 3.x models (can use both parameters)

**Solution:**
Anthropic's official recommendation: **"You usually only need to use temperature"**
- `top_p` is designated for "advanced use cases only"
- Most applications should use `temperature` only

**Transformer Implementation:**
```javascript
// Prefer temperature over top_p
if (anthropicRequest.temperature !== undefined) {
  bedrockRequest.inferenceConfig.temperature = anthropicRequest.temperature;
} else if (anthropicRequest.top_p !== undefined) {
  bedrockRequest.inferenceConfig.topP = anthropicRequest.top_p;
} else {
  bedrockRequest.inferenceConfig.temperature = 1.0; // Default
}
```

## Inference Profiles Required

Claude 4.5 models **cannot** be invoked using direct model IDs with on-demand throughput. You **must** use **inference profiles**.

**Old (doesn't work):**
```
anthropic.claude-sonnet-4-5-20250929-v1:0
```

**New (required):**
```
global.anthropic.claude-sonnet-4-5-20250929-v1:0
us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

**Error Message:**
```
ValidationException: Invocation of model ID anthropic.claude-sonnet-4-5-20250929-v1:0 with on-demand throughput isn't supported. Retry your request with the ID or ARN of an inference profile that contains this model.
```

### Available Inference Profiles

| Model | Global Profile | US Profile |
|-------|---------------|------------|
| Claude Opus 4.5 | `global.anthropic.claude-opus-4-5-20251101-v1:0` | `us.anthropic.claude-opus-4-5-20251101-v1:0` |
| Claude Sonnet 4.5 | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Claude Haiku 4.5 | `global.anthropic.claude-haiku-4-5-20251001-v1:0` | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |

**Benefits of Inference Profiles:**
- Route traffic across multiple regions for high availability
- Automatic failover
- Lower latency through optimal region selection

## Timeout Requirements

Claude 4.5 models have a **60-minute timeout** for inference calls.

**Problem:**
AWS SDK clients default to **1-minute timeout**, which will cause timeouts on longer responses.

**Solution:**
Increase read timeout to at least 60 minutes:
```python
# Python (botocore)
config = Config(read_timeout=3600)
client = boto3.client('bedrock-runtime', config=config)
```

```javascript
// Node.js (AWS SDK v3)
const client = new BedrockRuntimeClient({
  requestHandler: {
    requestTimeout: 3600000 // 60 minutes in milliseconds
  }
});
```

## Model Availability by Region

Not all regions have Claude 4.5 models available. Check your region:

```bash
# List available models
aws bedrock list-foundation-models \
  --region ca-central-1 \
  --by-provider anthropic

# List inference profiles
aws bedrock list-inference-profiles \
  --region ca-central-1
```

**Regions with Claude 4.5 (as of Jan 2026):**
- us-east-1
- us-west-2
- ca-central-1
- eu-west-1
- eu-central-1
- ap-northeast-1
- ap-southeast-1
- ap-southeast-2

## Migration from Claude 3.x to 4.5

If you're migrating from Claude 3.x, you need to:

1. ✅ **Update model IDs** to use inference profiles
2. ✅ **Remove top_p** if you're also using temperature
3. ✅ **Increase timeout** to 60 minutes
4. ✅ **Enable model access** in AWS Bedrock Console
5. ✅ **Update IAM permissions** if needed

**Example Migration:**

```diff
// Before (Claude 3)
{
-  "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
+  "modelId": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "inferenceConfig": {
    "temperature": 0.7,
-    "topP": 0.9  // REMOVE THIS
  }
}
```

## Known Issues & Workarounds

### Issue 1: Both Temperature and Top_P Sent by Default

**Problem:** Many libraries send both parameters by default
**Solution:** Patch the library or use this transformer to filter

### Issue 2: Inference Profile Not Recognized

**Problem:** Using wrong region or model not enabled
**Solution:**
- Check model access in AWS Bedrock Console
- Verify inference profiles exist: `aws bedrock list-inference-profiles`

### Issue 3: Timeout on Long Responses

**Problem:** Default 60-second timeout too short
**Solution:** Set `requestTimeout` to 3600000ms (60 minutes)

## Testing Your Setup

Run the test script to verify everything works:

```bash
cd ~/apps/ai400/claude-code-router-bedrock
npm test
```

**Expected Output:**
```
✅ Response received!
   Model: global.anthropic.claude-sonnet-4-5-20250929-v1:0
   Stop reason: end_turn
   Input tokens: 24
   Output tokens: 31
```

## References

- [GitHub Issue: deepeval #2133](https://github.com/confident-ai/deepeval/issues/2133)
- [GitHub Issue: pipecat #2878](https://github.com/pipecat-ai/pipecat/issues/2878)
- [GitHub Issue: open-webui #17922](https://github.com/open-webui/open-webui/issues/17922)
- [AWS Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- [Anthropic Claude on Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html)

## Summary

The key takeaways:

1. **Use inference profiles** (global.* or us.*) for Claude 4.5
2. **Use temperature ONLY** (not top_p) for Claude 4.5
3. **Increase timeout** to 60 minutes
4. **Enable models** in AWS Bedrock Console first

These changes are **required** for Claude 4.5 models and represent breaking changes from Claude 3.x behavior.

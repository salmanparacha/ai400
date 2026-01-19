# Quick Start Guide

## 1. Enable Bedrock Access

First, ensure you have access to Claude models in AWS Bedrock:

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Model Access** (left sidebar)
3. Click **Request Model Access**
4. Select all **Anthropic Claude** models
5. Click **Request Model Access** (approval is usually instant)

## 2. Run Setup Script

```bash
cd ~/apps/ai400/claude-code-router-bedrock
./setup.sh
```

This will:
- Check Node.js version
- Verify AWS credentials
- Install dependencies
- Test the transformer with a real Bedrock request

## 3. Restart Claude Code Router

```bash
ccr stop
ccr start
```

## 4. Test with Claude Code

Now Claude Code will use Bedrock by default. The router configuration sets:

- **Default model**: `bedrock,claude-4-sonnet`
- **Thinking tasks**: `bedrock,claude-4-opus`
- **Background tasks**: `ollama,llama3.1:8b` (local)
- **Long context**: `bedrock,claude-4-sonnet`
- **Web search**: `bedrock,claude-3-5-sonnet`

### Switch Models

```bash
# Use the /model command in Claude Code
/model bedrock,claude-4-opus
/model bedrock,claude-3-5-sonnet
/model bedrock,claude-3-5-haiku

# Or use ccr CLI
ccr model list
ccr model switch bedrock,claude-4-sonnet
```

## Troubleshooting

### Test the Transformer

```bash
cd ~/apps/ai400/claude-code-router-bedrock
npm test
```

### Check Router Logs

```bash
tail -f ~/.claude-code-router/logs/ccr.log
```

### Verify AWS Credentials

```bash
# List AWS profiles
cat ~/.aws/credentials

# Test AWS access
aws bedrock list-foundation-models --region ca-central-1
```

### Common Issues

**1. AccessDeniedException**
- Add IAM permissions for `bedrock:InvokeModel`
- Example policy in README.md

**2. ResourceNotFoundException**
- Model not available in your region
- Try `us-east-1` or `us-west-2`
- Enable models in Bedrock Console

**3. CredentialsProviderError**
- Check `~/.aws/credentials` exists
- Verify credentials are valid
- Try: `aws sts get-caller-identity`

## Cost Optimization

- Use **Claude 3.5 Haiku** for simple tasks (cheapest)
- Use **Claude 4 Sonnet** for most coding tasks (balanced)
- Use **Claude 4 Opus** only for complex reasoning (most expensive)

Current configuration already uses local Ollama for background tasks to save costs.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- Explore the [transformer code](transformers/bedrock-transformer.js)
- Customize your [router configuration](~/.claude-code-router/config.json)

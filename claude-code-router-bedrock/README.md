# AWS Bedrock Transformer for Claude Code Router

This custom transformer enables **Claude Code** to use **AWS Bedrock's Claude models** through the **claude-code-router**.

## Features

- ✅ Full compatibility with AWS Bedrock Converse API
- ✅ AWS Signature V4 authentication using your AWS credentials
- ✅ Support for all Claude models (Claude 4, Claude 3.5, Claude 3)
- ✅ Tool use (function calling) support
- ✅ Streaming and non-streaming responses
- ✅ Friendly model name mappings
- ✅ Automatic credential loading from AWS config

## Prerequisites

1. **Node.js** 18+ installed
2. **AWS Account** with Bedrock access
3. **Claude Code Router** installed and configured
4. **AWS CLI** configured with credentials (or AWS credentials in `~/.aws/credentials`)

### AWS Bedrock Setup

1. **Enable Claude models in AWS Bedrock:**
   - Go to AWS Bedrock Console → Model Access
   - Request access to Anthropic Claude models
   - Wait for approval (usually instant for most regions)

2. **IAM Permissions:**
   Your AWS user/role needs these permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream"
         ],
         "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
       }
     ]
   }
   ```

3. **AWS Credentials:**
   Ensure your credentials are configured in `~/.aws/credentials`:
   ```ini
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   region = us-east-1
   ```

## Installation

### 1. Install Dependencies

```bash
cd ~/apps/ai400/claude-code-router-bedrock
npm install
```

### 2. Test the Transformer

Run the test script to verify everything is configured correctly:

```bash
npm test
```

This will:
- Load your AWS credentials
- Make a test request to Bedrock
- Display the response
- Show any configuration issues

### 3. Update Claude Code Router Configuration

Add the Bedrock provider to your `~/.claude-code-router/config.json`:

```json
{
  "LOG": true,
  "LOG_LEVEL": "debug",
  "NON_INTERACTIVE_MODE": true,
  "HOST": "127.0.0.1",
  "PORT": 3456,
  "API_TIMEOUT_MS": 600000,
  "Providers": [
    {
      "name": "bedrock",
      "api_base_url": "https://bedrock-runtime.us-east-1.amazonaws.com",
      "api_key": "bedrock",
      "models": [
        "claude-4-opus",
        "claude-4-sonnet",
        "claude-3-5-sonnet",
        "claude-3-5-haiku"
      ],
      "transformer": {
        "use": [
          ["custom", {
            "path": "/home/sparacha/apps/ai400/claude-code-router-bedrock/transformers/bedrock-transformer.js",
            "region": "us-east-1",
            "profile": "default"
          }]
        ]
      }
    }
  ],
  "Router": {
    "default": "bedrock,claude-4-sonnet",
    "background": "bedrock,claude-3-5-haiku",
    "think": "bedrock,claude-4-opus",
    "longContext": "bedrock,claude-4-sonnet",
    "longContextThreshold": 60000,
    "webSearch": "bedrock,claude-3-5-sonnet"
  }
}
```

### 4. Restart Claude Code Router

```bash
# Stop the router
ccr stop

# Start it again to load the new configuration
ccr start
```

## Usage

Once configured, Claude Code will automatically use Bedrock models through the router.

### Available Models

The transformer supports friendly names that map to Bedrock model IDs:

| Friendly Name | Bedrock Model ID |
|--------------|------------------|
| `claude-4-opus` | `anthropic.claude-opus-4-20250514-v1:0` |
| `claude-4-sonnet` | `anthropic.claude-sonnet-4-20250514-v1:0` |
| `claude-3-5-sonnet` | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `claude-3-5-haiku` | `anthropic.claude-3-5-haiku-20241022-v1:0` |
| `claude-3-opus` | `anthropic.claude-3-opus-20240229-v1:0` |
| `claude-3-sonnet` | `anthropic.claude-3-sonnet-20240229-v1:0` |
| `claude-3-haiku` | `anthropic.claude-3-haiku-20240307-v1:0` |

You can also use the full Bedrock model IDs directly in your configuration.

### Switching Models

Use the `/model` command in Claude Code:

```bash
# Switch to Claude 4 Opus
/model bedrock,claude-4-opus

# Switch to Claude 3.5 Sonnet
/model bedrock,claude-3-5-sonnet
```

Or use the `ccr model` CLI command:

```bash
# List available models
ccr model list

# Switch model
ccr model switch bedrock,claude-4-sonnet
```

## Configuration Options

The transformer accepts these configuration options:

```json
{
  "transformer": {
    "use": [
      ["custom", {
        "path": "/path/to/bedrock-transformer.js",
        "region": "us-east-1",      // AWS region (default: from AWS_REGION or 'us-east-1')
        "profile": "default"         // AWS profile name (default: from AWS_PROFILE or 'default')
      }]
    ]
  }
}
```

### Environment Variables

You can also set these environment variables:

```bash
export AWS_REGION=us-west-2
export AWS_PROFILE=my-profile
```

## Supported Features

### ✅ Text Generation
Standard text generation works out of the box.

### ✅ Tool Use (Function Calling)
The transformer fully supports Claude's tool use:

```javascript
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get weather for a location",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": { "type": "string" }
        },
        "required": ["location"]
      }
    }
  ]
}
```

### ✅ Image Input
Send images to vision-capable models:

```javascript
{
  "content": [
    {
      "type": "image",
      "source": {
        "type": "base64",
        "media_type": "image/jpeg",
        "data": "base64_encoded_image_data"
      }
    },
    {
      "type": "text",
      "text": "What's in this image?"
    }
  ]
}
```

### ✅ Streaming
The transformer handles streaming responses automatically when Claude Code requests them.

## Troubleshooting

### CredentialsProviderError

**Error:** Cannot load AWS credentials

**Solution:**
- Check that `~/.aws/credentials` exists and has valid credentials
- Or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables
- Or ensure your AWS profile is set correctly

### AccessDeniedException

**Error:** User is not authorized to perform: bedrock:InvokeModel

**Solution:**
- Add the required IAM permissions (see Prerequisites)
- Ensure your IAM user/role has `bedrock:InvokeModel` permission

### ResourceNotFoundException

**Error:** Model not found

**Solution:**
- Check that the model is available in your region
- Enable the model in AWS Bedrock Console → Model Access
- Try a different region (us-east-1 or us-west-2 have the most models)

### Model Access Not Enabled

**Error:** You don't have access to the model

**Solution:**
- Go to AWS Bedrock Console → Model Access
- Request access to Anthropic Claude models
- Wait for approval (usually instant)

## Cost Considerations

AWS Bedrock charges per token. Current pricing (as of January 2026):

- **Claude 4 Opus**: ~$15/$75 per 1M tokens (input/output)
- **Claude 4 Sonnet**: ~$3/$15 per 1M tokens (input/output)
- **Claude 3.5 Sonnet**: ~$3/$15 per 1M tokens (input/output)
- **Claude 3.5 Haiku**: ~$0.25/$1.25 per 1M tokens (input/output)

Check [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) for current rates.

## Architecture

```
┌─────────────┐
│ Claude Code │
└──────┬──────┘
       │ Anthropic Messages API format
       │
┌──────▼───────────────┐
│ Claude Code Router   │
│ (localhost:3456)     │
└──────┬───────────────┘
       │
┌──────▼──────────────────┐
│ Bedrock Transformer     │
│ - Format conversion     │
│ - AWS authentication    │
│ - Request signing       │
└──────┬──────────────────┘
       │ Bedrock Converse API format
       │ + AWS Signature V4
       │
┌──────▼──────────────┐
│ AWS Bedrock API     │
│ Claude Models       │
└─────────────────────┘
```

## Development

### Project Structure

```
claude-code-router-bedrock/
├── transformers/
│   └── bedrock-transformer.js    # Main transformer logic
├── examples/
│   ├── config-example.json       # Example configuration
│   └── test-transformer.js       # Test script
├── package.json
└── README.md
```

### Running Tests

```bash
# Test the transformer
npm test

# Test with specific AWS profile
AWS_PROFILE=my-profile npm test

# Test with specific region
AWS_REGION=us-west-2 npm test
```

## Contributing

Contributions are welcome! This transformer can be:
- Improved with additional features
- Optimized for better performance
- Extended to support more Bedrock features
- Contributed back to the claude-code-router project

## License

MIT

## Support

For issues related to:
- **Transformer code**: Open an issue in this repository
- **Claude Code Router**: See [musistudio/claude-code-router](https://github.com/musistudio/claude-code-router)
- **AWS Bedrock**: Check [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- **Claude API**: See [Anthropic Documentation](https://docs.anthropic.com/)

## References

- [Claude Code Router GitHub](https://github.com/musistudio/claude-code-router)
- [AWS Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- [Anthropic Claude Models on Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html)
- [Bedrock Converse API Examples](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-examples.html)

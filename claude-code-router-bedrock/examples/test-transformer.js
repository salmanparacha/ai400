/**
 * Test script for Bedrock Transformer
 *
 * This script tests the transformer with a simple request to verify:
 * 1. Request transformation works correctly
 * 2. AWS credentials are properly loaded
 * 3. Response transformation works correctly
 */

const { BedrockTransformer } = require('../transformers/bedrock-transformer.js');

async function testTransformer() {
  console.log('🧪 Testing Bedrock Transformer...\n');

  // Initialize transformer
  // Read region from AWS config if available
  let defaultRegion = 'us-east-1';
  try {
    const fs = require('fs');
    const configPath = require('path').join(require('os').homedir(), '.aws', 'config');
    if (fs.existsSync(configPath)) {
      const configContent = fs.readFileSync(configPath, 'utf8');
      const regionMatch = configContent.match(/region\s*=\s*(\S+)/);
      if (regionMatch) {
        defaultRegion = regionMatch[1];
      }
    }
  } catch (e) {
    // Ignore errors, use default
  }

  const config = {
    region: process.env.AWS_REGION || defaultRegion,
    profile: process.env.AWS_PROFILE || 'default'
  };

  const transformer = new BedrockTransformer(config);
  console.log('✅ Transformer initialized');
  console.log(`   Region: ${transformer.region}`);
  console.log(`   Profile: ${transformer.profile}\n`);

  // Test model ID mapping
  console.log('🔄 Testing model ID mapping:');
  const testModels = [
    'claude-4-sonnet',
    'claude-4-opus',
    'claude-3-5-sonnet',
    'anthropic.claude-opus-4-20250514-v1:0'
  ];

  testModels.forEach(model => {
    const mapped = transformer.getModelId(model);
    console.log(`   ${model} → ${mapped}`);
  });
  console.log();

  // Create a test request (Anthropic Messages API format)
  const testRequest = {
    model: 'claude-4-sonnet',
    max_tokens: 1024,
    temperature: 1.0,
    system: 'You are a helpful AI assistant.',
    messages: [
      {
        role: 'user',
        content: 'Hello! Can you tell me a short joke?'
      }
    ]
  };

  console.log('📤 Test Request (Anthropic format):');
  console.log(JSON.stringify(testRequest, null, 2));
  console.log();

  try {
    console.log('🚀 Sending request to AWS Bedrock...');
    const response = await transformer.transform(testRequest, config);

    console.log('✅ Response received!\n');
    console.log('📥 Response (Anthropic format):');
    console.log(JSON.stringify(response, null, 2));
    console.log();

    console.log('✨ Test completed successfully!');
    console.log(`   Model: ${response.model}`);
    console.log(`   Stop reason: ${response.stop_reason}`);
    console.log(`   Input tokens: ${response.usage.input_tokens}`);
    console.log(`   Output tokens: ${response.usage.output_tokens}`);

  } catch (error) {
    console.error('❌ Test failed:');
    console.error(`   Error: ${error.message}`);
    console.error();

    if (error.name === 'CredentialsProviderError') {
      console.error('💡 Tip: Make sure your AWS credentials are configured:');
      console.error('   - Check ~/.aws/credentials file');
      console.error('   - Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables');
      console.error('   - Or set AWS_PROFILE environment variable');
    } else if (error.name === 'AccessDeniedException') {
      console.error('💡 Tip: Your AWS credentials don\'t have access to Bedrock:');
      console.error('   - Ensure your IAM user/role has bedrock:InvokeModel permission');
      console.error('   - Check that you have access to the specific model');
    } else if (error.code === 'ResourceNotFoundException') {
      console.error('💡 Tip: The model might not be available in your region:');
      console.error(`   - Current region: ${config.region}`);
      console.error('   - Try a different region like us-east-1 or us-west-2');
      console.error('   - Ensure the model is enabled in your AWS Bedrock console');
    }

    process.exit(1);
  }
}

// Run the test
testTransformer().catch(error => {
  console.error('Unhandled error:', error);
  process.exit(1);
});

#!/usr/bin/env node
/**
 * Test Tool Use Workflow
 * Tests the complete tool use cycle through the proxy
 */

const http = require('http');

function makeRequest(data) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(data);

    const options = {
      hostname: 'localhost',
      port: 3456,
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': 'test',
        'anthropic-version': '2023-06-01',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error(`Parse error: ${body}`));
        }
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function testToolUse() {
  console.log('🧪 Testing Tool Use Workflow\n');

  // Test 1: Request with tool definition
  console.log('Test 1: Claude receives tool definition and uses it');
  const response1 = await makeRequest({
    model: 'bedrock/sonnet',
    max_tokens: 200,
    messages: [{
      role: 'user',
      content: 'What is the weather in Paris? Use the get_weather tool.'
    }],
    tools: [{
      name: 'get_weather',
      description: 'Get current weather for a location',
      input_schema: {
        type: 'object',
        properties: {
          location: { type: 'string', description: 'City name' },
          unit: { type: 'string', enum: ['celsius', 'fahrenheit'] }
        },
        required: ['location']
      }
    }]
  });

  console.log('Response:', JSON.stringify(response1, null, 2));

  // Check if tool was used
  const usedTool = response1.content?.find(block => block.type === 'tool_use');
  if (usedTool) {
    console.log('✅ Claude requested tool use:', usedTool.name);
    console.log('   Tool ID:', usedTool.id);
    console.log('   Input:', JSON.stringify(usedTool.input, null, 2));

    // Test 2: Send tool result back
    console.log('\nTest 2: Sending tool result back to Claude');
    const response2 = await makeRequest({
      model: 'bedrock/sonnet',
      max_tokens: 200,
      messages: [
        {
          role: 'user',
          content: 'What is the weather in Paris?'
        },
        {
          role: 'assistant',
          content: response1.content
        },
        {
          role: 'user',
          content: [{
            type: 'tool_result',
            tool_use_id: usedTool.id,
            content: 'The weather in Paris is 18°C, partly cloudy with light winds.'
          }]
        }
      ],
      tools: [{
        name: 'get_weather',
        description: 'Get current weather for a location',
        input_schema: {
          type: 'object',
          properties: {
            location: { type: 'string' },
            unit: { type: 'string', enum: ['celsius', 'fahrenheit'] }
          },
          required: ['location']
        }
      }]
    });

    console.log('Response:', JSON.stringify(response2, null, 2));

    const finalText = response2.content?.find(block => block.type === 'text');
    if (finalText) {
      console.log('✅ Claude processed tool result successfully');
      console.log('   Final response:', finalText.text);
    } else {
      console.log('❌ No text response after tool result');
    }

  } else {
    console.log('⚠️  Claude did not use the tool');
    console.log('   Response:', response1.content);
  }

  console.log('\n✨ Tool use workflow test complete!');
}

testToolUse().catch(error => {
  console.error('❌ Test failed:', error.message);
  process.exit(1);
});

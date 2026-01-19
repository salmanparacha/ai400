/**
 * Local Proxy Server for AWS Bedrock
 *
 * This server acts as an HTTP proxy that claude-code-router can call.
 * It receives Anthropic Messages API requests and forwards them to AWS Bedrock.
 * Returns OpenAI format so claude-code-router can convert it properly.
 */

const http = require('http');
const { BedrockTransformer } = require('./transformers/bedrock-transformer.js');

const PORT = 3457;
const HOST = '127.0.0.1';

// Initialize the Bedrock transformer
const config = {
  region: process.env.AWS_REGION || 'ca-central-1',
  profile: process.env.AWS_PROFILE || 'default'
};

const transformer = new BedrockTransformer(config);

function openAiToAnthropic(openAiRequest) {
  const messages = Array.isArray(openAiRequest.messages) ? openAiRequest.messages : [];
  const systemParts = [];
  const anthropicMessages = [];

  for (const msg of messages) {
    if (!msg || !msg.role) {
      continue;
    }

    if (msg.role === 'system') {
      if (typeof msg.content === 'string') {
        systemParts.push(msg.content);
      } else if (Array.isArray(msg.content)) {
        systemParts.push(msg.content.map(part => part.text || '').join(''));
      }
      continue;
    }

    if (msg.role === 'tool') {
      const toolContent = typeof msg.content === 'string' && msg.content.trim().length > 0
        ? msg.content
        : '[empty]';
      anthropicMessages.push({
        role: 'user',
        content: [{
          type: 'tool_result',
          tool_use_id: msg.tool_call_id,
          content: toolContent,
          is_error: false
        }]
      });
      continue;
    }

    if (msg.role === 'assistant') {
      const contentBlocks = [];
      if (typeof msg.content === 'string') {
        const text = msg.content.trim();
        if (text.length > 0) {
          contentBlocks.push({ type: 'text', text: msg.content });
        }
      } else if (Array.isArray(msg.content)) {
        for (const part of msg.content) {
          if (part.type === 'text') {
            const text = (part.text || '').trim();
            if (text.length > 0) {
              contentBlocks.push({ type: 'text', text: part.text });
            }
          }
        }
      }

      if (Array.isArray(msg.tool_calls)) {
        for (const call of msg.tool_calls) {
          if (call && call.type === 'function') {
            let input = {};
            try {
              input = call.function?.arguments ? JSON.parse(call.function.arguments) : {};
            } catch {
              input = {};
            }
            contentBlocks.push({
              type: 'tool_use',
              id: call.id,
              name: call.function?.name || '',
              input
            });
          }
        }
      }

      if (contentBlocks.length > 0) {
        anthropicMessages.push({
          role: 'assistant',
          content: contentBlocks
        });
      }
      continue;
    }

    if (msg.role === 'user') {
      if (typeof msg.content === 'string') {
        const text = msg.content.trim();
        anthropicMessages.push({ role: 'user', content: text.length > 0 ? msg.content : '[empty]' });
      } else if (Array.isArray(msg.content)) {
        const contentBlocks = [];
        for (const part of msg.content) {
          if (part.type === 'text') {
            const text = (part.text || '').trim();
            if (text.length > 0) {
              contentBlocks.push({ type: 'text', text: part.text });
            }
          } else if (part.type === 'image_url' && part.image_url?.url) {
            const dataUrl = part.image_url.url;
            const match = dataUrl.match(/^data:(.+);base64,(.+)$/);
            if (match) {
              contentBlocks.push({
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: match[1],
                  data: match[2]
                }
              });
            }
          }
        }
        if (contentBlocks.length > 0) {
          anthropicMessages.push({ role: 'user', content: contentBlocks });
        } else {
          anthropicMessages.push({ role: 'user', content: '[empty]' });
        }
      } else {
        const text = String(msg.content || '').trim();
        anthropicMessages.push({ role: 'user', content: text.length > 0 ? text : '[empty]' });
      }
    }
  }

  const tools = Array.isArray(openAiRequest.tools)
    ? openAiRequest.tools
        .filter(tool => tool && tool.type === 'function' && tool.function?.name)
        .map(tool => ({
          name: tool.function.name,
          description: tool.function.description || '',
          input_schema: tool.function.parameters || {}
        }))
    : undefined;

  let toolChoice;
  if (openAiRequest.tool_choice) {
    if (typeof openAiRequest.tool_choice === 'string') {
      if (openAiRequest.tool_choice === 'required') {
        toolChoice = { type: 'any' };
      } else if (openAiRequest.tool_choice === 'none') {
        toolChoice = undefined;
      } else {
        toolChoice = { type: openAiRequest.tool_choice };
      }
    } else if (openAiRequest.tool_choice.type === 'function') {
      toolChoice = { type: 'tool', name: openAiRequest.tool_choice.function?.name };
    } else if (openAiRequest.tool_choice.type === 'tool') {
      toolChoice = { type: 'tool', name: openAiRequest.tool_choice.name };
    }
  } else if (Array.isArray(openAiRequest.tools) && openAiRequest.tools.length > 0) {
    toolChoice = { type: 'auto' };
  }

  let stopSequences;
  if (Array.isArray(openAiRequest.stop)) {
    stopSequences = openAiRequest.stop;
  } else if (typeof openAiRequest.stop === 'string') {
    stopSequences = [openAiRequest.stop];
  }

  return {
    model: openAiRequest.model,
    messages: anthropicMessages,
    system: systemParts.length > 0 ? systemParts.join('\n\n') : undefined,
    max_tokens: openAiRequest.max_tokens,
    temperature: openAiRequest.temperature,
    top_p: openAiRequest.top_p,
    stop_sequences: stopSequences,
    tools,
    tool_choice: toolChoice,
    stream: openAiRequest.stream === true
  };
}

/**
 * Convert Anthropic response to OpenAI format
 * The router will then convert it back to Anthropic format for Claude Code
 */
function anthropicToOpenAI(anthropicResponse) {
  // Extract text content and tool calls
  let content = '';
  const toolCalls = [];

  if (anthropicResponse.content && Array.isArray(anthropicResponse.content)) {
    for (const block of anthropicResponse.content) {
      if (block.type === 'text') {
        content += block.text;
      } else if (block.type === 'tool_use') {
        toolCalls.push({
          id: block.id,
          type: 'function',
          function: {
            name: block.name,
            arguments: JSON.stringify(block.input)
          }
        });
      }
    }
  }

  // Map stop reasons
  const finishReasonMap = {
    'end_turn': 'stop',
    'max_tokens': 'length',
    'tool_use': 'tool_calls',
    'stop_sequence': 'stop'
  };

  const message = {
    role: 'assistant',
    content: content
  };

  // Add tool calls if present
  if (toolCalls.length > 0) {
    message.tool_calls = toolCalls;
  }

  // Build OpenAI format response
  return {
    id: anthropicResponse.id,
    object: 'chat.completion',
    created: Math.floor(Date.now() / 1000),
    model: anthropicResponse.model,
    choices: [
      {
        index: 0,
        message: message,
        finish_reason: finishReasonMap[anthropicResponse.stop_reason] || 'stop'
      }
    ],
    usage: {
      prompt_tokens: anthropicResponse.usage?.input_tokens || 0,
      completion_tokens: anthropicResponse.usage?.output_tokens || 0,
      total_tokens: (anthropicResponse.usage?.input_tokens || 0) + (anthropicResponse.usage?.output_tokens || 0)
    }
  };
}

function writeSse(res, data) {
  res.write(`data: ${JSON.stringify(data)}\n\n`);
}

function chunkFromAnthropic(anthropicResponse, responseId, model) {
  const toolCalls = [];
  let content = '';

  if (anthropicResponse.content && Array.isArray(anthropicResponse.content)) {
    for (const block of anthropicResponse.content) {
      if (block.type === 'text') {
        content += block.text;
      } else if (block.type === 'tool_use') {
        toolCalls.push({
          id: block.id,
          type: 'function',
          function: {
            name: block.name,
            arguments: JSON.stringify(block.input)
          }
        });
      }
    }
  }

  const finishReasonMap = {
    'end_turn': 'stop',
    'max_tokens': 'length',
    'tool_use': 'tool_calls',
    'stop_sequence': 'stop'
  };

  return {
    content,
    toolCalls,
    finishReason: finishReasonMap[anthropicResponse.stop_reason] || 'stop',
    model: model || anthropicResponse.model || 'claude-bedrock',
    id: responseId
  };
}

async function streamAnthropicToOpenAI(res, streamResult) {
  const responseId = `chatcmpl_${Date.now()}`;
  const model = 'claude-bedrock';
  const toolCallsByIndex = new Map();
  let sentRole = false;

  for await (const event of streamResult.stream) {
    const anthropicEvent = streamResult.transformStreamEvent(event);
    if (!anthropicEvent) {
      continue;
    }

    if (anthropicEvent.type === 'message_start') {
      if (!sentRole) {
        writeSse(res, {
          id: responseId,
          object: 'chat.completion.chunk',
          created: Math.floor(Date.now() / 1000),
          model,
          choices: [{ index: 0, delta: { role: 'assistant' }, finish_reason: null }]
        });
        sentRole = true;
      }
      continue;
    }

    if (anthropicEvent.type === 'content_block_start' && anthropicEvent.content_block?.type === 'tool_use') {
      const index = anthropicEvent.index;
      toolCallsByIndex.set(index, {
        id: anthropicEvent.content_block.id,
        name: anthropicEvent.content_block.name
      });
      continue;
    }

    if (anthropicEvent.type === 'content_block_delta') {
      if (anthropicEvent.delta?.type === 'text_delta') {
        writeSse(res, {
          id: responseId,
          object: 'chat.completion.chunk',
          created: Math.floor(Date.now() / 1000),
          model,
          choices: [{ index: 0, delta: { content: anthropicEvent.delta.text }, finish_reason: null }]
        });
      } else if (anthropicEvent.delta?.type === 'input_json_delta') {
        const tool = toolCallsByIndex.get(anthropicEvent.index) || {};
        writeSse(res, {
          id: responseId,
          object: 'chat.completion.chunk',
          created: Math.floor(Date.now() / 1000),
          model,
          choices: [{
            index: 0,
            delta: {
              tool_calls: [{
                index: anthropicEvent.index,
                id: tool.id,
                type: 'function',
                function: {
                  name: tool.name,
                  arguments: anthropicEvent.delta.partial_json || ''
                }
              }]
            },
            finish_reason: null
          }]
        });
      }
      continue;
    }

    if (anthropicEvent.type === 'message_delta') {
      const finishReasonMap = {
        'end_turn': 'stop',
        'max_tokens': 'length',
        'tool_use': 'tool_calls',
        'stop_sequence': 'stop'
      };
      writeSse(res, {
        id: responseId,
        object: 'chat.completion.chunk',
        created: Math.floor(Date.now() / 1000),
        model,
        choices: [{ index: 0, delta: {}, finish_reason: finishReasonMap[anthropicEvent.delta?.stop_reason] || 'stop' }]
      });
    }
  }

  res.write('data: [DONE]\n\n');
  res.end();
}

const server = http.createServer(async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-api-key, anthropic-version');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Only handle POST requests to /v1/messages
  if (req.method !== 'POST' || !req.url.includes('/messages')) {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
    return;
  }

  let body = '';
  req.on('data', chunk => {
    body += chunk.toString();
  });

  req.on('end', async () => {
    try {
      const openAiRequest = JSON.parse(body);
      const anthropicRequest = openAiToAnthropic(openAiRequest);

      console.log('📥 Received request for model:', anthropicRequest.model);

      let anthropicResponse;
      if (anthropicRequest.stream) {
        const nonStreamingRequest = { ...anthropicRequest, stream: false };
        anthropicResponse = await transformer.transform(nonStreamingRequest, config);

        res.writeHead(200, {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          'X-Accel-Buffering': 'no'
        });
        if (typeof res.flushHeaders === 'function') {
          res.flushHeaders();
        }

        const responseId = `chatcmpl_${Date.now()}`;
        const chunk = chunkFromAnthropic(anthropicResponse, responseId, anthropicResponse.model);

        writeSse(res, {
          id: responseId,
          object: 'chat.completion.chunk',
          created: Math.floor(Date.now() / 1000),
          model: chunk.model,
          choices: [{ index: 0, delta: { role: 'assistant' }, finish_reason: null }]
        });

        if (chunk.content) {
          writeSse(res, {
            id: responseId,
            object: 'chat.completion.chunk',
            created: Math.floor(Date.now() / 1000),
            model: chunk.model,
            choices: [{ index: 0, delta: { content: chunk.content }, finish_reason: null }]
          });
        }

        if (chunk.toolCalls.length > 0) {
          writeSse(res, {
            id: responseId,
            object: 'chat.completion.chunk',
            created: Math.floor(Date.now() / 1000),
            model: chunk.model,
            choices: [{ index: 0, delta: { tool_calls: chunk.toolCalls }, finish_reason: null }]
          });
        }

        writeSse(res, {
          id: responseId,
          object: 'chat.completion.chunk',
          created: Math.floor(Date.now() / 1000),
          model: chunk.model,
          choices: [{ index: 0, delta: {}, finish_reason: chunk.finishReason }]
        });

        res.write('data: [DONE]\n\n');
        res.end();
        return;
      }

      // Transform and send to Bedrock (non-streaming)
      anthropicResponse = await transformer.transform(anthropicRequest, config);

      console.log('✅ Response from Bedrock:', {
        model: anthropicResponse.model,
        stop_reason: anthropicResponse.stop_reason,
        tokens: anthropicResponse.usage
      });

      // Convert to OpenAI format for claude-code-router
      const openaiResponse = anthropicToOpenAI(anthropicResponse);

      console.log('🔄 Converted to OpenAI format for router');

      // Return OpenAI-formatted response
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(openaiResponse));

    } catch (error) {
      console.error('❌ Error:', error.message);

      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        error: {
          type: 'api_error',
          message: error.message
        }
      }));
    }
  });
});

server.listen(PORT, HOST, () => {
  console.log(`🚀 Bedrock Proxy Server running at http://${HOST}:${PORT}`);
  console.log(`   Region: ${config.region}`);
  console.log(`   Profile: ${config.profile}`);
  console.log(`   Format: OpenAI → Router → Anthropic`);
  console.log(`\nUpdate your claude-code-router config to use:`);
  console.log(`   "api_base_url": "http://127.0.0.1:${PORT}/v1/messages"\n`);
});

// Handle shutdown gracefully
process.on('SIGTERM', () => {
  console.log('\n👋 Shutting down proxy server...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});

/**
 * AWS Bedrock Transformer for Claude Code Router
 *
 * Transforms Anthropic Messages API format to AWS Bedrock Converse API format
 * Handles AWS Signature V4 authentication
 * Supports tool use (function calling) and streaming
 */

const { BedrockRuntimeClient, ConverseCommand, ConverseStreamCommand } = require('@aws-sdk/client-bedrock-runtime');
const { fromIni } = require('@aws-sdk/credential-providers');

class BedrockTransformer {
  constructor(config) {
    this.config = config || {};
    this.region = this.config.region || process.env.AWS_REGION || 'us-east-1';
    this.profile = this.config.profile || process.env.AWS_PROFILE || 'default';

    // Initialize Bedrock client with credentials from AWS config
    this.client = new BedrockRuntimeClient({
      region: this.region,
      credentials: fromIni({ profile: this.profile })
    });

    // Model ID mappings for AWS Bedrock
    // Note: Claude 4.5 models require inference profile IDs (global. prefix)
    // Claude 3 models can use direct model IDs
    this.modelMappings = {
      // Claude 4.5 models (latest) - using global inference profiles
      'claude-4.5-opus': 'global.anthropic.claude-opus-4-5-20251101-v1:0',
      'claude-4.5-sonnet': 'global.anthropic.claude-sonnet-4-5-20250929-v1:0',
      'claude-4.5-haiku': 'global.anthropic.claude-haiku-4-5-20251001-v1:0',
      // Raw Claude Code model IDs
      'claude-opus-4-5-20251101': 'global.anthropic.claude-opus-4-5-20251101-v1:0',
      'claude-sonnet-4-5-20250929': 'global.anthropic.claude-sonnet-4-5-20250929-v1:0',
      'claude-haiku-4-5-20251001': 'global.anthropic.claude-haiku-4-5-20251001-v1:0',
      // Aliases for convenience
      'claude-4-opus': 'global.anthropic.claude-opus-4-5-20251101-v1:0',
      'claude-4-sonnet': 'global.anthropic.claude-sonnet-4-5-20250929-v1:0',
      'claude-4-haiku': 'global.anthropic.claude-haiku-4-5-20251001-v1:0',
      'opus': 'global.anthropic.claude-opus-4-5-20251101-v1:0',
      'sonnet': 'global.anthropic.claude-sonnet-4-5-20250929-v1:0',
      'haiku': 'global.anthropic.claude-haiku-4-5-20251001-v1:0',
      // US-specific inference profiles (if needed)
      'us-opus': 'us.anthropic.claude-opus-4-5-20251101-v1:0',
      'us-sonnet': 'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
      'us-haiku': 'us.anthropic.claude-haiku-4-5-20251001-v1:0',
      // Claude 3 models (direct model IDs)
      'claude-3-sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
      'claude-3-haiku': 'anthropic.claude-3-haiku-20240307-v1:0'
    };
  }

  /**
   * Get the Bedrock model ID from a friendly name or pass through if already a full ID
   */
  getModelId(model) {
    // If it's already a Bedrock model ID, return as-is
    if (model.startsWith('anthropic.')) {
      return model;
    }
    // Otherwise, look up the mapping
    return this.modelMappings[model] || model;
  }

  /**
   * Transform Anthropic Messages API content to Bedrock Converse API format
   */
  transformContent(content) {
    if (typeof content === 'string') {
      return [{ text: content }];
    }

    if (Array.isArray(content)) {
      return content.map(block => {
        if (block.type === 'text') {
          return { text: block.text };
        } else if (block.type === 'image') {
          return {
            image: {
              format: block.source.media_type.split('/')[1], // e.g., 'jpeg' from 'image/jpeg'
              source: {
                bytes: Buffer.from(block.source.data, 'base64')
              }
            }
          };
        } else if (block.type === 'tool_use') {
          return {
            toolUse: {
              toolUseId: block.id,
              name: block.name,
              input: block.input
            }
          };
        } else if (block.type === 'tool_result') {
          return {
            toolResult: {
              toolUseId: block.tool_use_id,
              content: typeof block.content === 'string'
                ? [{ text: block.content }]
                : this.transformContent(block.content),
              status: block.is_error ? 'error' : 'success'
            }
          };
        }
        return block;
      });
    }

    return [{ text: String(content) }];
  }

  /**
   * Transform Anthropic messages to Bedrock conversation format
   * CRITICAL: Bedrock only accepts "user" and "assistant" roles
   * Any "system" role messages must be filtered out (handled separately)
   */
  transformMessages(messages) {
    return messages
      .filter(msg => msg.role === 'user' || msg.role === 'assistant')
      .map(msg => ({
        role: msg.role,
        content: this.transformContent(msg.content)
      }));
  }

  /**
   * Extract system messages from messages array
   * Returns null if no system messages found
   */
  extractSystemFromMessages(messages) {
    const systemMessages = messages.filter(msg => msg.role === 'system');
    if (systemMessages.length === 0) {
      return null;
    }

    // Combine all system message content
    const systemText = systemMessages
      .map(msg => {
        if (typeof msg.content === 'string') {
          return msg.content;
        } else if (Array.isArray(msg.content)) {
          return msg.content
            .filter(block => block.type === 'text' || typeof block === 'string')
            .map(block => typeof block === 'string' ? block : block.text)
            .join('\n');
        }
        return '';
      })
      .filter(text => text.length > 0)
      .join('\n\n');

    return systemText.length > 0 ? systemText : null;
  }

  /**
   * Transform Anthropic tool_choice to Bedrock toolChoice
   */
  transformToolChoice(toolChoice) {
    if (!toolChoice) {
      return undefined;
    }

    // Handle different tool_choice formats
    if (typeof toolChoice === 'string') {
      if (toolChoice === 'none') {
        return undefined;
      }
      if (toolChoice === 'auto') {
        return { auto: {} };
      }
      if (toolChoice === 'any') {
        return { any: {} };
      }
      return undefined;
    }

    if (typeof toolChoice === 'object') {
      if (toolChoice.type === 'none' || !toolChoice.type) {
        return undefined;
      }
      if (toolChoice.type === 'auto') {
        return { auto: {} };
      }
      if (toolChoice.type === 'any') {
        return { any: {} };
      }
      if (toolChoice.type === 'tool' && toolChoice.name) {
        return { tool: { name: toolChoice.name } };
      }
      return undefined;
    }

    return undefined;
  }

  /**
   * Transform Anthropic tools to Bedrock tool configuration
   */
  transformTools(tools) {
    if (!tools || tools.length === 0) {
      return undefined;
    }

    // Filter out null/undefined tools and validate required fields
    const validTools = tools.filter(tool =>
      tool &&
      tool.name &&
      typeof tool.name === 'string' &&
      tool.input_schema
    );

    if (validTools.length === 0) {
      return undefined;
    }

    return {
      tools: validTools.map(tool => ({
        toolSpec: {
          name: tool.name,
          description: tool.description || '',
          inputSchema: {
            json: tool.input_schema
          }
        }
      }))
    };
  }

  /**
   * Transform Bedrock response back to Anthropic Messages API format
   */
  transformResponse(bedrockResponse) {
    const output = bedrockResponse.output;

    if (!output || !output.message) {
      throw new Error('Invalid Bedrock response: missing output.message');
    }

    const message = output.message;
    const content = [];

    // Transform content blocks
    if (message.content) {
      for (const block of message.content) {
        if (block.text) {
          content.push({
            type: 'text',
            text: block.text
          });
        } else if (block.toolUse) {
          content.push({
            type: 'tool_use',
            id: block.toolUse.toolUseId,
            name: block.toolUse.name,
            input: block.toolUse.input
          });
        }
      }
    }

    // Build Anthropic-style response
    return {
      id: `msg_${Date.now()}`,
      type: 'message',
      role: 'assistant',
      content: content,
      model: bedrockResponse.$metadata?.httpHeaders?.['x-amzn-bedrock-model-id'] ||
             bedrockResponse.modelId ||
             'claude-bedrock',
      stop_reason: this.mapStopReason(bedrockResponse.stopReason),
      stop_sequence: null,
      usage: {
        input_tokens: bedrockResponse.usage?.inputTokens || 0,
        output_tokens: bedrockResponse.usage?.outputTokens || 0
      }
    };
  }

  /**
   * Map Bedrock stop reasons to Anthropic format
   */
  mapStopReason(bedrockStopReason) {
    const mapping = {
      'end_turn': 'end_turn',
      'tool_use': 'tool_use',
      'max_tokens': 'max_tokens',
      'stop_sequence': 'stop_sequence',
      'content_filtered': 'end_turn'
    };
    return mapping[bedrockStopReason] || 'end_turn';
  }

  /**
   * Main transform method called by claude-code-router
   * Converts Anthropic API request to Bedrock and makes the API call
   */
  async transform(anthropicRequest, config) {
    try {
      // Extract model and get Bedrock model ID
      const model = anthropicRequest.model;
      const modelId = this.getModelId(model);

      // Extract system messages from messages array (if any)
      // CRITICAL: Bedrock rejects "system" role in messages
      const systemFromMessages = this.extractSystemFromMessages(anthropicRequest.messages);

      // Build Bedrock Converse API request
      const bedrockRequest = {
        modelId: modelId,
        messages: this.transformMessages(anthropicRequest.messages) // Filters out system messages
      };

      // Combine system prompts (from top-level field + extracted from messages)
      const systemPrompts = [];

      // Add top-level system if present
      if (anthropicRequest.system) {
        if (typeof anthropicRequest.system === 'string') {
          systemPrompts.push(anthropicRequest.system);
        } else if (Array.isArray(anthropicRequest.system)) {
          const systemText = anthropicRequest.system
            .map(block => block.text || block)
            .filter(text => text)
            .join('\n');
          if (systemText) {
            systemPrompts.push(systemText);
          }
        }
      }

      // Add extracted system messages
      if (systemFromMessages) {
        systemPrompts.push(systemFromMessages);
      }

      // Set system field if we have any system content
      if (systemPrompts.length > 0) {
        bedrockRequest.system = [{ text: systemPrompts.join('\n\n') }];
      }

      // Add inference configuration
      // IMPORTANT: Claude 4.5 models do NOT allow both temperature and topP
      // Anthropic recommends using temperature only
      bedrockRequest.inferenceConfig = {
        maxTokens: anthropicRequest.max_tokens || 4096
      };

      // Only add temperature OR topP, not both (prefer temperature)
      if (anthropicRequest.temperature !== undefined) {
        bedrockRequest.inferenceConfig.temperature = anthropicRequest.temperature;
      } else if (anthropicRequest.top_p !== undefined) {
        bedrockRequest.inferenceConfig.topP = anthropicRequest.top_p;
      } else {
        // Default to temperature if neither is specified
        bedrockRequest.inferenceConfig.temperature = 1.0;
      }

      // Add stop sequences if present
      if (anthropicRequest.stop_sequences && anthropicRequest.stop_sequences.length > 0) {
        bedrockRequest.inferenceConfig.stopSequences = anthropicRequest.stop_sequences;
      }

      // Add tools if present
      if (anthropicRequest.tools && anthropicRequest.tools.length > 0) {
        const toolConfig = this.transformTools(anthropicRequest.tools);
        if (toolConfig) {
          bedrockRequest.toolConfig = toolConfig;

          // Add tool_choice if specified
          if (anthropicRequest.tool_choice) {
            const toolChoice = this.transformToolChoice(anthropicRequest.tool_choice);
            if (toolChoice) {
              bedrockRequest.toolConfig.toolChoice = toolChoice;
            }
          }
        }
      }

      // Handle streaming vs non-streaming
      if (anthropicRequest.stream) {
        return await this.handleStreaming(bedrockRequest);
      } else {
        return await this.handleNonStreaming(bedrockRequest);
      }

    } catch (error) {
      console.error('Bedrock transformer error:', error);
      throw error;
    }
  }

  /**
   * Handle non-streaming requests
   */
  async handleNonStreaming(bedrockRequest) {
    const command = new ConverseCommand(bedrockRequest);
    const response = await this.client.send(command);
    return this.transformResponse(response);
  }

  /**
   * Handle streaming requests
   */
  async handleStreaming(bedrockRequest) {
    const command = new ConverseStreamCommand(bedrockRequest);
    const response = await this.client.send(command);

    // Return the stream for claude-code-router to handle
    // The router will need to process the stream events
    return {
      stream: response.stream,
      transformStreamEvent: (event) => this.transformStreamEvent(event)
    };
  }

  /**
   * Transform Bedrock stream events to Anthropic format
   */
  transformStreamEvent(event) {
    if (event.messageStart) {
      return {
        type: 'message_start',
        message: {
          id: `msg_${Date.now()}`,
          type: 'message',
          role: 'assistant',
          content: [],
          model: event.messageStart.role || 'assistant'
        }
      };
    } else if (event.contentBlockStart) {
      const index = event.contentBlockStart.contentBlockIndex;
      const start = event.contentBlockStart.start;

      if (start.toolUse) {
        return {
          type: 'content_block_start',
          index: index,
          content_block: {
            type: 'tool_use',
            id: start.toolUse.toolUseId,
            name: start.toolUse.name
          }
        };
      } else {
        return {
          type: 'content_block_start',
          index: index,
          content_block: {
            type: 'text',
            text: ''
          }
        };
      }
    } else if (event.contentBlockDelta) {
      const delta = event.contentBlockDelta.delta;

      if (delta.text) {
        return {
          type: 'content_block_delta',
          index: event.contentBlockDelta.contentBlockIndex,
          delta: {
            type: 'text_delta',
            text: delta.text
          }
        };
      } else if (delta.toolUse) {
        return {
          type: 'content_block_delta',
          index: event.contentBlockDelta.contentBlockIndex,
          delta: {
            type: 'input_json_delta',
            partial_json: delta.toolUse.input
          }
        };
      }
    } else if (event.contentBlockStop) {
      return {
        type: 'content_block_stop',
        index: event.contentBlockStop.contentBlockIndex
      };
    } else if (event.messageStop) {
      return {
        type: 'message_delta',
        delta: {
          stop_reason: this.mapStopReason(event.messageStop.stopReason)
        },
        usage: {
          output_tokens: 0 // Will be updated in metadata
        }
      };
    } else if (event.metadata) {
      return {
        type: 'message_stop',
        usage: {
          input_tokens: event.metadata.usage?.inputTokens || 0,
          output_tokens: event.metadata.usage?.outputTokens || 0
        }
      };
    }

    return null;
  }
}

// Export factory function for claude-code-router
module.exports = async (req, config) => {
  const transformer = new BedrockTransformer(config);
  return transformer.transform(req, config);
};

// Also export the class for direct use
module.exports.BedrockTransformer = BedrockTransformer;

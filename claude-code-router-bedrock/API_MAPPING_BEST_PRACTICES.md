# Best Practices for API Mapping & Transformation

## Lessons Learned from Bedrock Integration

### ❌ What Went Wrong (My Mistakes)

1. **Started coding before reading docs** - Led to multiple fix iterations
2. **Didn't create comparison matrix first** - Missed system message issue
3. **Assumed similarity** - Bedrock Converse != Anthropic Messages
4. **No validation** - Null tools crashed the system
5. **No test suite** - Found bugs in production
6. **Incomplete error handling** - Generic errors aren't helpful

### ✅ What Should Have Been Done

## Phase 1: Complete Documentation Research

**Before writing ANY code:**

```markdown
### 1. Read COMPLETE vendor documentation
- [ ] Source API (Anthropic) - every field, every constraint
- [ ] Target API (Bedrock) - every field, every constraint
- [ ] Output format (OpenAI) - for router compatibility

### 2. Create comprehensive comparison
- [ ] Request structure side-by-side
- [ ] Response structure side-by-side
- [ ] Field name mapping
- [ ] Type differences
- [ ] Default values
- [ ] Required vs optional fields
- [ ] Validation rules
- [ ] Error formats
```

**Example Comparison Matrix:**

| Feature | Source API | Target API | Transformation |
|---------|-----------|------------|----------------|
| System prompt | `system: string` | `system: [{text}]` | Wrap in array |
| Message roles | `user\|assistant` | `user\|assistant` | ⚠️ No `system` |
| Temp + Top_P | ✅ Both (old models) | ❌ Choose one | Prefer temperature |
| Tools | `input_schema` | `inputSchema.json` | Rename + wrap |

## Phase 2: Identify Breaking Differences

**Critical vs Nice-to-have:**

```javascript
// CRITICAL (will break): Different data structures
{
  severity: 'CRITICAL',
  issue: 'System role in messages',
  impact: '400 Validation Error',
  fix: 'Extract and move to system field'
}

// CRITICAL (will break): Missing required fields
{
  severity: 'CRITICAL',
  issue: 'Null tool names',
  impact: 'Bedrock rejects request',
  fix: 'Filter null/invalid tools'
}

// IMPORTANT (wrong results): Semantic differences
{
  severity: 'IMPORTANT',
  issue: 'Temperature + top_p together',
  impact: 'Request rejected',
  fix: 'Use temperature only'
}

// MINOR (cosmetic): Field name differences
{
  severity: 'MINOR',
  issue: 'input_tokens vs inputTokens',
  impact: 'Display only',
  fix: 'Map field names'
}
```

## Phase 3: Defensive Programming Patterns

### Pattern 1: Always Validate Input

```javascript
function validateBeforeTransform(input) {
  // Check required fields
  if (!input || typeof input !== 'object') {
    throw new ValidationError('Input must be an object');
  }

  if (!input.messages || !Array.isArray(input.messages)) {
    throw new ValidationError('messages must be an array');
  }

  if (input.messages.length === 0) {
    throw new ValidationError('messages cannot be empty');
  }

  // Validate each message
  for (const [index, msg] of input.messages.entries()) {
    if (!msg.role) {
      throw new ValidationError(`Message ${index} missing role`);
    }

    if (!['user', 'assistant', 'system'].includes(msg.role)) {
      throw new ValidationError(`Invalid role: ${msg.role}`);
    }

    if (!msg.content) {
      throw new ValidationError(`Message ${index} missing content`);
    }
  }

  return true;
}
```

### Pattern 2: Safe Field Access

```javascript
// ❌ WRONG - will crash if usage is undefined
const tokens = response.usage.input_tokens;

// ✅ CORRECT - safe with fallback
const tokens = response.usage?.input_tokens ?? 0;

// ✅ EVEN BETTER - validate type too
const tokens = typeof response.usage?.input_tokens === 'number'
  ? response.usage.input_tokens
  : 0;
```

### Pattern 3: Filter Invalid Data

```javascript
// ❌ WRONG - assumes all tools are valid
const tools = input.tools.map(transformTool);

// ✅ CORRECT - filter then transform
const tools = input.tools
  .filter(tool => tool && tool.name && tool.input_schema)
  .map(transformTool);

// ✅ EVEN BETTER - log what you filter
const tools = input.tools
  .filter(tool => {
    if (!tool || !tool.name) {
      console.warn('Filtered invalid tool:', tool);
      return false;
    }
    return true;
  })
  .map(transformTool);
```

### Pattern 4: Graceful Degradation

```javascript
// Try to extract, fallback if not possible
function extractSystemPrompt(input) {
  try {
    if (typeof input.system === 'string') {
      return input.system;
    }

    if (Array.isArray(input.system)) {
      return input.system
        .map(block => block.text || String(block))
        .join('\n');
    }

    return null; // No system prompt
  } catch (error) {
    console.warn('Failed to extract system prompt:', error);
    return null; // Don't crash the whole request
  }
}
```

### Pattern 5: Detailed Error Messages

```javascript
// ❌ WRONG - vague error
throw new Error('Invalid tool');

// ✅ CORRECT - specific error with context
throw new ValidationError(
  `Tool validation failed: missing required field 'name' in tool at index ${index}. ` +
  `Received: ${JSON.stringify(tool)}`
);
```

## Phase 4: Comprehensive Testing

### Test Categories

```javascript
const testSuites = {
  // Happy path
  basic: [
    'simple text message',
    'multiple messages',
    'with system prompt',
  ],

  // Features
  features: [
    'tool definitions',
    'tool use',
    'tool results',
    'images',
    'documents',
    'streaming',
  ],

  // Edge cases
  edgeCases: [
    'empty array',
    'null values',
    'undefined fields',
    'wrong types',
    'very long content',
    'unicode/emoji',
    'special characters',
  ],

  // Error scenarios
  errors: [
    'missing required fields',
    'invalid types',
    'authentication failure',
    'rate limiting',
    'timeout',
    'service error',
  ],
};
```

### Test Template

```javascript
describe('API Transformation', () => {
  test('transforms basic request correctly', async () => {
    const input = {
      model: 'claude-sonnet',
      messages: [{role: 'user', content: 'Hello'}],
      max_tokens: 100
    };

    const output = await transform(input);

    expect(output.modelId).toBe('global.anthropic.claude-sonnet-4-5-20250929-v1:0');
    expect(output.messages).toHaveLength(1);
    expect(output.messages[0].role).toBe('user');
    expect(output.inferenceConfig.maxTokens).toBe(100);
  });

  test('handles null tools gracefully', async () => {
    const input = {
      model: 'claude-sonnet',
      messages: [{role: 'user', content: 'Hello'}],
      tools: [null, {name: 'valid_tool', input_schema: {}}]
    };

    const output = await transform(input);

    expect(output.toolConfig.tools).toHaveLength(1);
    expect(output.toolConfig.tools[0].toolSpec.name).toBe('valid_tool');
  });
});
```

## Phase 5: Observability

### Logging Strategy

```javascript
// Request/Response logging
console.log({
  timestamp: new Date().toISOString(),
  requestId: req.id,
  direction: 'REQUEST',
  source: 'anthropic',
  target: 'bedrock',
  model: req.model,
  messageCount: req.messages.length,
  hasTools: !!req.tools,
  hasSystem: !!req.system
});

// Transformation logging
console.log({
  requestId: req.id,
  action: 'TRANSFORM',
  changes: {
    systemMessagesExtracted: systemCount,
    toolsFiltered: filteredCount,
    modelMapped: `${req.model} -> ${bedrockModelId}`
  }
});

// Error logging
console.error({
  requestId: req.id,
  error: err.message,
  stack: err.stack,
  input: JSON.stringify(req),
  phase: 'transformation'
});
```

### Metrics to Track

```javascript
{
  requests_total: counter,
  requests_failed: counter,
  transformation_duration_ms: histogram,
  tools_filtered: counter,
  system_messages_extracted: counter,
  token_usage: {
    input: counter,
    output: counter
  }
}
```

## Phase 6: Documentation

### Required Documents

1. **API_MAPPING.md** - Complete field-by-field comparison
2. **KNOWN_LIMITATIONS.md** - What doesn't work, untested features
3. **TROUBLESHOOTING.md** - Common errors and solutions
4. **TESTING.md** - How to test, test cases
5. **CHANGELOG.md** - Version history, breaking changes

### Code Documentation

```javascript
/**
 * Transform Anthropic Messages API request to AWS Bedrock Converse API
 *
 * CRITICAL DIFFERENCES:
 * 1. System messages must be extracted from messages array
 * 2. Bedrock rejects "system" role in messages
 * 3. Claude 4.5 does not allow temperature + top_p together
 * 4. Tool schema format is different (input_schema -> inputSchema.json)
 * 5. Model IDs must use inference profiles (global.anthropic.*)
 *
 * @param {Object} anthropicRequest - Anthropic Messages API format
 * @param {Object} config - Transformer configuration
 * @returns {Object} Bedrock Converse API format
 * @throws {ValidationError} If request is invalid
 *
 * @example
 * const bedrock = await transform({
 *   model: 'claude-sonnet',
 *   messages: [{role: 'user', content: 'Hello'}],
 *   max_tokens: 100
 * });
 */
```

## Checklist for Any API Mapping Project

```markdown
Research Phase:
- [ ] Read source API docs completely
- [ ] Read target API docs completely
- [ ] Create comparison matrix
- [ ] Identify all differences
- [ ] Categorize by severity
- [ ] List assumptions

Design Phase:
- [ ] Design transformation logic
- [ ] Plan error handling
- [ ] Plan validation strategy
- [ ] Design test cases
- [ ] Document decisions

Implementation Phase:
- [ ] Implement with defensive programming
- [ ] Add comprehensive validation
- [ ] Add detailed logging
- [ ] Handle all error cases
- [ ] Add null checks everywhere

Testing Phase:
- [ ] Unit tests for transformations
- [ ] Integration tests end-to-end
- [ ] Edge case tests
- [ ] Error scenario tests
- [ ] Load tests
- [ ] Manual QA

Documentation Phase:
- [ ] API mapping document
- [ ] Known limitations
- [ ] Troubleshooting guide
- [ ] Code comments
- [ ] README updates

Production Phase:
- [ ] Monitoring/metrics
- [ ] Error alerting
- [ ] Performance tracking
- [ ] User feedback loop
- [ ] Continuous testing
```

## Summary: What I Should Have Done

1. ✅ Read AWS Bedrock Converse API docs COMPLETELY
2. ✅ Read Anthropic Messages API docs COMPLETELY
3. ✅ Create comparison matrix FIRST
4. ❌ Build test suite BEFORE coding
5. ❌ Validate all inputs
6. ❌ Test streaming
7. ❌ Test tool use workflows
8. ❌ Handle all error cases
9. ✅ Document transformations
10. ❌ Add monitoring

**Result:** Would have saved hours of debugging and prevented production issues.

**Key Lesson:** Research first, code second, test thoroughly, document everything.

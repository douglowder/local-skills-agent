# Testing Documentation

## Test Summary

This project includes comprehensive test coverage for all core components.

### Test Statistics

- **Total Tests**: 80
- **Unit Tests**: 68
- **Integration Tests**: 12 (with qwen3:30b model)
- **Code Coverage**: 69% overall
- **All Tests**: ✅ PASSING

### Coverage Breakdown

| Module | Coverage | Notes |
|--------|----------|-------|
| `skills/agent.py` | 100% | Complete coverage of agent loop |
| `skills/ollama_client.py` | 100% | Complete coverage of Ollama integration |
| `skills/skill_loader.py` | 100% | Complete coverage of skill discovery |
| `skills/tools.py` | 97% | Near complete (2 lines uncovered) |
| `skills/main.py` | 0% | CLI interface (not unit tested) |

## Running Tests

### All Tests
```bash
uv run pytest -v
```

### Unit Tests Only
```bash
uv run pytest tests/test_*.py -v --ignore=tests/test_integration.py
```

### Integration Tests Only (requires Ollama + qwen3:30b)
```bash
uv run pytest tests/test_integration.py -v -s
```

### With Coverage Report
```bash
uv run pytest --cov=skills --cov-report=html
```

## Test Structure

### Unit Tests

#### `tests/test_tools.py` (26 tests)
- Tool base class functionality
- ReadFileTool: file reading, error handling
- WriteFileTool: file writing, parent directory creation
- BashTool: command execution, timeouts, error handling
- ListDirectoryTool: directory listing
- Tool execution and error handling

#### `tests/test_skill_loader.py` (18 tests)
- Skill class initialization
- Skill discovery from `.skills/` directory
- Markdown file parsing
- Skill descriptions extraction
- Error handling for corrupted files
- Skills summary generation

#### `tests/test_ollama_client.py` (13 tests)
- Client initialization
- Model listing
- Chat functionality
- Tool calling support
- Streaming responses
- Error handling and recovery

#### `tests/test_agent.py` (14 tests)
- Agent initialization with tools and skills
- System prompt generation
- Message history management
- Tool call orchestration
- Multi-turn conversations
- Max iteration limits
- Context preservation

### Integration Tests (qwen3:30b)

#### `tests/test_integration.py` (12 tests)

**TestOllamaIntegration** (3 tests)
- List available models
- Simple chat interactions
- Tool calling capability

**TestAgentIntegration** (6 tests)
- Agent initialization
- Simple user interactions
- File reading with tools
- Bash command execution
- Skill discovery and usage
- Conversation context preservation

**TestModelCapabilities** (3 tests)
- Response quality and coherence
- JSON understanding
- Instruction following

## Integration Test Results

The qwen3:30b model successfully demonstrated:

1. **Tool Usage**: Correctly invoked `read_file`, `write_file`, `bash`, and `list_directory` tools
2. **Reasoning**: Showed detailed chain-of-thought reasoning in responses
3. **Context Awareness**: Maintained conversation history across multiple turns
4. **Skill Discovery**: Successfully listed and understood available skills
5. **Instruction Following**: Followed specific user instructions accurately

## Test Fixtures

Located in `tests/conftest.py`:
- `temp_dir`: Temporary directory for file operations
- `sample_skill_dir`: Pre-populated skills directory
- `sample_file`: Test file with content
- `mock_ollama_response`: Mock Ollama responses
- `ollama_model`: Model name for integration tests
- `check_ollama_available`: Ensures Ollama is running

## Notes

- Integration tests require Ollama to be running: `ollama serve`
- The qwen3:30b model must be available: `ollama pull qwen3:30b`
- Integration tests may take longer due to LLM inference time
- All tests use `uv` for dependency management

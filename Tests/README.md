# Tests Module

Comprehensive test suite for AI CLI with 100+ tests covering all functionality, including 80 tests for the variable system alone.

## Structure

- `__init__.py` - Module initialization
- `conftest.py` - Pytest configuration and shared fixtures
- `unit/` - Unit tests for individual components
  - `test_api_client.py` - API client tests (sync and async)
  - `test_cli.py` - CLI argument parsing and command handling
  - `test_config.py` - Configuration loading and management
  - `test_interactive_mode.py` - Interactive mode behavior
  - `test_io_utils.py` - File I/O and token management
  - `test_validation.py` - Input validation and security
  - `test_variables.py` - **Variable system tests (80 comprehensive tests)**
  - `test_music.py` - Music generation and playback
  - `test_theme.py` - Theme system and color management
- `integration/` - Integration tests
  - `test_full_conversation.py` - End-to-end conversation flows
  - `test_variable_integration.py` - **Variable system integration across modes**
- `cpp/` - C++ API tests
  - `test_variable_api.cpp` - **C++ variable API cross-language tests**
  - `CMakeLists.txt` - C++ test build configuration

## Running Tests

### Quick Test Script (Recommended)
```bash
./t --quick       # Fast functionality test (30 seconds)
./t --unit        # Run all unit tests (100+ tests)
./t --integration # Integration tests  
./t --cpp         # C++ API tests
./t --build       # Build system tests
./t               # Complete test suite
```

### Using Pytest Directly
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai --cov-report=html

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -k "variable"       # Tests containing "variable"

# Run specific test files
pytest tests/unit/test_variables.py     # 80 variable tests
pytest tests/unit/test_music.py         # Music tests
```

### Using Make
```bash
make test           # Run all tests
make test-unit      # Unit tests only
make test-coverage  # With coverage report
```

## Test Coverage

### Unit Tests (100+)
- **Variable System**: 80 tests covering all edge cases
- **API Clients**: Request/response handling, error cases
- **CLI**: Argument parsing, command execution
- **Configuration**: Loading, validation, defaults
- **Interactive Mode**: User input, commands, display
- **Music System**: Generation, playback, MIDI creation
- **Themes**: Color application, theme switching
- **Validation**: Security checks, input sanitization

### Integration Tests
- **Full Conversations**: End-to-end API interactions
- **Variable Integration**: Cross-mode variable usage
- **File Uploads**: Multiple file handling
- **Error Recovery**: Network issues, API limits

### C++ Tests
- **Variable API**: Get/Set operations from C++
- **Memory Management**: No leaks, proper cleanup
- **Cross-language**: Python ↔ C++ data exchange

## Variable System Tests

The variable system includes comprehensive testing for:
- Assignment and retrieval (`name=John`, `name`)
- JSON parsing (arrays, objects, booleans, null)
- Persistence across sessions
- Interactive mode integration
- C++ API cross-language access
- Error handling and edge cases
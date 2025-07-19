# Tests Module

Comprehensive test suite for PyClaudeCli with 40+ tests covering all functionality.

## Structure

- `__init__.py` - Module initialization
- `conftest.py` - Pytest configuration and fixtures
- `unit/` - Unit tests for individual components
  - `test_api_client.py` - API client tests
  - `test_cli.py` - CLI tests
  - `test_config.py` - Configuration tests
  - `test_interactive_mode.py` - Interactive mode tests
  - `test_io_utils.py` - I/O utility tests
  - `test_validation.py` - Validation tests
  - `test_variables.py` - **Variable system tests (40 comprehensive tests)**
- `integration/` - Integration tests
  - `test_full_conversation.py` - Full conversation flow tests
  - `test_variable_integration.py` - **Variable system integration tests**
- `cpp/` - C++ API tests
  - `test_variable_api.cpp` - **C++ variable API tests**
  - `CMakeLists.txt` - C++ test build configuration

## Running Tests

### Quick Test Script (Recommended)
```bash
./t --quick       # Fast functionality test (30 seconds)
./t --unit        # Run 40 unit tests
./t --integration # Integration tests  
./t --cpp         # C++ API tests
./t               # Complete test suite
```

### Traditional Methods
```bash
pytest                                    # All pytest tests
python3 tests/unit/test_variables.py     # Variable system tests
python3 tests/integration/test_variable_integration.py  # Integration tests
```

### Build and Test
```bash
./b               # Build everything and run all tests
```

## Test Coverage

- **40 Unit Tests**: Complete variable system coverage
- **Integration Tests**: Interactive mode integration
- **C++ Tests**: Cross-language API validation
- **Build Tests**: CMake and compilation validation
- **Edge Cases**: Unicode, corruption, performance testing

## Variable System Tests

The variable system includes comprehensive testing for:
- Assignment and retrieval (`name=John`, `name`)
- JSON parsing (arrays, objects, booleans, null)
- Persistence across sessions
- Interactive mode integration
- C++ API cross-language access
- Error handling and edge cases
# Tests Module

Test suite for PyClaudeCli.

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
- `integration/` - Integration tests
  - `test_full_conversation.py` - Full conversation flow tests

## Running Tests

Run tests using pytest:
```bash
pytest
```
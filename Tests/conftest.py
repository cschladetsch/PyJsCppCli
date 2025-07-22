"""Pytest configuration and shared fixtures for Ask CLI tests"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import asyncio
import json
from typing import Dict, Any, List

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_home(monkeypatch):
    """Create a temporary home directory for test isolation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("HOME", tmpdir)
        monkeypatch.setenv("USERPROFILE", tmpdir)  # Windows compatibility
        yield Path(tmpdir)


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock Claude API key"""
    test_key = "test-api-key-12345"
    monkeypatch.setenv("CLAUDE_API_KEY", test_key)
    return test_key


@pytest.fixture
def mock_claude_client():
    """Mock Claude API client"""
    client = AsyncMock()
    client.generate_response = AsyncMock(return_value=(
        "This is a test response",
        [{"query": "test", "response": "This is a test response"}]
    ))
    client.stream_response = AsyncMock()
    
    async def mock_stream():
        for chunk in ["This ", "is ", "a ", "streaming ", "response"]:
            yield chunk
    
    client.stream_response.return_value = mock_stream()
    return client


@pytest.fixture
def cli_runner():
    """Create a CLI test runner"""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def sample_conversation():
    """Sample conversation data for testing"""
    return [
        {
            "query": "What is Python?",
            "response": "Python is a high-level programming language...",
            "timestamp": "2024-01-01T12:00:00"
        },
        {
            "query": "How do I install packages?",
            "response": "You can install packages using pip...",
            "timestamp": "2024-01-01T12:05:00"
        }
    ]


@pytest.fixture
def mock_response_data():
    """Mock API response data"""
    return {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "This is a mock response from Claude"
            }
        ],
        "model": "claude-3-sonnet-20241022",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 20
        }
    }


@pytest.fixture
def test_files(tmp_path):
    """Create test files for upload testing"""
    files = {}
    
    # Create a text file
    text_file = tmp_path / "test.txt"
    text_file.write_text("This is a test file")
    files["text"] = text_file
    
    # Create a Python file
    py_file = tmp_path / "test.py"
    py_file.write_text("def hello():\n    return 'world'")
    files["python"] = py_file
    
    # Create a markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\nThis is a test markdown file")
    files["markdown"] = md_file
    
    # Create a directory with files
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    (test_dir / "file1.txt").write_text("File 1")
    (test_dir / "file2.txt").write_text("File 2")
    files["directory"] = test_dir
    
    return files


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Markers for different test types
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as a performance benchmark"
    )
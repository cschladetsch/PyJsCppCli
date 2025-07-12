"""Unit tests for I/O utilities"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open, Mock
from ai.utils.io import (
    load_conversation_state,
    save_conversation_state,
    append_to_conversation_log,
    resolve_file_paths,
    prepare_files_for_upload,
    get_api_key
)
from ai.models import Interaction


class TestIOUtils:
    """Test cases for I/O utility functions"""
    
    def test_load_conversation_state_no_file(self):
        """Test loading conversation state when no file exists"""
        with patch('os.path.exists', return_value=False):
            state = load_conversation_state()
            assert state == []
    
    def test_load_conversation_state_legacy_file(self):
        """Test loading from legacy conversation file"""
        legacy_data = [
            {"query": "old query", "response": "old response"}
        ]
        
        with patch('os.path.exists') as mock_exists:
            # New file doesn't exist, legacy does
            mock_exists.side_effect = lambda x: ".claude_" in x
            
            with patch('builtins.open', mock_open(read_data=json.dumps(legacy_data))):
                state = load_conversation_state()
                
                assert len(state) == 1
                assert isinstance(state[0], Interaction)
                assert state[0].query == "old query"
    
    def test_load_conversation_state_valid_json(self):
        """Test loading valid conversation state"""
        data = [
            {"query": "q1", "response": "r1", "timestamp": "2024-01-01"},
            {"query": "q2", "response": "r2"}
        ]
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(data))):
                state = load_conversation_state()
                
                assert len(state) == 2
                assert all(isinstance(item, Interaction) for item in state)
                assert state[0].query == "q1"
                assert state[1].response == "r2"
    
    def test_load_conversation_state_invalid_json(self):
        """Test loading invalid JSON gracefully"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="invalid json")):
                state = load_conversation_state()
                assert state == []
    
    def test_save_conversation_state(self, tmp_path):
        """Test saving conversation state"""
        interactions = [
            Interaction(query="q1", response="r1"),
            Interaction(query="q2", response="r2")
        ]
        
        test_file = tmp_path / "test_state.json"
        
        with patch('os.path.expanduser', return_value=str(test_file)):
            save_conversation_state(interactions)
        
        # Verify file was written correctly
        with open(test_file) as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]["query"] == "q1"
        assert data[1]["response"] == "r2"
        assert all("timestamp" in item for item in data)
    
    def test_append_to_conversation_log(self, tmp_path):
        """Test appending to conversation log"""
        interaction = Interaction(
            query="Test query",
            response="Test response"
        )
        
        log_file = tmp_path / "test_log.md"
        
        with patch('os.path.expanduser', return_value=str(log_file)):
            append_to_conversation_log(interaction)
        
        content = log_file.read_text()
        assert "Test query" in content
        assert "Test response" in content
        assert "## User" in content
        assert "## Assistant" in content
        assert "---" in content  # Separator
    
    def test_resolve_file_paths_single_file(self, tmp_path):
        """Test resolving single file path"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        paths = resolve_file_paths([str(test_file)])
        assert len(paths) == 1
        assert paths[0] == test_file
    
    def test_resolve_file_paths_directory_non_recursive(self, tmp_path):
        """Test resolving directory without recursion"""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("1")
        (test_dir / "file2.txt").write_text("2")
        
        sub_dir = test_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file3.txt").write_text("3")
        
        paths = resolve_file_paths([str(test_dir)], recursive=False)
        path_names = [p.name for p in paths]
        
        assert len(paths) == 2
        assert "file1.txt" in path_names
        assert "file2.txt" in path_names
        assert "file3.txt" not in path_names
    
    def test_resolve_file_paths_directory_recursive(self, tmp_path):
        """Test resolving directory with recursion"""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("1")
        
        sub_dir = test_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file2.txt").write_text("2")
        
        paths = resolve_file_paths([str(test_dir)], recursive=True)
        path_names = [p.name for p in paths]
        
        assert len(paths) == 2
        assert "file1.txt" in path_names
        assert "file2.txt" in path_names
    
    def test_resolve_file_paths_nonexistent(self):
        """Test resolving non-existent paths"""
        with patch('builtins.print') as mock_print:
            paths = resolve_file_paths(["/nonexistent/file.txt"])
            
            assert len(paths) == 0
            # Should print warning
            output = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "not found" in output.lower()
    
    def test_prepare_files_for_upload_text_files(self, test_files):
        """Test preparing text files for upload"""
        files = [test_files["text"], test_files["python"]]
        
        contents, images = prepare_files_for_upload(files)
        
        assert len(contents) == 2
        assert len(images) == 0
        
        # Check content format
        assert "test.txt" in contents[0]
        assert "This is a test file" in contents[0]
        assert "test.py" in contents[1]
        assert "def hello():" in contents[1]
    
    @patch('ai.utils.io.base64.b64encode')
    def test_prepare_files_for_upload_image_files(self, mock_b64, tmp_path):
        """Test preparing image files for upload"""
        # Create fake image file
        img_file = tmp_path / "test.png"
        img_file.write_bytes(b"fake image data")
        
        mock_b64.return_value = b"encoded_data"
        
        contents, images = prepare_files_for_upload([img_file])
        
        assert len(contents) == 0
        assert len(images) == 1
        assert images[0]["source"]["type"] == "base64"
        assert images[0]["source"]["media_type"] == "image/png"
        assert images[0]["source"]["data"] == "encoded_data"
    
    def test_prepare_files_for_upload_mixed_files(self, tmp_path):
        """Test preparing mixed file types"""
        text_file = tmp_path / "doc.txt"
        text_file.write_text("Documentation")
        
        img_file = tmp_path / "image.jpg"
        img_file.write_bytes(b"image data")
        
        with patch('ai.utils.io.base64.b64encode', return_value=b"encoded"):
            contents, images = prepare_files_for_upload([text_file, img_file])
        
        assert len(contents) == 1
        assert len(images) == 1
        assert "Documentation" in contents[0]
    
    def test_get_api_key_from_env(self, monkeypatch):
        """Test getting API key from environment"""
        monkeypatch.setenv("CLAUDE_API_KEY", "env-key-123")
        
        key = get_api_key()
        assert key == "env-key-123"
    
    def test_get_api_key_from_file(self, monkeypatch, tmp_path):
        """Test getting API key from file"""
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        
        token_file = tmp_path / ".ask_token"
        token_file.write_text("file-key-456\n")
        
        with patch('os.path.expanduser', return_value=str(token_file)):
            key = get_api_key()
            assert key == "file-key-456"
    
    def test_get_api_key_not_found(self, monkeypatch):
        """Test API key not found"""
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        
        with patch('os.path.exists', return_value=False):
            with pytest.raises(ValueError) as exc_info:
                get_api_key()
            
            assert "API key" in str(exc_info.value)
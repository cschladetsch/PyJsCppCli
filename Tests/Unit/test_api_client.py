"""Unit tests for the Claude API client"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
import httpx
from ask.Api.client import ClaudeClient


class TestClaudeClient:
    """Test cases for ClaudeClient"""
    
    @pytest.fixture
    def client(self, mock_api_key):
        """Create a ClaudeClient instance with mocked API key"""
        return ClaudeClient()
    
    def test_client_initialization(self, client):
        """Test client initializes with correct defaults"""
        assert client.model == "claude-3-5-sonnet-20241022"
        assert client.max_tokens == 1024
        assert client.base_url == "https://api.anthropic.com/v1/messages"
    
    def test_headers_include_api_key(self, client, mock_api_key):
        """Test that headers include the API key"""
        headers = client._get_headers()
        assert headers["x-api-key"] == mock_api_key
        assert headers["anthropic-version"] == "2023-06-01"
        assert headers["content-type"] == "application/json"
    
    @patch('httpx.post')
    def test_generate_response_success(self, mock_post, client):
        """Test successful response generation"""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "Hello, world!"}],
            "usage": {"input_tokens": 10, "output_tokens": 20}
        }
        mock_post.return_value = mock_response
        
        query = "Say hello"
        response, interactions = client.generate_response(query)
        
        assert response == "Hello, world!"
        assert len(interactions) == 1
        assert interactions[0].query == query
        assert interactions[0].response == "Hello, world!"
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == client.base_url
        assert "messages" in call_args[1]["json"]
    
    @patch('httpx.post')
    def test_generate_response_with_system_prompt(self, mock_post, client):
        """Test response generation with custom system prompt"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "Response"}],
            "usage": {"input_tokens": 10, "output_tokens": 5}
        }
        mock_post.return_value = mock_response
        
        system_prompt = "You are a helpful coding assistant"
        query = "Help me write a function"
        
        response, _ = client.generate_response(
            query, 
            system_prompt=system_prompt
        )
        
        # Verify system prompt was included
        call_args = mock_post.call_args[1]["json"]
        assert call_args["system"] == system_prompt
    
    @patch('httpx.post')
    def test_generate_response_with_existing_interactions(self, mock_post, client, sample_conversation):
        """Test response generation with conversation history"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "New response"}],
            "usage": {"input_tokens": 50, "output_tokens": 10}
        }
        mock_post.return_value = mock_response
        
        query = "Tell me more"
        response, interactions = client.generate_response(
            query,
            interactions=sample_conversation
        )
        
        assert response == "New response"
        assert len(interactions) == len(sample_conversation) + 1
        assert interactions[-1].query == query
        assert interactions[-1].response == "New response"
    
    @patch('httpx.post')
    def test_api_error_handling(self, mock_post, client):
        """Test handling of API errors"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {"message": "Rate limit exceeded"}
        }
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=Mock(),
            response=mock_response
        )
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            client.generate_response("test")
        
        assert "429" in str(exc_info.value) or "Rate limit" in str(exc_info.value)
    
    @patch('httpx.post')
    def test_network_error_handling(self, mock_post, client):
        """Test handling of network errors"""
        mock_post.side_effect = httpx.ConnectError("Network error")
        
        with pytest.raises(Exception) as exc_info:
            client.generate_response("test")
        
        assert "Network error" in str(exc_info.value)
    
    def test_missing_api_key(self, monkeypatch):
        """Test error when API key is missing"""
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        
        # Mock both token file paths to not exist
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            with pytest.raises(ValueError) as exc_info:
                ClaudeClient()
            
            assert "API key" in str(exc_info.value)
    
    def test_token_from_file(self, monkeypatch, tmp_path):
        """Test reading API key from token file"""
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        
        # Create a mock token file
        token_file = tmp_path / ".claude_token"
        token_file.write_text("file-api-key-123")
        
        with patch('os.path.expanduser') as mock_expand:
            mock_expand.return_value = str(token_file)
            
            client = ClaudeClient()
            headers = client._get_headers()
            assert headers["x-api-key"] == "file-api-key-123"
    
    @patch('httpx.post')
    def test_max_tokens_configuration(self, mock_post, client):
        """Test max_tokens parameter is passed correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "Response"}],
            "usage": {"input_tokens": 10, "output_tokens": 5}
        }
        mock_post.return_value = mock_response
        
        client.max_tokens = 2048
        client.generate_response("test")
        
        call_args = mock_post.call_args[1]["json"]
        assert call_args["max_tokens"] == 2048
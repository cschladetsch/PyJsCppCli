"""Integration tests for full conversation workflows"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
import json
from ask.cli import main
from ask.Modes.interactive import InteractiveMode
from ask.models import Interaction


class TestFullConversation:
    """Test complete conversation workflows"""
    
    @pytest.mark.integration
    def test_single_query_workflow(self, temp_home, mock_api_key):
        """Test a complete single query workflow"""
        with patch('sys.argv', ['ask', 'What is Python?']):
            with patch('ask.Api.client.httpx.post') as mock_post:
                # Mock API response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "content": [{"type": "text", "text": "Python is a programming language"}],
                    "usage": {"input_tokens": 10, "output_tokens": 20}
                }
                mock_post.return_value = mock_response
                
                result = main()
                
                assert result == 0
                
                # Check conversation was saved
                state_file = temp_home / ".ask_conversation_state.json"
                assert state_file.exists()
                
                with open(state_file) as f:
                    state = json.load(f)
                assert len(state) == 1
                assert state[0]["query"] == "What is Python?"
                
                # Check history was saved
                history_file = temp_home / ".ask_history"
                assert history_file.exists()
                assert "What is Python?" in history_file.read_text()
    
    @pytest.mark.integration
    def test_interactive_conversation_flow(self, temp_home, mock_api_key):
        """Test a multi-turn interactive conversation"""
        queries = [
            "Hello",
            "Tell me about Python",
            "c 1",  # Show last conversation
            "exit"
        ]
        
        with patch('prompt_toolkit.PromptSession.prompt') as mock_prompt:
            mock_prompt.side_effect = queries
            
            with patch('ask.Api.client.httpx.post') as mock_post:
                # Mock API responses
                responses = [
                    {"content": [{"type": "text", "text": "Hello! How can I help?"}]},
                    {"content": [{"type": "text", "text": "Python is a versatile language"}]}
                ]
                
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.side_effect = [
                    {**resp, "usage": {"input_tokens": 10, "output_tokens": 20}}
                    for resp in responses
                ]
                mock_post.return_value = mock_response
                
                interactive = InteractiveMode()
                interactive.run()
                
                # Check final state
                assert len(interactive.interactions) == 2
                assert interactive.interactions[0].query == "Hello"
                assert interactive.interactions[1].query == "Tell me about Python"
    
    @pytest.mark.integration
    def test_conversation_persistence_across_sessions(self, temp_home, mock_api_key):
        """Test that conversations persist across sessions"""
        # First session
        with patch('sys.argv', ['ask', 'First question']):
            with patch('ask.Api.client.httpx.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "content": [{"type": "text", "text": "First answer"}],
                    "usage": {"input_tokens": 10, "output_tokens": 10}
                }
                mock_post.return_value = mock_response
                
                main()
        
        # Second session
        with patch('sys.argv', ['ask', 'Second question']):
            with patch('ask.Api.client.httpx.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "content": [{"type": "text", "text": "Second answer"}],
                    "usage": {"input_tokens": 20, "output_tokens": 10}
                }
                mock_post.return_value = mock_response
                
                main()
        
        # Check combined state
        state_file = temp_home / ".ask_conversation_state.json"
        with open(state_file) as f:
            state = json.load(f)
        
        assert len(state) == 2
        assert state[0]["query"] == "First question"
        assert state[1]["query"] == "Second question"
    
    @pytest.mark.integration
    def test_clear_conversation_workflow(self, temp_home, mock_api_key):
        """Test clearing conversation history"""
        # Create initial conversation
        initial_state = [
            {"query": "old query", "response": "old response", "timestamp": "2024-01-01"}
        ]
        
        state_file = temp_home / ".ask_conversation_state.json"
        with open(state_file, 'w') as f:
            json.dump(initial_state, f)
        
        # Clear conversation
        with patch('sys.argv', ['ask', 'clear']):
            result = main()
            assert result == 0
        
        # Check state was cleared
        with open(state_file) as f:
            state = json.load(f)
        assert state == []
    
    @pytest.mark.integration
    def test_file_upload_workflow(self, temp_home, mock_api_key, test_files):
        """Test file upload workflow"""
        test_file = test_files["text"]
        
        with patch('sys.argv', ['ask', 'upload', str(test_file)]):
            with patch('ask.Api.client.httpx.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "content": [{"type": "text", "text": "I see the uploaded file"}],
                    "usage": {"input_tokens": 50, "output_tokens": 10}
                }
                mock_post.return_value = mock_response
                
                with patch('builtins.print') as mock_print:
                    result = main()
                
                assert result == 0
                
                # Check upload was mentioned
                output = ' '.join(str(call) for call in mock_print.call_args_list)
                assert "uploaded" in output.lower()
    
    @pytest.mark.integration
    def test_error_recovery_workflow(self, temp_home, mock_api_key):
        """Test error recovery in conversation"""
        with patch('sys.argv', ['ask', 'Test query']):
            with patch('ask.Api.client.httpx.post') as mock_post:
                # First call fails, second succeeds
                mock_response_fail = Mock()
                mock_response_fail.status_code = 500
                mock_response_fail.raise_for_status.side_effect = Exception("Server error")
                
                mock_response_success = Mock()
                mock_response_success.status_code = 200
                mock_response_success.json.return_value = {
                    "content": [{"type": "text", "text": "Success after retry"}],
                    "usage": {"input_tokens": 10, "output_tokens": 10}
                }
                
                mock_post.side_effect = [mock_response_fail, mock_response_success]
                
                # For this test, we expect it to fail without retry logic
                # This is where retry logic would be implemented
                result = main()
                assert result == 1  # Should fail
    
    @pytest.mark.integration
    def test_conversation_log_creation(self, temp_home, mock_api_key):
        """Test markdown conversation log creation"""
        with patch('sys.argv', ['ask', 'Log this conversation']):
            with patch('ask.Api.client.httpx.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "content": [{"type": "text", "text": "This will be logged"}],
                    "usage": {"input_tokens": 10, "output_tokens": 10}
                }
                mock_post.return_value = mock_response
                
                main()
        
        # Check markdown log was created
        log_file = temp_home / ".ask_conversation.md"
        assert log_file.exists()
        
        content = log_file.read_text()
        assert "Log this conversation" in content
        assert "This will be logged" in content
        assert "## User" in content
        assert "## Assistant" in content
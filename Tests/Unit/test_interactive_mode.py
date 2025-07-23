"""Unit tests for interactive mode functionality"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from ask.Modes.interactive import InteractiveMode
from ask.models import Interaction


class TestInteractiveMode:
    """Test cases for InteractiveMode"""
    
    @pytest.fixture
    def interactive_mode(self, mock_api_key):
        """Create an InteractiveMode instance"""
        with patch('ask.Modes.interactive.ClaudeClient'):
            return InteractiveMode()
    
    def test_initialization(self, interactive_mode):
        """Test interactive mode initialization"""
        assert interactive_mode.system_prompt is not None
        assert interactive_mode.client is not None
        assert isinstance(interactive_mode.interactions, list)
    
    @patch('ask.Modes.interactive.PromptSession')
    def test_command_parsing_exit(self, mock_prompt_session, interactive_mode):
        """Test exit command detection"""
        # Test various exit commands
        for cmd in ['exit', 'quit', 'EXIT', 'QUIT']:
            assert interactive_mode._should_exit(cmd) is True
        
        # Test non-exit commands
        assert interactive_mode._should_exit('help') is False
        assert interactive_mode._should_exit('what is exit?') is False
    
    def test_help_command(self, interactive_mode):
        """Test help command display"""
        with patch('builtins.print') as mock_print:
            interactive_mode.handle_help_command()
            
            # Verify help content is printed
            calls = [str(call) for call in mock_print.call_args_list]
            help_text = ' '.join(calls)
            
            assert 'Available commands:' in help_text
            assert 'help' in help_text
            assert 'exit' in help_text
            assert 'upload' in help_text
    
    @patch('builtins.open', create=True)
    def test_history_command(self, mock_open, interactive_mode):
        """Test history command"""
        # Mock history file content
        mock_open.return_value.__enter__.return_value.readlines.return_value = [
            "query 1\n",
            "query 2\n",
            "query 3\n"
        ]
        
        with patch('builtins.print') as mock_print:
            # Test showing all history
            interactive_mode.handle_history_command()
            assert mock_print.call_count >= 3
            
            # Reset mock
            mock_print.reset_mock()
            
            # Test showing last N entries
            interactive_mode.handle_history_command(2)
            assert mock_print.call_count >= 2
    
    def test_conversation_command_empty(self, interactive_mode):
        """Test conversation command with no history"""
        interactive_mode.interactions = []
        
        with patch('builtins.print') as mock_print:
            interactive_mode.handle_conversation_command()
            
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("No conversation" in str(call) for call in calls)
    
    def test_conversation_command_with_history(self, interactive_mode):
        """Test conversation command with existing history"""
        interactive_mode.interactions = [
            Interaction(query="Hello", response="Hi there!"),
            Interaction(query="How are you?", response="I'm doing well!")
        ]
        
        with patch('builtins.print') as mock_print:
            interactive_mode.handle_conversation_command()
            
            output = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Hello" in output
            assert "Hi there!" in output
            assert "How are you?" in output
    
    def test_conversation_command_limit(self, interactive_mode):
        """Test conversation command with limit"""
        interactive_mode.interactions = [
            Interaction(query=f"Query {i}", response=f"Response {i}")
            for i in range(10)
        ]
        
        with patch('builtins.print') as mock_print:
            interactive_mode.handle_conversation_command(3)
            
            output = ' '.join(str(call) for call in mock_print.call_args_list)
            # Should show last 3 exchanges
            assert "Query 9" in output
            assert "Query 8" in output
            assert "Query 7" in output
            assert "Query 6" not in output
    
    def test_clear_command(self, interactive_mode):
        """Test clear command"""
        interactive_mode.interactions = [
            Interaction(query="test", response="response")
        ]
        
        with patch('ask.Modes.interactive.save_conversation_state') as mock_save:
            with patch('builtins.print') as mock_print:
                interactive_mode.handle_clear_command()
                
                assert len(interactive_mode.interactions) == 0
                mock_save.assert_called_once_with([])
                
                output = ' '.join(str(call) for call in mock_print.call_args_list)
                assert "cleared" in output.lower()
    
    @patch('ask.Modes.interactive.resolve_file_paths')
    @patch('ask.Modes.interactive.prepare_files_for_upload')
    def test_upload_command_single_file(self, mock_prepare, mock_resolve, interactive_mode):
        """Test upload command with single file"""
        mock_resolve.return_value = [Path("/test/file.txt")]
        mock_prepare.return_value = (["file.txt content"], [])
        
        with patch('builtins.print') as mock_print:
            interactive_mode.handle_upload_command(["file.txt"])
            
            mock_resolve.assert_called_once_with(["file.txt"], recursive=False)
            mock_prepare.assert_called_once()
            
            output = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "uploaded" in output.lower()
    
    @patch('ask.Modes.interactive.resolve_file_paths')
    def test_upload_command_recursive(self, mock_resolve, interactive_mode):
        """Test upload command with recursive flag"""
        mock_resolve.return_value = [
            Path("/test/dir/file1.txt"),
            Path("/test/dir/file2.txt")
        ]
        
        with patch('ask.Modes.interactive.prepare_files_for_upload'):
            interactive_mode.handle_upload_command(["--recursive", "/test/dir"])
            
            mock_resolve.assert_called_with(["/test/dir"], recursive=True)
    
    def test_upload_command_no_files(self, interactive_mode):
        """Test upload command with no files specified"""
        with patch('builtins.print') as mock_print:
            interactive_mode.handle_upload_command([])
            
            output = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "usage" in output.lower()
    
    @patch('ask.Modes.interactive.PromptSession')
    def test_run_loop_exit(self, mock_prompt_session_class, interactive_mode):
        """Test main run loop with exit command"""
        mock_session = Mock()
        mock_session.prompt.side_effect = ["test query", "exit"]
        mock_prompt_session_class.return_value = mock_session
        
        interactive_mode.client.generate_response.return_value = (
            "Response", 
            [Interaction(query="test query", response="Response")]
        )
        
        with patch('builtins.print'):
            interactive_mode.run()
        
        # Should have prompted twice (once for query, once for exit)
        assert mock_session.prompt.call_count == 2
        assert interactive_mode.client.generate_response.call_count == 1
    
    @patch('ask.Modes.interactive.PromptSession')
    def test_run_loop_keyboard_interrupt(self, mock_prompt_session_class, interactive_mode):
        """Test handling keyboard interrupt in run loop"""
        mock_session = Mock()
        mock_session.prompt.side_effect = KeyboardInterrupt()
        mock_prompt_session_class.return_value = mock_session
        
        with patch('builtins.print') as mock_print:
            interactive_mode.run()
            
            # Should exit gracefully
            output = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "goodbye" in output.lower() or "exit" in output.lower()
    
    def test_process_query_normal(self, interactive_mode):
        """Test processing a normal query"""
        query = "What is Python?"
        interactive_mode.client.generate_response.return_value = (
            "Python is a programming language",
            [Interaction(query=query, response="Python is a programming language")]
        )
        
        with patch('ask.Modes.interactive.save_conversation_state'):
            with patch('ask.Modes.interactive.append_to_conversation_log'):
                with patch('builtins.print'):
                    result = interactive_mode._process_query(query)
        
        assert result is True  # Should continue
        assert len(interactive_mode.interactions) == 1
        assert interactive_mode.interactions[0].query == query
    
    def test_process_query_commands(self, interactive_mode):
        """Test processing various commands"""
        # Test help command
        with patch.object(interactive_mode, 'handle_help_command') as mock_help:
            interactive_mode._process_query("help")
            mock_help.assert_called_once()
        
        # Test clear command
        with patch.object(interactive_mode, 'handle_clear_command') as mock_clear:
            interactive_mode._process_query("clear")
            mock_clear.assert_called_once()
        
        # Test exit command
        result = interactive_mode._process_query("exit")
        assert result is False  # Should exit
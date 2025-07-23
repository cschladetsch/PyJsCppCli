"""Unit tests for CLI command handling"""

import pytest
from unittest.mock import Mock, patch, mock_open
import sys
from io import StringIO
from ask.cli import handle_command_line_query, main


class TestCLI:
    """Test cases for CLI functionality"""
    
    @patch('ask.cli.ClaudeClient')
    @patch('ask.cli.save_conversation_state')
    @patch('ask.cli.load_conversation_state')
    def test_simple_query(self, mock_load, mock_save, mock_client_class):
        """Test handling a simple query"""
        # Setup mocks
        mock_load.return_value = []
        mock_client = Mock()
        mock_client.generate_response.return_value = (
            "Test response",
            [{"query": "test query", "response": "Test response"}]
        )
        mock_client_class.return_value = mock_client
        
        # Capture output
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = handle_command_line_query("test query")
            output = fake_out.getvalue()
        
        assert result == 0
        assert "Test response" in output
        mock_client.generate_response.assert_called_once_with(
            "test query", 
            interactions=[]
        )
        mock_save.assert_called_once()
    
    @patch('ask.cli.load_conversation_state')
    @patch('ask.cli.save_conversation_state')
    def test_clear_command(self, mock_save, mock_load):
        """Test the clear command"""
        mock_load.return_value = [{"query": "old", "response": "data"}]
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = handle_command_line_query("clear")
            output = fake_out.getvalue()
        
        assert result == 0
        assert "Conversation history cleared" in output
        mock_save.assert_called_once_with([])
    
    @patch('ask.cli.load_conversation_state')
    def test_conversation_command_empty(self, mock_load):
        """Test conversation command with no history"""
        mock_load.return_value = []
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = handle_command_line_query("c")
            output = fake_out.getvalue()
        
        assert result == 0
        assert "No conversation history found" in output
    
    @patch('ask.cli.load_conversation_state')
    def test_conversation_command_with_history(self, mock_load, sample_conversation):
        """Test conversation command with existing history"""
        mock_load.return_value = sample_conversation
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = handle_command_line_query("conversation")
            output = fake_out.getvalue()
        
        assert result == 0
        assert "What is Python?" in output
        assert "How do I install packages?" in output
    
    def test_help_command(self):
        """Test help command output"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = handle_command_line_query("help")
            output = fake_out.getvalue()
        
        assert result == 0
        assert "Ask CLI - Command Line Interface" in output
        assert "Available commands:" in output
        assert "clear" in output
        assert "conversation" in output
        assert "upload" in output
    
    @patch('ask.cli.InteractiveMode')
    def test_upload_command(self, mock_interactive_class):
        """Test upload command delegation"""
        mock_interactive = Mock()
        mock_interactive_class.return_value = mock_interactive
        
        result = handle_command_line_query("upload test.txt")
        
        assert result == 0
        mock_interactive.handle_upload_command.assert_called_once_with(["test.txt"])
    
    @patch('ask.cli.ClaudeClient')
    @patch('builtins.open', new_callable=mock_open, read_data="existing history\n")
    def test_history_file_append(self, mock_file, mock_client_class):
        """Test that queries are appended to history file"""
        mock_client = Mock()
        mock_client.generate_response.return_value = ("Response", [])
        mock_client_class.return_value = mock_client
        
        with patch('ask.cli.load_conversation_state', return_value=[]):
            with patch('ask.cli.save_conversation_state'):
                handle_command_line_query("test query")
        
        # Verify history file was opened for append
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called_with("test query\n")
    
    @patch('sys.argv', ['ask', '--help'])
    def test_main_help_flag(self):
        """Test main function with --help flag"""
        with patch('ask.cli.handle_command_line_query') as mock_handle:
            mock_handle.return_value = 0
            
            result = main()
            
            assert result == 0
            mock_handle.assert_called_once_with("help")
    
    @patch('sys.argv', ['ask', 'What is Python?'])
    def test_main_with_query(self):
        """Test main function with a query"""
        with patch('ask.cli.handle_command_line_query') as mock_handle:
            mock_handle.return_value = 0
            
            result = main()
            
            assert result == 0
            mock_handle.assert_called_once_with("What is Python?")
    
    @patch('sys.argv', ['ask'])
    @patch('ask.cli.InteractiveMode')
    def test_main_interactive_mode(self, mock_interactive_class):
        """Test main function entering interactive mode"""
        mock_interactive = Mock()
        mock_interactive_class.return_value = mock_interactive
        
        result = main()
        
        assert result == 0
        mock_interactive.run.assert_called_once()
    
    @patch('ask.cli.ClaudeClient')
    def test_keyboard_interrupt_handling(self, mock_client_class):
        """Test handling of keyboard interrupt"""
        mock_client = Mock()
        mock_client.generate_response.side_effect = KeyboardInterrupt()
        mock_client_class.return_value = mock_client
        
        with patch('ask.cli.load_conversation_state', return_value=[]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                result = handle_command_line_query("test")
                output = fake_out.getvalue()
        
        assert result == 1
        assert "Operation canceled" in output
    
    @patch('ask.cli.ClaudeClient')
    def test_general_exception_handling(self, mock_client_class):
        """Test handling of general exceptions"""
        mock_client = Mock()
        mock_client.generate_response.side_effect = Exception("Test error")
        mock_client_class.return_value = mock_client
        
        with patch('ask.cli.load_conversation_state', return_value=[]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                result = handle_command_line_query("test")
                output = fake_out.getvalue()
        
        assert result == 1
        assert "An error occurred" in output
        assert "Test error" in output
"""
Integration tests for variable system with interactive mode
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.modes.interactive import InteractiveMode
from ai.utils.variables import get_variable_manager, VariableManager


class TestVariableIntegration(unittest.TestCase):
    """Integration tests for variable system with interactive mode"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()
        
        # Set up variable manager with temp storage
        self.vm = VariableManager(self.temp_path)
        
        # Mock the global variable manager to use our test instance
        self.original_vm = get_variable_manager()
        
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
    
    @patch('ai.modes.interactive.ClaudeClient')
    @patch('ai.utils.variables._variable_manager')
    def test_interactive_variable_assignment(self, mock_vm, mock_client):
        """Test variable assignment through interactive mode"""
        mock_vm.process_input.return_value = ("Variable 'test' set to: value", True)
        
        # Create interactive mode instance
        interactive = InteractiveMode()
        
        # Test variable assignment
        result = interactive.process_input("test=value")
        
        # Should return True (continue) and call variable processing
        self.assertTrue(result)
        mock_vm.process_input.assert_called_once_with("test=value")
    
    @patch('ai.modes.interactive.ClaudeClient')
    @patch('ai.utils.variables._variable_manager')
    def test_interactive_variable_interpolation(self, mock_vm, mock_client):
        """Test variable interpolation through interactive mode"""
        mock_vm.process_input.return_value = ("Hello John", False)
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.generate_response.return_value = ("AI response", [])
        
        # Create interactive mode instance
        interactive = InteractiveMode()
        
        # Test variable interpolation
        with patch('ai.modes.interactive.Spinner'), \
             patch('ai.modes.interactive.print_response'), \
             patch('ai.modes.interactive.save_conversation_state'), \
             patch('ai.modes.interactive.append_to_conversation_log'):
            
            result = interactive.process_input("Hello name")
        
        # Should process variables and then send to AI
        self.assertTrue(result)
        mock_vm.process_input.assert_called_once_with("Hello name")
        mock_client_instance.generate_response.assert_called_once()
        
        # Check that the interpolated text was passed to AI
        call_args = mock_client_instance.generate_response.call_args[0]
        self.assertEqual(call_args[0], "Hello John")  # First argument should be the interpolated text
    
    @patch('ai.modes.interactive.ClaudeClient')
    @patch('ai.utils.variables._variable_manager')
    def test_interactive_vars_command(self, mock_vm, mock_client):
        """Test the 'vars' command in interactive mode"""
        mock_vm.list_variables.return_value = {"test": "value", "name": "John"}
        
        # Create interactive mode instance
        interactive = InteractiveMode()
        
        # Test vars command
        with patch('builtins.print') as mock_print:
            result = interactive.process_input("vars")
        
        # Should return True and print variables
        self.assertTrue(result)
        mock_vm.list_variables.assert_called_once()
        
        # Check that variables were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        self.assertIn("Stored variables:", print_calls)
    
    @patch('ai.modes.interactive.ClaudeClient')
    @patch('ai.utils.variables._variable_manager')
    def test_interactive_vars_command_empty(self, mock_vm, mock_client):
        """Test the 'vars' command when no variables exist"""
        mock_vm.list_variables.return_value = {}
        
        # Create interactive mode instance
        interactive = InteractiveMode()
        
        # Test vars command with no variables
        with patch('builtins.print') as mock_print:
            result = interactive.process_input("vars")
        
        # Should return True and print empty message
        self.assertTrue(result)
        mock_vm.list_variables.assert_called_once()
        
        # Check that empty message was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        self.assertIn("No variables stored", print_calls)
    
    def test_variable_persistence_real(self):
        """Test real variable persistence without mocks"""
        # Test with actual variable manager
        vm1 = VariableManager(self.temp_path)
        
        # Set variables
        result1, was_assignment1 = vm1.process_input("name=Alice")
        result2, was_assignment2 = vm1.process_input("age=25")
        
        self.assertTrue(was_assignment1)
        self.assertTrue(was_assignment2)
        
        # Create new manager (simulates restart)
        vm2 = VariableManager(self.temp_path)
        
        # Test interpolation
        result, was_assignment = vm2.process_input("Hello name, you are age years old")
        
        self.assertFalse(was_assignment)
        self.assertEqual(result, "Hello Alice, you are 25 years old")
    
    def test_complex_interpolation_scenarios(self):
        """Test complex variable interpolation scenarios"""
        vm = VariableManager(self.temp_path)
        
        # Set up variables
        vm.process_input("first=John")
        vm.process_input("last=Doe")
        vm.process_input("age=30")
        vm.process_input('hobbies=["reading", "coding", "hiking"]')
        
        # Test multiple interpolations
        test_cases = [
            ("first last", "John Doe"),
            ("first is age years old", "John is 30 years old"),
            ("first likes hobbies", "John likes ['reading', 'coding', 'hiking']"),
            ("Hello first last, age", "Hello John Doe, 30"),
            ("No variables here", "No variables here"),
            ("Mix of text and first", "Mix of text and John"),
        ]
        
        for input_text, expected in test_cases:
            result, was_assignment = vm.process_input(input_text)
            self.assertFalse(was_assignment, f"'{input_text}' should not be assignment")
            self.assertEqual(result, expected, f"Interpolation failed for '{input_text}'")
    
    def test_help_command_includes_variables(self):
        """Test that help command includes variable-related help"""
        interactive = InteractiveMode()
        
        with patch('builtins.print') as mock_print:
            result = interactive.process_input("help")
        
        self.assertTrue(result)
        
        # Check that variable help is included
        help_text = "\n".join([call[0][0] for call in mock_print.call_args_list])
        self.assertIn("vars", help_text)
        self.assertIn("var=value", help_text)
    
    def test_json_variables_integration(self):
        """Test JSON variables work properly in integration"""
        vm = VariableManager(self.temp_path)
        
        # Set JSON variables
        vm.process_input('config={"theme": "dark", "lang": "en"}')
        vm.process_input('users=[{"name": "Alice"}, {"name": "Bob"}]')
        vm.process_input("flag=true")
        vm.process_input("count=null")
        
        # Test interpolation with JSON
        result1, _ = vm.process_input("Current config")
        result2, _ = vm.process_input("Users: users")
        result3, _ = vm.process_input("Flag is flag")
        result4, _ = vm.process_input("Count: count")
        
        self.assertEqual(result1, "Current {'theme': 'dark', 'lang': 'en'}")
        self.assertEqual(result2, "Users: [{'name': 'Alice'}, {'name': 'Bob'}]")
        self.assertEqual(result3, "Flag is True")
        self.assertEqual(result4, "Count: None")
    
    def test_error_recovery(self):
        """Test error recovery in variable system"""
        vm = VariableManager(self.temp_path)
        
        # Test invalid assignments (should not crash)
        test_inputs = [
            "=invalid",  # No variable name
            "123=invalid",  # Invalid variable name
            "valid=works",  # This should work
            "",  # Empty input
            "just text",  # No assignment
        ]
        
        for input_text in test_inputs:
            try:
                result, was_assignment = vm.process_input(input_text)
                # Should not raise exception
                self.assertIsInstance(result, str)
                self.assertIsInstance(was_assignment, bool)
            except Exception as e:
                self.fail(f"Variable processing crashed on input '{input_text}': {e}")
        
        # Check that valid assignment worked
        self.assertEqual(vm.get_variable("valid"), "works")


if __name__ == '__main__':
    unittest.main(verbosity=2)
"""
Comprehensive test suite for the variable system (40 tests)
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.utils.variables import VariableManager


class TestVariableManager(unittest.TestCase):
    """Test suite for VariableManager with 40 comprehensive tests"""
    
    def setUp(self):
        """Set up a temporary storage file for each test"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()
        self.vm = VariableManager(self.temp_path)
    
    def tearDown(self):
        """Clean up temporary file after each test"""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
    
    # Basic Assignment Tests (Tests 1-10)
    
    def test_01_simple_string_assignment(self):
        """Test basic string variable assignment"""
        result, was_assignment = self.vm.process_input("name=John")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("name"), "John")
        self.assertIn("Variable 'name' set to: John", result)
    
    def test_02_simple_number_assignment(self):
        """Test basic number variable assignment"""
        result, was_assignment = self.vm.process_input("age=25")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("age"), 25)
    
    def test_03_json_number_assignment(self):
        """Test JSON number assignment"""
        result, was_assignment = self.vm.process_input("count=42")
        self.assertTrue(was_assignment)
        # Should be parsed as integer
        self.assertEqual(self.vm.get_variable("count"), 42)
    
    def test_04_json_array_assignment(self):
        """Test JSON array assignment"""
        result, was_assignment = self.vm.process_input('items=["apple", "banana", "cherry"]')
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("items"), ["apple", "banana", "cherry"])
    
    def test_05_json_object_assignment(self):
        """Test JSON object assignment"""
        result, was_assignment = self.vm.process_input('user={"name": "Alice", "age": 30}')
        self.assertTrue(was_assignment)
        expected = {"name": "Alice", "age": 30}
        self.assertEqual(self.vm.get_variable("user"), expected)
    
    def test_06_assignment_with_spaces(self):
        """Test assignment with spaces around equals sign"""
        result, was_assignment = self.vm.process_input("city = Paris")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("city"), "Paris")
    
    def test_07_assignment_with_multiple_spaces(self):
        """Test assignment with multiple spaces"""
        result, was_assignment = self.vm.process_input("country   =   France")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("country"), "France")
    
    def test_08_empty_string_assignment(self):
        """Test assignment of empty string"""
        result, was_assignment = self.vm.process_input("empty=")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("empty"), "")
    
    def test_09_assignment_with_equals_in_value(self):
        """Test assignment where value contains equals sign"""
        result, was_assignment = self.vm.process_input("equation=x=y+1")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("equation"), "x=y+1")
    
    def test_10_boolean_assignment(self):
        """Test boolean assignment"""
        result, was_assignment = self.vm.process_input("active=true")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("active"), True)
    
    # Variable Retrieval Tests (Tests 11-15)
    
    def test_11_get_existing_variable(self):
        """Test retrieving an existing variable"""
        self.vm.set_variable("test", "value")
        self.assertEqual(self.vm.get_variable("test"), "value")
    
    def test_12_get_nonexistent_variable(self):
        """Test retrieving a non-existent variable"""
        self.assertIsNone(self.vm.get_variable("nonexistent"))
    
    def test_13_list_empty_variables(self):
        """Test listing variables when none exist"""
        variables = self.vm.list_variables()
        self.assertEqual(variables, {})
    
    def test_14_list_multiple_variables(self):
        """Test listing multiple variables"""
        self.vm.set_variable("a", "1")
        self.vm.set_variable("b", "2")
        variables = self.vm.list_variables()
        expected = {"a": "1", "b": "2"}
        self.assertEqual(variables, expected)
    
    def test_15_delete_existing_variable(self):
        """Test deleting an existing variable"""
        self.vm.set_variable("temp", "delete_me")
        result = self.vm.delete_variable("temp")
        self.assertTrue(result)
        self.assertIsNone(self.vm.get_variable("temp"))
    
    # Interpolation Tests (Tests 16-25)
    
    def test_16_simple_interpolation(self):
        """Test basic variable interpolation"""
        self.vm.set_variable("name", "Alice")
        result = self.vm.interpolate_variables("Hello name")
        self.assertEqual(result, "Hello Alice")
    
    def test_17_multiple_interpolation(self):
        """Test multiple variable interpolation in one string"""
        self.vm.set_variable("first", "John")
        self.vm.set_variable("last", "Doe")
        result = self.vm.interpolate_variables("first last")
        self.assertEqual(result, "John Doe")
    
    def test_18_interpolation_with_punctuation(self):
        """Test interpolation with punctuation"""
        self.vm.set_variable("city", "Paris")
        result = self.vm.interpolate_variables("I love city!")
        self.assertEqual(result, "I love Paris!")
    
    def test_19_interpolation_nonexistent_variable(self):
        """Test interpolation with non-existent variable"""
        result = self.vm.interpolate_variables("Hello unknown")
        self.assertEqual(result, "Hello unknown")
    
    def test_20_interpolation_mixed_content(self):
        """Test interpolation mixed with regular text"""
        self.vm.set_variable("count", "5")
        result = self.vm.interpolate_variables("There are count apples and 3 oranges")
        self.assertEqual(result, "There are 5 apples and 3 oranges")
    
    def test_21_interpolation_at_start(self):
        """Test interpolation at start of string"""
        self.vm.set_variable("greeting", "Hello")
        result = self.vm.interpolate_variables("greeting world")
        self.assertEqual(result, "Hello world")
    
    def test_22_interpolation_at_end(self):
        """Test interpolation at end of string"""
        self.vm.set_variable("name", "Bob")
        result = self.vm.interpolate_variables("Hello name")
        self.assertEqual(result, "Hello Bob")
    
    def test_23_interpolation_array_variable(self):
        """Test interpolation with array variable"""
        self.vm.set_variable("items", ["a", "b", "c"])
        result = self.vm.interpolate_variables("The items are")
        self.assertEqual(result, "The ['a', 'b', 'c'] are")
    
    def test_24_interpolation_object_variable(self):
        """Test interpolation with object variable"""
        self.vm.set_variable("user", {"name": "Alice"})
        result = self.vm.interpolate_variables("User: user")
        self.assertEqual(result, "User: {'name': 'Alice'}")
    
    def test_25_interpolation_with_numbers(self):
        """Test interpolation with numeric variables"""
        self.vm.set_variable("num", "42")
        result = self.vm.interpolate_variables("The answer is num")
        self.assertEqual(result, "The answer is 42")
    
    # Persistence Tests (Tests 26-30)
    
    def test_26_save_and_load_variables(self):
        """Test saving and loading variables from file"""
        self.vm.set_variable("persistent", "value")
        
        # Create new manager with same file
        vm2 = VariableManager(self.temp_path)
        self.assertEqual(vm2.get_variable("persistent"), "value")
    
    def test_27_persistence_after_multiple_operations(self):
        """Test persistence after multiple variable operations"""
        self.vm.set_variable("a", "1")
        self.vm.set_variable("b", "2")
        self.vm.delete_variable("a")
        
        vm2 = VariableManager(self.temp_path)
        self.assertIsNone(vm2.get_variable("a"))
        self.assertEqual(vm2.get_variable("b"), "2")
    
    def test_28_corrupted_file_handling(self):
        """Test handling of corrupted storage file"""
        # Write invalid JSON to file
        with open(self.temp_path, 'w') as f:
            f.write("invalid json content")
        
        # Should create new manager without errors
        vm = VariableManager(self.temp_path)
        self.assertEqual(vm.list_variables(), {})
    
    def test_29_missing_file_handling(self):
        """Test handling when storage file doesn't exist"""
        os.unlink(self.temp_path)
        vm = VariableManager(self.temp_path)
        self.assertEqual(vm.list_variables(), {})
    
    def test_30_file_permissions(self):
        """Test file creation with proper permissions"""
        self.vm.set_variable("test", "value")
        self.assertTrue(os.path.exists(self.temp_path))
        # File should be readable and writable by owner
        stat_info = os.stat(self.temp_path)
        self.assertTrue(stat_info.st_mode & 0o600)
    
    # Edge Cases and Error Handling (Tests 31-35)
    
    def test_31_invalid_variable_names(self):
        """Test invalid variable name handling"""
        result, was_assignment = self.vm.process_input("123=value")
        self.assertFalse(was_assignment)
        result, was_assignment = self.vm.process_input("-name=value")
        self.assertFalse(was_assignment)
    
    def test_32_special_characters_in_values(self):
        """Test special characters in variable values"""
        result, was_assignment = self.vm.process_input("special=@#$%^&*()")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("special"), "@#$%^&*()")
    
    def test_33_unicode_values(self):
        """Test unicode characters in values"""
        result, was_assignment = self.vm.process_input("unicode=héllo wörld 🌍")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("unicode"), "héllo wörld 🌍")
    
    def test_34_very_long_values(self):
        """Test very long variable values"""
        long_value = "x" * 10000
        result, was_assignment = self.vm.process_input(f"long={long_value}")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("long"), long_value)
    
    def test_35_clear_all_variables(self):
        """Test clearing all variables"""
        self.vm.set_variable("a", "1")
        self.vm.set_variable("b", "2")
        self.vm.clear_variables()
        self.assertEqual(self.vm.list_variables(), {})
    
    # Complex JSON Tests (Tests 36-40)
    
    def test_36_nested_json_objects(self):
        """Test nested JSON object assignment"""
        complex_json = '{"user": {"profile": {"name": "Alice", "settings": {"theme": "dark"}}}}'
        result, was_assignment = self.vm.process_input(f"config={complex_json}")
        self.assertTrue(was_assignment)
        expected = {"user": {"profile": {"name": "Alice", "settings": {"theme": "dark"}}}}
        self.assertEqual(self.vm.get_variable("config"), expected)
    
    def test_37_json_array_with_objects(self):
        """Test JSON array containing objects"""
        json_array = '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'
        result, was_assignment = self.vm.process_input(f"users={json_array}")
        self.assertTrue(was_assignment)
        expected = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        self.assertEqual(self.vm.get_variable("users"), expected)
    
    def test_38_json_with_null_values(self):
        """Test JSON with null values"""
        result, was_assignment = self.vm.process_input('nullable={"value": null, "active": false}')
        self.assertTrue(was_assignment)
        expected = {"value": None, "active": False}
        self.assertEqual(self.vm.get_variable("nullable"), expected)
    
    def test_39_invalid_json_fallback(self):
        """Test invalid JSON falls back to string"""
        result, was_assignment = self.vm.process_input('invalid={"incomplete": json')
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("invalid"), '{"incomplete": json')
    
    def test_40_process_input_comprehensive(self):
        """Test comprehensive process_input functionality"""
        # Test assignment
        result, was_assignment = self.vm.process_input("test=hello")
        self.assertTrue(was_assignment)
        self.assertIn("Variable 'test' set to: hello", result)
        
        # Test interpolation
        result, was_assignment = self.vm.process_input("Say test to the world")
        self.assertFalse(was_assignment)
        self.assertEqual(result, "Say hello to the world")
        
        # Test non-variable text
        result, was_assignment = self.vm.process_input("Just plain text")
        self.assertFalse(was_assignment)
        self.assertEqual(result, "Just plain text")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
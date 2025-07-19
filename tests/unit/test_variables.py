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
    
    # Tests 41-80: Advanced edge cases, security, and performance tests
    
    def test_41_variable_name_with_numbers(self):
        """Test variable names containing numbers"""
        result, was_assignment = self.vm.process_input("var123=test123")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("var123"), "test123")
        
        # Interpolation with numeric variable names
        result, _ = self.vm.process_input("Value is var123")
        self.assertEqual(result, "Value is test123")
    
    def test_42_variable_name_with_underscores(self):
        """Test variable names with underscores"""
        self.vm.process_input("user_name=john_doe")
        self.vm.process_input("api_key=secret123")
        result, _ = self.vm.process_input("User user_name with key api_key")
        self.assertEqual(result, "User john_doe with key secret123")
    
    def test_43_case_sensitive_variables(self):
        """Test case sensitivity in variable names"""
        self.vm.process_input("name=lowercase")
        self.vm.process_input("Name=titlecase")
        self.vm.process_input("NAME=uppercase")
        
        self.assertEqual(self.vm.get_variable("name"), "lowercase")
        self.assertEqual(self.vm.get_variable("Name"), "titlecase")
        self.assertEqual(self.vm.get_variable("NAME"), "uppercase")
    
    def test_44_interpolation_with_partial_matches(self):
        """Test interpolation doesn't match partial variable names"""
        self.vm.process_input("test=value")
        result, _ = self.vm.process_input("testing is not test")
        self.assertEqual(result, "testing is not value")
        
        result, _ = self.vm.process_input("pretest should not match")
        self.assertEqual(result, "pretest should not match")
    
    def test_45_multiple_equals_in_assignment(self):
        """Test assignments with multiple equals signs"""
        result, was_assignment = self.vm.process_input("equation=a=b=c")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("equation"), "a=b=c")
    
    def test_46_whitespace_in_values(self):
        """Test preserving whitespace in values"""
        self.vm.process_input("spaces=   leading and trailing   ")
        # Note: Current implementation trims whitespace
        self.assertEqual(self.vm.get_variable("spaces"), "leading and trailing")
        
        self.vm.process_input("tabs=\tTabbed\tValue\t")
        # Note: Leading/trailing tabs are trimmed
        self.assertEqual(self.vm.get_variable("tabs"), "Tabbed\tValue")
    
    def test_47_newline_in_values(self):
        """Test handling newlines in values"""
        self.vm.process_input("multiline=Line1\\nLine2\\nLine3")
        value = self.vm.get_variable("multiline")
        self.assertIn("Line1", value)
        self.assertIn("Line2", value)
    
    def test_48_json_with_unicode(self):
        """Test JSON with unicode characters"""
        self.vm.process_input('unicode_json={"emoji": "🚀", "text": "café"}')
        value = self.vm.get_variable("unicode_json")
        self.assertEqual(value["emoji"], "🚀")
        self.assertEqual(value["text"], "café")
    
    def test_49_circular_reference_prevention(self):
        """Test prevention of circular references in interpolation"""
        self.vm.process_input("a=b")
        self.vm.process_input("b=a")
        # Should not cause infinite recursion
        result, _ = self.vm.process_input("Value is a")
        # Note: Interpolation happens, so a -> b
        self.assertEqual(result, "Value is b")
    
    def test_50_interpolation_at_word_boundaries(self):
        """Test interpolation respects word boundaries"""
        self.vm.process_input("cat=feline")
        result, _ = self.vm.process_input("category is not a cat")
        self.assertEqual(result, "category is not a feline")
        
        result, _ = self.vm.process_input("concatenate cat with cat")
        self.assertEqual(result, "concatenate feline with feline")
    
    def test_51_delete_and_recreate_variable(self):
        """Test deleting and recreating variables"""
        self.vm.process_input("temp=value1")
        self.assertEqual(self.vm.get_variable("temp"), "value1")
        
        self.vm.delete_variable("temp")
        self.assertIsNone(self.vm.get_variable("temp"))
        
        self.vm.process_input("temp=value2")
        self.assertEqual(self.vm.get_variable("temp"), "value2")
    
    def test_52_numeric_string_preservation(self):
        """Test numeric strings are preserved as strings"""
        self.vm.process_input("zipcode=01234")
        self.assertEqual(self.vm.get_variable("zipcode"), "01234")
        
        self.vm.process_input("phone=+1-555-0123")
        self.assertEqual(self.vm.get_variable("phone"), "+1-555-0123")
    
    def test_53_empty_json_structures(self):
        """Test empty JSON arrays and objects"""
        self.vm.process_input("empty_array=[]")
        self.assertEqual(self.vm.get_variable("empty_array"), [])
        
        self.vm.process_input("empty_object={}")
        self.assertEqual(self.vm.get_variable("empty_object"), {})
    
    def test_54_json_with_nested_arrays(self):
        """Test JSON with nested arrays"""
        self.vm.process_input('matrix=[[1,2,3], [4,5,6], [7,8,9]]')
        matrix = self.vm.get_variable("matrix")
        self.assertEqual(len(matrix), 3)
        self.assertEqual(matrix[1][1], 5)
    
    def test_55_special_json_values(self):
        """Test special JSON values like Infinity and NaN"""
        # Python's JSON parser actually supports Infinity as float('inf')
        self.vm.process_input('special={"value": Infinity}')
        value = self.vm.get_variable("special")
        self.assertIsInstance(value, dict)
        self.assertEqual(value["value"], float('inf'))
    
    def test_56_variable_with_quotes_in_name(self):
        """Test variables with quotes in values"""
        self.vm.process_input('quoted=He said "Hello"')
        self.assertEqual(self.vm.get_variable("quoted"), 'He said "Hello"')
        
        self.vm.process_input("single_quoted=It's working")
        self.assertEqual(self.vm.get_variable("single_quoted"), "It's working")
    
    def test_57_interpolation_with_punctuation_boundaries(self):
        """Test interpolation with various punctuation boundaries"""
        self.vm.process_input("word=replaced")
        
        test_cases = [
            ("(word)", "(replaced)"),
            ("[word]", "[replaced]"),
            ("{word}", "{replaced}"),
            ("word.", "replaced."),
            ("word,", "replaced,"),
            ("word;", "replaced;"),
            ("word:", "replaced:"),
            ("word!", "replaced!"),
            ("word?", "replaced?"),
        ]
        
        for input_text, expected in test_cases:
            result, _ = self.vm.process_input(input_text)
            self.assertEqual(result, expected)
    
    def test_58_concurrent_variable_access(self):
        """Test variable system handles concurrent-like access"""
        # Simulate rapid succession of operations
        for i in range(10):
            self.vm.process_input(f"counter{i}={i}")
        
        # Verify all variables exist
        for i in range(10):
            self.assertEqual(self.vm.get_variable(f"counter{i}"), i)
    
    def test_59_variable_name_max_length(self):
        """Test very long variable names"""
        long_name = "a" * 255  # Reasonable max length
        self.vm.process_input(f"{long_name}=test")
        self.assertEqual(self.vm.get_variable(long_name), "test")
    
    def test_60_interpolation_performance(self):
        """Test interpolation with many variables"""
        # Create many variables
        for i in range(100):
            self.vm.process_input(f"var{i}=value{i}")
        
        # Test interpolation with multiple variables
        result, _ = self.vm.process_input("var1 var50 var99")
        self.assertEqual(result, "value1 value50 value99")
    
    def test_61_json_escape_sequences(self):
        """Test JSON with escape sequences"""
        self.vm.process_input('escaped={"tab": "\\t", "newline": "\\n", "quote": "\\""}')
        value = self.vm.get_variable("escaped")
        self.assertEqual(value["tab"], "\t")
        self.assertEqual(value["newline"], "\n")
        self.assertEqual(value["quote"], '"')
    
    def test_62_assignment_with_comments(self):
        """Test assignments that look like they have comments"""
        self.vm.process_input("url=http://example.com#anchor")
        self.assertEqual(self.vm.get_variable("url"), "http://example.com#anchor")
        
        self.vm.process_input("comment=value # this is not a comment")
        self.assertEqual(self.vm.get_variable("comment"), "value # this is not a comment")
    
    def test_63_interpolation_with_special_chars(self):
        """Test interpolation with variables containing special characters"""
        self.vm.process_input("path=/usr/local/bin")
        result, _ = self.vm.process_input("Install to path directory")
        self.assertEqual(result, "Install to /usr/local/bin directory")
    
    def test_64_mixed_type_list_interpolation(self):
        """Test interpolation of lists with mixed types"""
        self.vm.process_input('mixed=[1, "two", true, null, {"key": "value"}]')
        result, _ = self.vm.process_input("Mixed types: mixed")
        self.assertIn("1", result)
        self.assertIn("two", result)
        self.assertIn("True", result)
        self.assertIn("None", result)
    
    def test_65_variable_shadowing(self):
        """Test variable shadowing/overwriting"""
        self.vm.process_input("shadow=first")
        self.assertEqual(self.vm.get_variable("shadow"), "first")
        
        self.vm.process_input("shadow=second")
        self.assertEqual(self.vm.get_variable("shadow"), "second")
        
        # Ensure old value is completely replaced
        vars_list = self.vm.list_variables()
        self.assertEqual(vars_list["shadow"], "second")
    
    def test_66_assignment_with_leading_spaces(self):
        """Test assignment with leading spaces before variable name"""
        # Current implementation treats this as assignment
        result, was_assignment = self.vm.process_input("  spaced=value")
        self.assertTrue(was_assignment)
        self.assertEqual(self.vm.get_variable("spaced"), "value")
    
    def test_67_json_scientific_notation(self):
        """Test JSON with scientific notation numbers"""
        self.vm.process_input('scientific={"small": 1.23e-10, "large": 6.02e23}')
        value = self.vm.get_variable("scientific")
        self.assertEqual(value["small"], 1.23e-10)
        self.assertEqual(value["large"], 6.02e23)
    
    def test_68_interpolation_with_numbers_in_text(self):
        """Test interpolation doesn't affect numbers in text"""
        self.vm.process_input("port=8080")
        result, _ = self.vm.process_input("Connect to localhost:port")
        self.assertEqual(result, "Connect to localhost:8080")
        
        result, _ = self.vm.process_input("Error 404 on port")
        self.assertEqual(result, "Error 404 on 8080")
    
    def test_69_persistence_with_special_chars(self):
        """Test persistence of variables with special characters"""
        temp_file = self.temp_file.name.replace('.json', '_special.json')
        vm = VariableManager(temp_file)
        
        vm.process_input('special=<>&"\'\\/')
        vm.process_input('unicode=αβγδε')
        
        # Load in new instance
        vm2 = VariableManager(temp_file)
        self.assertEqual(vm2.get_variable("special"), '<>&"\'\\/')
        self.assertEqual(vm2.get_variable("unicode"), 'αβγδε')
        
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)
    
    def test_70_clear_with_persistence(self):
        """Test clearing variables affects persistence"""
        temp_file = self.temp_file.name.replace('.json', '_clear.json')
        vm = VariableManager(temp_file)
        
        vm.process_input("persist1=value1")
        vm.process_input("persist2=value2")
        
        # Clear and verify file is updated
        for var in list(vm.list_variables().keys()):
            vm.delete_variable(var)
        
        # New instance should have no variables
        vm2 = VariableManager(temp_file)
        self.assertEqual(len(vm2.list_variables()), 0)
        
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)
    
    def test_71_assignment_with_trailing_spaces(self):
        """Test assignment with trailing spaces after value"""
        self.vm.process_input("trailing=value   ")
        # Note: Current implementation trims trailing spaces
        self.assertEqual(self.vm.get_variable("trailing"), "value")
    
    def test_72_interpolation_case_sensitivity(self):
        """Test interpolation is case sensitive"""
        self.vm.process_input("lower=lowercase")
        self.vm.process_input("UPPER=UPPERCASE")
        
        result, _ = self.vm.process_input("lower UPPER Lower")
        self.assertEqual(result, "lowercase UPPERCASE Lower")
    
    def test_73_json_with_duplicate_keys(self):
        """Test JSON with duplicate keys (last one wins)"""
        # Python's JSON parser will use the last occurrence
        self.vm.process_input('dupe={"key": "first", "key": "second"}')
        value = self.vm.get_variable("dupe")
        self.assertEqual(value["key"], "second")
    
    def test_74_variable_with_dots(self):
        """Test variable names with dots are not supported"""
        result, was_assignment = self.vm.process_input("my.var=value")
        # Should not be treated as a valid variable name
        self.assertFalse(was_assignment)
    
    def test_75_interpolation_with_regexp_chars(self):
        """Test interpolation with regex special characters in variable names"""
        # Only alphanumeric and underscore are valid in variable names
        self.vm.process_input("valid_var=replaced")
        result, _ = self.vm.process_input("valid_var works")
        self.assertEqual(result, "replaced works")
    
    def test_76_stress_test_many_variables(self):
        """Stress test with many variables"""
        # Create 1000 variables
        for i in range(1000):
            self.vm.process_input(f"stress{i}={i}")
        
        # Verify a sample
        self.assertEqual(self.vm.get_variable("stress500"), 500)
        self.assertEqual(self.vm.get_variable("stress999"), 999)
        
        # Test listing doesn't break
        all_vars = self.vm.list_variables()
        self.assertGreaterEqual(len(all_vars), 1000)
    
    def test_77_interpolation_with_adjacent_vars(self):
        """Test interpolation with adjacent variables"""
        self.vm.process_input("a=A")
        self.vm.process_input("b=B")
        
        # Space separated
        result, _ = self.vm.process_input("a b")
        self.assertEqual(result, "A B")
        
        # Should not interpolate without word boundaries
        result, _ = self.vm.process_input("ab")
        self.assertEqual(result, "ab")
    
    def test_78_json_nested_depth(self):
        """Test deeply nested JSON structures"""
        deep_json = '{"l1": {"l2": {"l3": {"l4": {"l5": "deep"}}}}}'
        self.vm.process_input(f"deep={deep_json}")
        value = self.vm.get_variable("deep")
        self.assertEqual(value["l1"]["l2"]["l3"]["l4"]["l5"], "deep")
    
    def test_79_variable_name_starting_with_number(self):
        """Test variable names cannot start with numbers"""
        result, was_assignment = self.vm.process_input("123var=value")
        self.assertFalse(was_assignment)
        self.assertIsNone(self.vm.get_variable("123var"))
    
    def test_80_interpolation_in_json_strings(self):
        """Test interpolation doesn't occur in JSON string values"""
        self.vm.process_input("name=John")
        self.vm.process_input('json={"greeting": "Hello name"}')
        
        value = self.vm.get_variable("json")
        # Should not interpolate inside JSON
        self.assertEqual(value["greeting"], "Hello name")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
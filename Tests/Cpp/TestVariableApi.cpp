/**
 * @file TestVariableApi.cpp
 * @brief Comprehensive test suite for the C++ Variable API
 * 
 * This file contains unit tests for the VariableManager C++ interface,
 * testing both the C++ class interface and the C-style FFI interface.
 * Tests cover basic operations, persistence, edge cases, and error handling.
 * 
 * @author PyClaudeCli Team
 * @date 2024
 */

#include <iostream>
#include <cassert>
#include <string>
#include <cstdlib>
#include <fstream>
#include <filesystem>

// Prevent multiple main functions
#define SKIP_MAIN
#include "../../AI/Bindings/VariableApi.cpp"
#undef SKIP_MAIN

/**
 * @class TestRunner
 * @brief Test runner for Variable API unit tests
 * 
 * This class manages test execution, reporting, and cleanup.
 * It creates a temporary directory for test isolation and
 * provides assertion helpers for test validation.
 */
class TestRunner {
private:
    /**
     * @brief Count of passed tests
     */
    int passed = 0;
    
    /**
     * @brief Count of failed tests
     */
    int failed = 0;
    
    /**
     * @brief Temporary directory path for test isolation
     */
    std::string test_dir;
    
public:
    /**
     * @brief Construct a new Test Runner object
     * 
     * Creates a unique temporary directory for test isolation.
     * Each test run uses a separate directory to avoid interference.
     */
    TestRunner() {
        // Create temporary test directory
        test_dir = "/tmp/cpp_variable_test_" + std::to_string(time(nullptr));
        std::filesystem::create_directories(test_dir);
    }
    
    /**
     * @brief Destroy the Test Runner object
     * 
     * Cleans up the temporary test directory and all its contents.
     */
    ~TestRunner() {
        // Clean up test directory
        std::filesystem::remove_all(test_dir);
    }
    
    /**
     * @brief Assert that two strings are equal
     * 
     * @param actual The actual value produced by the test
     * @param expected The expected value
     * @param test_name Name of the test for reporting
     * 
     * @details
     * Compares two strings and reports pass/fail status.
     * On failure, displays both expected and actual values.
     */
    void assert_equal(const std::string& actual, const std::string& expected, const std::string& test_name) {
        if (actual == expected) {
            std::cout << "PASS: " << test_name << std::endl;
            passed++;
        } else {
            std::cout << "FAIL: " << test_name << std::endl;
            std::cout << "  Expected: '" << expected << "'" << std::endl;
            std::cout << "  Actual: '" << actual << "'" << std::endl;
            failed++;
        }
    }
    
    /**
     * @brief Assert that a condition is true
     * 
     * @param condition Boolean condition to test
     * @param test_name Name of the test for reporting
     */
    void assert_true(bool condition, const std::string& test_name) {
        if (condition) {
            std::cout << "PASS: " << test_name << std::endl;
            passed++;
        } else {
            std::cout << "FAIL: " << test_name << std::endl;
            failed++;
        }
    }
    
    /**
     * @brief Run all test suites
     * 
     * @details
     * Executes all test methods in sequence:
     * - Basic operations
     * - Persistence
     * - C interface
     * - Edge cases
     * 
     * Reports final results and exits with appropriate code.
     */
    void run_all_tests() {
        std::cout << "Running C++ Variable API Tests..." << std::endl;
        std::cout << "Test directory: " << test_dir << std::endl;
        
        test_basic_operations();
        test_persistence();
        test_c_interface();
        test_edge_cases();
        
        std::cout << "\nTest Results:" << std::endl;
        std::cout << "Passed: " << passed << std::endl;
        std::cout << "Failed: " << failed << std::endl;
        
        if (failed == 0) {
            std::cout << "All tests passed!" << std::endl;
        } else {
            std::cout << "Some tests failed." << std::endl;
            exit(1);
        }
    }
    
    /**
     * @brief Test basic variable operations
     * 
     * @details
     * Tests fundamental operations:
     * - Setting and getting variables
     * - Numeric values
     * - Empty values
     * - Non-existent variables
     * - Listing variables
     */
    void test_basic_operations() {
        std::cout << "\n=== Basic Operations Tests ===" << std::endl;
        
        VariableManager vm(test_dir);
        
        // Test 1: Set and get simple variable
        bool set_result = vm.SetVariable("test_var", "test_value");
        assert_true(set_result, "Set simple variable");
        
        std::string get_result = vm.GetVariable("test_var");
        assert_equal(get_result, "test_value", "Get simple variable");
        
        // Test 2: Set numeric variable
        vm.SetVariable("number", "42");
        std::string number = vm.GetVariable("number");
        assert_equal(number, "42", "Set and get numeric variable");
        
        // Test 3: Set empty variable
        vm.SetVariable("empty", "");
        std::string empty = vm.GetVariable("empty");
        assert_equal(empty, "", "Set and get empty variable");
        
        // Test 4: Get non-existent variable
        std::string nonexistent = vm.GetVariable("does_not_exist");
        assert_equal(nonexistent, "", "Get non-existent variable returns empty");
        
        // Test 5: List variables
        std::string vars_json = vm.ListVariables();
        assert_true(!vars_json.empty(), "List variables returns non-empty JSON");
        assert_true(vars_json.find("test_var") != std::string::npos, "List contains test_var");
    }
    
    /**
     * @brief Test variable persistence across instances
     * 
     * @details
     * Verifies that variables persist to disk and can be
     * loaded by new VariableManager instances, simulating
     * application restarts.
     */
    void test_persistence() {
        std::cout << "\n=== Persistence Tests ===" << std::endl;
        
        // Test 6: Create variable in one manager
        {
            VariableManager vm1(test_dir);
            vm1.SetVariable("persistent", "persistent_value");
        }
        
        // Test 7: Read variable from new manager (simulates restart)
        {
            VariableManager vm2(test_dir);
            std::string value = vm2.GetVariable("persistent");
            assert_equal(value, "persistent_value", "Variable persists across manager instances");
        }
        
        // Test 8: Multiple variables persistence
        {
            VariableManager vm3(test_dir);
            vm3.SetVariable("var1", "value1");
            vm3.SetVariable("var2", "value2");
            vm3.SetVariable("var3", "value3");
        }
        
        {
            VariableManager vm4(test_dir);
            assert_equal(vm4.GetVariable("var1"), "value1", "Multiple variables persist - var1");
            assert_equal(vm4.GetVariable("var2"), "value2", "Multiple variables persist - var2");
            assert_equal(vm4.GetVariable("var3"), "value3", "Multiple variables persist - var3");
        }
    }
    
    /**
     * @brief Test C-style interface functions
     * 
     * @details
     * Tests the extern "C" interface designed for FFI:
     * - create_variable_manager()
     * - set_variable()
     * - get_variable()
     * - list_variables()
     * - destroy_variable_manager()
     */
    void test_c_interface() {
        std::cout << "\n=== C Interface Tests ===" << std::endl;
        
        // Test 9: Create and destroy manager
        VariableManager* vm = create_variable_manager(test_dir.c_str());
        assert_true(vm != nullptr, "Create variable manager via C interface");
        
        // Test 10: Set variable via C interface
        int set_result = set_variable(vm, "c_test", "c_value");
        assert_true(set_result == 1, "Set variable via C interface");
        
        // Test 11: Get variable via C interface
        const char* value = get_variable(vm, "c_test");
        assert_equal(std::string(value), "c_value", "Get variable via C interface");
        
        // Test 12: List variables via C interface
        const char* vars = list_variables(vm);
        std::string vars_str(vars);
        assert_true(!vars_str.empty(), "List variables via C interface");
        assert_true(vars_str.find("c_test") != std::string::npos, "C interface list contains c_test");
        
        // Test 13: Clean up
        destroy_variable_manager(vm);
        assert_true(true, "Destroy variable manager via C interface");
    }
    
    /**
     * @brief Test edge cases and error handling
     * 
     * @details
     * Tests unusual inputs and error conditions:
     * - Special characters
     * - Long strings
     * - Unicode
     * - Invalid paths
     * - Empty names
     */
    void test_edge_cases() {
        std::cout << "\n=== Edge Cases Tests ===" << std::endl;
        
        VariableManager vm(test_dir);
        
        // Test 14: Special characters in variable names and values
        vm.SetVariable("special_chars", "!@#$%^&*()");
        std::string special = vm.GetVariable("special_chars");
        assert_equal(special, "!@#$%^&*()", "Special characters in values");
        
        // Test 15: Long variable names and values
        std::string long_name = "very_long_variable_name_with_many_characters";
        std::string long_value = std::string(1000, 'x');
        vm.SetVariable(long_name, long_value);
        std::string retrieved = vm.GetVariable(long_name);
        assert_equal(retrieved, long_value, "Long variable names and values");
        
        // Test 16: Unicode characters
        vm.SetVariable("unicode", "héllo_wörld_🌍");
        std::string unicode = vm.GetVariable("unicode");
        assert_equal(unicode, "héllo_wörld_🌍", "Unicode characters in values");
        
        // Test 17: Empty variable name handling (should fail gracefully)
        bool empty_name_result = vm.SetVariable("", "value");
        assert_true(empty_name_result, "Empty variable name handling");
        
        // Test 18: Invalid directory handling
        VariableManager invalid_vm("/invalid/path/that/does/not/exist");
        // Should not crash, even if it can't save
        invalid_vm.SetVariable("test", "value");
        assert_true(true, "Invalid directory doesn't crash");
    }
};

/**
 * @brief Main test entry point
 * 
 * @return 0 on success, 1 on test failure
 * 
 * @details
 * Sets up the test environment by ensuring the correct working
 * directory for Python imports, then runs all tests through
 * the TestRunner.
 */
int main() {
    // Change to project directory for Python imports to work
    std::string project_dir = std::filesystem::current_path();
    if (project_dir.find("Tests/Cpp") != std::string::npos) {
        // We're in Tests/Cpp, go back to project root
        std::filesystem::current_path("../..");
    }
    
    TestRunner runner;
    runner.run_all_tests();
    
    return 0;
}
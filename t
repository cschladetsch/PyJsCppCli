#!/usr/bin/env bash
# Comprehensive test suite for PyClaudeCli Variable System

# Source common utilities
source "$(dirname "$0")/Scripts/common.sh"

check_project_root

# Counters
declare -i TESTS_PASSED=0
declare -i TESTS_FAILED=0
declare -i TOTAL_TESTS=0

print_header "PyClaudeCli Variable System Test Suite" "Comprehensive testing with 80+ tests"

# Function to run test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="${3:-0}"
    
    show_progress "Running: $test_name"
    echo "Command: $test_command"
    
    set +e  # Temporarily disable exit on error
    eval "$test_command"
    local actual_exit_code=$?
    set -e  # Re-enable exit on error
    
    if [[ $actual_exit_code -eq $expected_exit_code ]]; then
        log_success "PASSED: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_error "FAILED: $test_name (exit code: $actual_exit_code, expected: $expected_exit_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

# Function to test variable functionality manually
test_variable_functionality() {
    log_test "Testing Variable System Functionality"
    
    PYTHONPATH=. python3 -c "
import sys
sys.path.append('.')
from AI.Utils.variables import VariableManager
import tempfile
import os

# Use temp file for testing
temp_file = '/tmp/test_variables_' + str(os.getpid()) + '.json'
vm = VariableManager(temp_file)

print('Testing basic assignment...')
result1, was_assignment1 = vm.process_input('name=TestUser')
assert was_assignment1, 'Assignment should return True'
assert 'TestUser' in result1, 'Result should contain value'

print('Testing interpolation...')
result2, was_assignment2 = vm.process_input('Hello name, welcome!')
assert not was_assignment2, 'Interpolation should not be assignment'
assert result2 == 'Hello TestUser, welcome!', f'Expected interpolation, got: {result2}'

print('Testing persistence...')
vm2 = VariableManager(temp_file)
result3, was_assignment3 = vm2.process_input('User name logged in')
assert not was_assignment3, 'Should not be assignment'
assert result3 == 'User TestUser logged in', f'Persistence failed, got: {result3}'

print('Testing JSON...')
vm.process_input('data=[\"item1\", \"item2\"]')
result4, _ = vm.process_input('Data contains data items')
assert 'item1' in result4 and 'item2' in result4, f'JSON interpolation failed: {result4}'

# Cleanup
os.unlink(temp_file)
print('✅ All functionality tests passed!')
"
}

# Function to check file existence
check_files() {
    echo -e "\n${YELLOW}📁 Checking Required Files${NC}"
    
    local files=(
        "AI/Utils/variables.py"
        "AI/Bindings/VariableApi.cpp"
        "Tests/Unit/test_variables.py"
        "Tests/Integration/test_variable_integration.py"
        "Tests/Cpp/TestVariableApi.cpp"
        "CMakeLists.txt"
        "Doxyfile"
        "b"
        "r"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅ Found: $file${NC}"
        else
            echo -e "${RED}❌ Missing: $file${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    done
}

# Function to test build system
test_build_system() {
    echo -e "\n${YELLOW}🔨 Testing Build System${NC}"
    
    # Clean build
    if [ -d "build" ]; then
        rm -rf build
        echo "Cleaned existing build directory"
    fi
    
    # Test CMake configuration
    mkdir -p build
    cd build
    
    echo "Testing CMake configuration..."
    if cmake .. >/dev/null 2>&1; then
        echo -e "${GREEN}✅ CMake configuration successful${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ CMake configuration failed${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test build
    echo "Testing build process..."
    if make >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Build successful${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ Build failed${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    cd ..
}

# Function to test scripts
test_scripts() {
    echo -e "\n${YELLOW}🚀 Testing Scripts${NC}"
    
    # Test build script
    if [ -x "./b" ]; then
        echo -e "${GREEN}✅ Build script (./b) is executable${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ Build script (./b) not executable${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test run script
    if [ -x "./r" ]; then
        echo -e "${GREEN}✅ Run script (./r) is executable${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ Run script (./r) not executable${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

# Function to show test summary
show_summary() {
    echo -e "\n${BLUE}📊 Test Summary${NC}"
    echo "================"
    echo -e "Total Tests: $TOTAL_TESTS"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed! Variable system is ready!${NC}"
        exit 0
    else
        echo -e "\n${RED}💥 Some tests failed. Check the output above.${NC}"
        exit 1
    fi
}

# Main test execution
main() {
    echo -e "${BLUE}Starting comprehensive tests...${NC}\n"
    
    # File existence checks
    check_files
    
    # Script permissions
    test_scripts
    
    # Build system
    test_build_system
    
    # Core functionality
    run_test "Variable System Import" "PYTHONPATH=. python3 -c 'from AI.Utils.variables import VariableManager; print(\"Import successful\")'"
    
    run_test "Variable Unit Tests (80 tests)" "PYTHONPATH=. python3 Tests/Unit/test_variables.py >/dev/null 2>&1"
    
    # Integration tests
    run_test "Integration Tests" "PYTHONPATH=. python3 Tests/Integration/test_variable_integration.py >/dev/null 2>&1"
    
    # C++ tests if build exists
    if [ -f "build/Tests/Cpp/TestVariableApi" ]; then
        run_test "C++ API Tests" "cd build/Tests/Cpp && PYTHONPATH=../../.. ./TestVariableApi >/dev/null 2>&1"
    else
        echo -e "${YELLOW}⚠️  C++ tests skipped (executable not found)${NC}"
    fi
    
    # Interactive mode test
    cd "$SCRIPT_DIR"  # Go back to project root
    run_test "Interactive Mode Import" "PYTHONPATH=\"\$(pwd)\" python3 -c 'from AI.Modes.interactive import InteractiveMode; print(\"Interactive mode import successful\")'"
    
    # Manual functionality test
    if test_variable_functionality >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: Variable Functionality Test${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED: Variable Functionality Test${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Compiler detection
    run_test "Clang Detection" "which clang >/dev/null 2>&1 && which clang++ >/dev/null 2>&1"
    
    # Show final results
    show_summary
}

# Help function
show_help() {
    echo "PyClaudeCli Variable System Test Suite"
    echo ""
    echo "Usage: ./t [option]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --unit         Run only unit tests"
    echo "  --integration  Run only integration tests"
    echo "  --cpp          Run only C++ tests"
    echo "  --build        Test only build system"
    echo "  --quick        Run quick functionality test"
    echo ""
    echo "Default: Run all tests"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --unit)
        run_test "Unit Tests" "python3 Tests/Unit/test_variables.py"
        show_summary
        ;;
    --integration)
        run_test "Integration Tests" "python3 Tests/Integration/test_variable_integration.py"
        show_summary
        ;;
    --cpp)
        if [ -f "build/Tests/Cpp/TestVariableApi" ]; then
            run_test "C++ API Tests" "cd build/Tests/Cpp && ./TestVariableApi"
        else
            echo "C++ tests not built. Run ./b first."
            exit 1
        fi
        show_summary
        ;;
    --build)
        test_build_system
        show_summary
        ;;
    --quick)
        test_variable_functionality
        ;;
    "")
        main
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use ./t --help for available options"
        show_help
        exit 1
        ;;
esac
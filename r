#!/usr/bin/env bash
# Run script for PyClaudeCli - builds if needed then runs console

# Source common utilities
source "$(dirname "$0")/scripts/common.sh"

check_project_root

print_header "PyClaudeCli Run System" "Smart build and console launcher"

# Check if we need to build
declare NEED_BUILD=false

# Check if build directory exists
if [[ ! -d "build" ]]; then
    log_info "Build directory not found, building..."
    NEED_BUILD=true
fi

# Check if any source files are newer than build artifacts
if [[ -d "build" ]]; then
    if is_newer "ai/utils/variables.py" "build/Makefile" || \
       is_newer "ai/bindings/variable_api.cpp" "build/Makefile" || \
       is_newer "CMakeLists.txt" "build/Makefile"; then
        log_info "Source files updated, rebuilding..."
        NEED_BUILD=true
    fi
fi

# Build if needed
if [[ "$NEED_BUILD" == "true" ]]; then
    log_build "Running build script..."
    ./b
fi

# Check available consoles and start the best one
if command_exists v8console; then
    log_run "Starting v8console..."
    v8console
elif command_exists node; then
    log_run "Starting Node.js REPL (v8console not found)..."
    node
elif command_exists python3; then
    log_run "Starting Python interactive mode (v8console not found)..."
    python3 -c "
import sys
sys.path.append('.')
from ai.utils.variables import VariableManager
print('PyClaudeCli Variable System Loaded')
print('Usage: vm = VariableManager(); vm.process_input(\"name=value\")')
exec('import code; code.interact(local=globals())')
"
else
    log_error "No suitable console found (v8console, node, or python3)"
    exit 1
fi
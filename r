#!/usr/bin/env bash
# Run script for PyClaudeCli - builds if needed then runs console

# Source common utilities
source "$(dirname "$0")/Scripts/common.sh"

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
    if is_newer "AI/utils/variables.py" "build/Makefile" || \
       is_newer "AI/bindings/VariableApi.cpp" "build/Makefile" || \
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
if command_exists python3; then
    log_run "Starting Python interactive mode..."
    python3 -c "
import sys
sys.path.append('.')
from AI.Utils.variables import VariableManager
from AI.Modes.interactive import InteractiveMode
from AI.Api.client import ClaudeClient

print('\n🚀 PyClaudeCli Variable System Loaded')
print('\nAvailable imports:')
print('  - VariableManager: Variable management system')
print('  - InteractiveMode: Interactive CLI mode')
print('  - ClaudeClient: Claude API client')
print('\nExample usage:')
print('  vm = VariableManager()')
print('  vm.process_input(\"name=John\")')
print('  vm.process_input(\"Hello name!\")')
print('\nType exit() or Ctrl+D to quit\n')

# Create global instances for convenience
vm = VariableManager()
globals()['vm'] = vm
globals()['VariableManager'] = VariableManager
globals()['InteractiveMode'] = InteractiveMode
globals()['ClaudeClient'] = ClaudeClient

import code
code.interact(local=globals(), banner='')
"
elif command_exists v8console; then
    log_run "Starting v8console..."
    v8console
elif command_exists node; then
    log_run "Starting Node.js REPL..."
    node
else
    log_error "No suitable console found (python3, v8console, or node)"
    exit 1
fi
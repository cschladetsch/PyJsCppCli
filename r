#!/bin/bash
# Run script for PyClaudeCli - builds if needed then runs console

set -e  # Exit on any error

# Check if we need to build
NEED_BUILD=false

# Check if build directory exists
if [ ! -d "build" ]; then
    echo "📦 Build directory not found, building..."
    NEED_BUILD=true
fi

# Check if any source files are newer than build artifacts
if [ -d "build" ]; then
    if [ "ai/utils/variables.py" -nt "build/Makefile" ] || \
       [ "ai/bindings/variable_api.cpp" -nt "build/Makefile" ] || \
       [ "CMakeLists.txt" -nt "build/Makefile" ]; then
        echo "📦 Source files updated, rebuilding..."
        NEED_BUILD=true
    fi
fi

# Build if needed
if [ "$NEED_BUILD" = true ]; then
    echo "🔨 Running build script..."
    ./b
fi

# Check if v8console exists
if command -v v8console >/dev/null 2>&1; then
    echo "🚀 Starting v8console..."
    v8console
elif command -v node >/dev/null 2>&1; then
    echo "🚀 Starting Node.js REPL (v8console not found)..."
    node
elif command -v python3 >/dev/null 2>&1; then
    echo "🚀 Starting Python interactive mode (v8console not found)..."
    python3 -c "
import sys
sys.path.append('.')
from ai.utils.variables import VariableManager
print('PyClaudeCli Variable System Loaded')
print('Usage: vm = VariableManager(); vm.process_input(\"name=value\")')
exec('import code; code.interact(local=globals())')
"
else
    echo "❌ No suitable console found (v8console, node, or python3)"
    exit 1
fi
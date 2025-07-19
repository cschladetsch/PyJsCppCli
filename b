#!/bin/bash
# Build script for PyClaudeCli

set -e  # Exit on any error

echo "🔨 Building PyClaudeCli..."

# Create build directory if it doesn't exist
mkdir -p build
cd build

# Configure with CMake
echo "⚙️  Configuring with CMake..."
cmake ..

# Build all targets
echo "🔧 Building all targets..."
make -j$(nproc)

# Run Python tests
echo "🧪 Running Python tests..."
cd ..
python3 tests/unit/test_variables.py
python3 tests/integration/test_variable_integration.py

# Build C++ tests if they exist
if [ -f "build/tests/cpp/test_variable_api" ]; then
    echo "🧪 Running C++ tests..."
    cd build/tests/cpp
    ./test_variable_api
    cd ../../..
fi

echo "✅ Build completed successfully!"
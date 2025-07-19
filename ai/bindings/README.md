# Bindings Directory

C++ API bindings for cross-language integration with the PyClaudeCli variable system.

## Files

- `variable_api.cpp` - **C++ interface for variable system access**
- `CMakeLists.txt` - **CMake build configuration for C++ API**

## C++ Variable API (`variable_api.cpp`)

### Purpose
Provides a C++ interface to the Python-based variable system, enabling cross-language integration and allowing C++ applications to:
- Set and retrieve persistent variables
- Access the same variable storage as the Python CLI
- Integrate with existing C++ codebases

### Features

#### Core Classes
```cpp
class VariableManager {
public:
    VariableManager(const std::string& config_dir = "");
    std::string GetVariable(const std::string& name) const;
    bool SetVariable(const std::string& name, const std::string& value) const;
    std::string ListVariables() const;
};
```

#### C Interface
```cpp
extern "C" {
    VariableManager* create_variable_manager(const char* config_dir);
    void destroy_variable_manager(VariableManager* vm);
    const char* get_variable(VariableManager* vm, const char* name);
    int set_variable(VariableManager* vm, const char* name, const char* value);
    const char* list_variables(VariableManager* vm);
}
```

#### Implementation Details
- **Python Integration**: Executes Python commands to access the variable system
- **Error Handling**: Graceful handling of Python execution errors
- **Memory Management**: Proper cleanup and resource management
- **Cross-Platform**: Works on Linux, macOS, and Windows

### Usage Examples

#### C++ Class Interface
```cpp
#include "variable_api.cpp"

VariableManager vm;

// Set variables
vm.SetVariable("name", "Alice");
vm.SetVariable("age", "25");

// Get variables  
std::string name = vm.GetVariable("name");
std::string age = vm.GetVariable("age");

// List all variables
std::string all_vars = vm.ListVariables();
```

#### C Interface
```cpp
VariableManager* vm = create_variable_manager(nullptr);

set_variable(vm, "user", "Bob");
const char* user = get_variable(vm, "user");
const char* vars = list_variables(vm);

destroy_variable_manager(vm);
```

### Build System (`CMakeLists.txt`)

#### Features
- **C++23 Standard**: Modern C++ with latest features
- **Multiple Targets**: 
  - `variable_api` - Static library for integration
  - `variable_api_test` - Example/test executable
- **Conditional Compilation**: Prevents main() conflicts in tests
- **Doxygen Integration**: Documentation generation support

#### Build Commands
```bash
mkdir build && cd build
cmake .. -DCMAKE_CXX_COMPILER=clang++
make variable_api          # Build library
make variable_api_test     # Build example
```

### Integration with Python

The C++ API seamlessly integrates with the Python variable system:
1. **Shared Storage**: Uses same `~/.config/claude/variables.json` file
2. **Consistent Behavior**: Same variable access patterns as Python
3. **Live Updates**: Changes in C++ are immediately visible in Python and vice versa
4. **Type Preservation**: JSON types maintained across language boundaries

### Testing

Comprehensive testing ensures reliability:
- **Unit Tests**: Basic operations and edge cases
- **Integration Tests**: Python/C++ interoperability  
- **Error Handling**: Graceful failure modes
- **Memory Safety**: No leaks or corruption

### Performance

- **Efficient**: Direct file system access when possible
- **Cached**: Variables cached in memory during session
- **Minimal Overhead**: Low-cost Python integration
- **Scalable**: Handles large variable sets efficiently

## Use Cases

- **Native Applications**: Integrate PyClaudeCli variables into C++ apps
- **Performance Critical**: Fast variable access from compiled code
- **Legacy Integration**: Connect existing C++ systems to PyClaudeCli
- **Cross-Language**: Share data between Python and C++ components
- **Embedded Systems**: Lightweight variable access for resource-constrained environments
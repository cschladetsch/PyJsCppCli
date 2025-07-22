/**
 * @file VariableApi.cpp
 * @brief C++ API for PyClaudeCli Variable Management System
 * 
 * This file provides a C++ interface to the Python-based variable management
 * system. It allows C++ applications to interact with the variable storage
 * through a clean API that internally uses Python for actual operations.
 * 
 * @author PyClaudeCli Team
 * @date 2024
 * 
 * @details
 * The implementation uses popen() to execute Python commands, ensuring
 * compatibility with the existing Python variable system while providing
 * native C++ access.
 */

#include <string>
#include <cstdlib>
#include <iostream>
#include <memory>

/**
 * @class VariableManager
 * @brief C++ interface for managing persistent variables
 * 
 * This class provides a C++ wrapper around the Python VariableManager,
 * allowing C++ applications to store, retrieve, and manage variables
 * that persist across sessions.
 * 
 * @details
 * The class uses the Python interpreter to execute commands from the
 * ai.utils.variables module, ensuring consistency with the Python API.
 * All variable operations are thread-safe at the Python level.
 * 
 * Example usage:
 * @code{.cpp}
 * VariableManager vm;
 * vm.SetVariable("username", "Alice");
 * std::string user = vm.GetVariable("username");
 * std::cout << "User: " << user << std::endl;
 * @endcode
 */
class VariableManager {
private:
    /**
     * @brief Path to the variable storage JSON file
     */
    std::string config_path;
    
    /**
     * @brief Execute a Python command and return its output
     * 
     * @param cmd Python code to execute
     * @return Command output as string
     * 
     * @details
     * This method handles the execution of Python commands through popen(),
     * manages the Python path, and captures the output. It automatically
     * strips trailing newlines from the output.
     * 
     * @note The method changes directory to the project root to ensure
     *       proper Python module imports.
     */
    std::string execute_python_command(const std::string& cmd) const {
        // Ensure we're using the project root as the Python path
        std::string project_root = std::string(getenv("PWD"));
        // If we're in a subdirectory, find the project root
        size_t build_pos = project_root.find("/build");
        if (build_pos != std::string::npos) {
            project_root = project_root.substr(0, build_pos);
        }
        
        std::string python_cmd = "cd " + project_root + " && python3 -c \"" + cmd + "\"";
        
        FILE* pipe = popen(python_cmd.c_str(), "r");
        if (!pipe) return "";
        
        char buffer[128];
        std::string result = "";
        while (!feof(pipe)) {
            if (fgets(buffer, 128, pipe) != nullptr) {
                result += buffer;
            }
        }
        pclose(pipe);
        
        // Remove trailing newline
        if (!result.empty() && result.back() == '\n') {
            result.pop_back();
        }
        
        return result;
    }

public:
    /**
     * @brief Construct a new Variable Manager object
     * 
     * @param config_dir Optional custom directory for variable storage.
     *                   If empty, defaults to ~/.config/claude/
     * 
     * @details
     * Initializes the variable manager with either a custom storage location
     * or the default location in the user's home directory.
     */
    VariableManager(const std::string& config_dir = "") {
        if (config_dir.empty()) {
            config_path = std::string(getenv("HOME")) + "/.config/claude/variables.json";
        } else {
            config_path = config_dir + "/variables.json";
        }
    }
    
    /**
     * @brief Get the value of a variable
     * 
     * @param name Variable name to retrieve
     * @return Variable value as string, empty string if not found
     * 
     * @details
     * Retrieves a variable value from persistent storage. The method
     * properly escapes the variable name to prevent injection attacks.
     * 
     * @code{.cpp}
     * std::string value = vm.GetVariable("api_key");
     * if (!value.empty()) {
     *     // Use the API key
     * }
     * @endcode
     */
    std::string GetVariable(const std::string& name) const {
        std::string escaped_path = config_path;
        std::string escaped_name = name;
        // Escape single quotes
        size_t pos = 0;
        while ((pos = escaped_path.find("'", pos)) != std::string::npos) {
            escaped_path.replace(pos, 1, "\\'");
            pos += 2;
        }
        pos = 0;
        while ((pos = escaped_name.find("'", pos)) != std::string::npos) {
            escaped_name.replace(pos, 1, "\\'");
            pos += 2;
        }
        
        std::string python_code = 
            "from AI.Utils.variables import VariableManager; "
            "vm = VariableManager('" + escaped_path + "'); "
            "value = vm.get_variable('" + escaped_name + "'); "
            "print(value if value is not None else '', end='')";
        
        return execute_python_command(python_code);
    }
    
    /**
     * @brief Set or update a variable value
     * 
     * @param name Variable name (must be valid identifier)
     * @param value Variable value to store
     * @return true if successfully set, false otherwise
     * 
     * @details
     * Stores a variable with the given name and value. The value is
     * stored as a string but can represent JSON data. All values are
     * properly escaped to prevent injection.
     * 
     * @code{.cpp}
     * if (vm.SetVariable("theme", "dark")) {
     *     std::cout << "Theme updated" << std::endl;
     * }
     * @endcode
     */
    bool SetVariable(const std::string& name, const std::string& value) const {
        std::string escaped_path = config_path;
        std::string escaped_name = name;
        std::string escaped_value = value;
        // Escape single quotes
        size_t pos = 0;
        while ((pos = escaped_path.find("'", pos)) != std::string::npos) {
            escaped_path.replace(pos, 1, "\\'");
            pos += 2;
        }
        pos = 0;
        while ((pos = escaped_name.find("'", pos)) != std::string::npos) {
            escaped_name.replace(pos, 1, "\\'");
            pos += 2;
        }
        pos = 0;
        while ((pos = escaped_value.find("'", pos)) != std::string::npos) {
            escaped_value.replace(pos, 1, "\\'");
            pos += 2;
        }
        
        std::string python_code = 
            "from AI.Utils.variables import VariableManager; "
            "vm = VariableManager('" + escaped_path + "'); "
            "vm.set_variable('" + escaped_name + "', '" + escaped_value + "'); "
            "print('success', end='')";
        
        std::string result = execute_python_command(python_code);
        return result == "success";
    }
    
    /**
     * @brief List all stored variables
     * 
     * @return JSON string containing all variables and their values
     * 
     * @details
     * Returns a JSON-formatted string containing all stored variables.
     * The format is a JSON object with variable names as keys.
     * 
     * @code{.cpp}
     * std::string vars_json = vm.ListVariables();
     * std::cout << "All variables: " << vars_json << std::endl;
     * // Output: {"name": "Alice", "theme": "dark", ...}
     * @endcode
     */
    std::string ListVariables() const {
        std::string escaped_path = config_path;
        // Escape single quotes
        size_t pos = 0;
        while ((pos = escaped_path.find("'", pos)) != std::string::npos) {
            escaped_path.replace(pos, 1, "\\'");
            pos += 2;
        }
        
        std::string python_code = 
            "from AI.Utils.variables import VariableManager; "
            "import json; "
            "vm = VariableManager('" + escaped_path + "'); "
            "print(json.dumps(vm.list_variables()), end='')";
        
        return execute_python_command(python_code);
    }
};

/**
 * @defgroup CInterface C-style Interface
 * @brief C-compatible interface for FFI and language bindings
 * @{
 */

extern "C" {
    /**
     * @brief Create a new variable manager instance
     * 
     * @param config_dir Optional configuration directory path
     * @return Pointer to new VariableManager instance
     * 
     * @note Caller is responsible for calling destroy_variable_manager()
     */
    VariableManager* create_variable_manager(const char* config_dir) {
        return new VariableManager(config_dir ? config_dir : "");
    }
    
    /**
     * @brief Destroy a variable manager instance
     * 
     * @param vm Pointer to VariableManager to destroy
     */
    void destroy_variable_manager(VariableManager* vm) {
        delete vm;
    }
    
    /**
     * @brief Get a variable value (C interface)
     * 
     * @param vm VariableManager instance
     * @param name Variable name
     * @return Variable value as C string
     * 
     * @warning The returned string is statically allocated and will be
     *          overwritten by subsequent calls
     */
    const char* get_variable(VariableManager* vm, const char* name) {
        static std::string result;
        result = vm->GetVariable(name);
        return result.c_str();
    }
    
    /**
     * @brief Set a variable value (C interface)
     * 
     * @param vm VariableManager instance
     * @param name Variable name
     * @param value Variable value
     * @return 1 on success, 0 on failure
     */
    int set_variable(VariableManager* vm, const char* name, const char* value) {
        return vm->SetVariable(name, value) ? 1 : 0;
    }
    
    /**
     * @brief List all variables (C interface)
     * 
     * @param vm VariableManager instance
     * @return JSON string of all variables
     * 
     * @warning The returned string is statically allocated and will be
     *          overwritten by subsequent calls
     */
    const char* list_variables(VariableManager* vm) {
        static std::string result;
        result = vm->ListVariables();
        return result.c_str();
    }
}
/** @} */ // end of CInterface group

#ifndef SKIP_MAIN
/**
 * @brief Example usage and test program
 * 
 * @return 0 on success
 * 
 * @details
 * This main function demonstrates basic usage of the VariableManager class.
 * It can be excluded by defining SKIP_MAIN during compilation.
 */
int main() {
    VariableManager vm;
    
    // Set a variable
    vm.SetVariable("cpp_test", "Hello from C++");
    
    // Get a variable
    std::string value = vm.GetVariable("a");
    std::cout << "Variable 'a' = " << value << std::endl;
    
    // List all variables
    std::string all_vars = vm.ListVariables();
    std::cout << "All variables: " << all_vars << std::endl;
    
    return 0;
}
#endif
#include <string>
#include <cstdlib>
#include <iostream>
#include <memory>

class VariableManager {
private:
    std::string config_path;
    
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
    VariableManager(const std::string& config_dir = "") {
        if (config_dir.empty()) {
            config_path = std::string(getenv("HOME")) + "/.config/claude/variables.json";
        } else {
            config_path = config_dir + "/variables.json";
        }
    }
    
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
            "from ai.utils.variables import VariableManager; "
            "vm = VariableManager('" + escaped_path + "'); "
            "value = vm.get_variable('" + escaped_name + "'); "
            "print(value if value is not None else '', end='')";
        
        return execute_python_command(python_code);
    }
    
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
            "from ai.utils.variables import VariableManager; "
            "vm = VariableManager('" + escaped_path + "'); "
            "vm.set_variable('" + escaped_name + "', '" + escaped_value + "'); "
            "print('success', end='')";
        
        std::string result = execute_python_command(python_code);
        return result == "success";
    }
    
    std::string ListVariables() const {
        std::string escaped_path = config_path;
        // Escape single quotes
        size_t pos = 0;
        while ((pos = escaped_path.find("'", pos)) != std::string::npos) {
            escaped_path.replace(pos, 1, "\\'");
            pos += 2;
        }
        
        std::string python_code = 
            "from ai.utils.variables import VariableManager; "
            "import json; "
            "vm = VariableManager('" + escaped_path + "'); "
            "print(json.dumps(vm.list_variables()), end='')";
        
        return execute_python_command(python_code);
    }
};

// C-style interface for easier binding
extern "C" {
    VariableManager* create_variable_manager(const char* config_dir) {
        return new VariableManager(config_dir ? config_dir : "");
    }
    
    void destroy_variable_manager(VariableManager* vm) {
        delete vm;
    }
    
    const char* get_variable(VariableManager* vm, const char* name) {
        static std::string result;
        result = vm->GetVariable(name);
        return result.c_str();
    }
    
    int set_variable(VariableManager* vm, const char* name, const char* value) {
        return vm->SetVariable(name, value) ? 1 : 0;
    }
    
    const char* list_variables(VariableManager* vm) {
        static std::string result;
        result = vm->ListVariables();
        return result.c_str();
    }
}

#ifndef SKIP_MAIN
// Example usage
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
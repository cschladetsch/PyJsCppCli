# Scripts Directory

Shared utilities and common functions for AI CLI shell scripts.

## Files

- `common.sh` - **Shared utilities and functions for all shell scripts**

## Common Utilities (`common.sh`)

### Purpose
Provides a unified foundation for all shell scripts in the project, eliminating code duplication and ensuring consistent behavior across:
- `./b` - Build script
- `./r` - Run script  
- `./t` - Test script
- `./install_alias.sh` - Alias installer

### Features

#### Strict Mode
- `set -euo pipefail` for robust error handling
- Prevents common bash scripting errors
- Ensures scripts fail fast on errors

#### Color System
```bash
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'
```

#### Icon System
```bash
readonly ICON_SUCCESS="✅"
readonly ICON_ERROR="❌"
readonly ICON_WARNING="⚠️"
readonly ICON_INFO="ℹ️"
readonly ICON_BUILD="🔨"
readonly ICON_TEST="🧪"
readonly ICON_RUN="🚀"
readonly ICON_CONFIG="🔧"
```

#### Logging Functions
- `log_info()` - Information messages
- `log_success()` - Success messages  
- `log_error()` - Error messages
- `log_warning()` - Warning messages
- `log_build()` - Build-related messages
- `log_test()` - Test-related messages
- `log_run()` - Run-related messages
- `log_config()` - Configuration messages

#### Utility Functions
- `print_header()` - Consistent script headers
- `show_progress()` - Progress indicators
- `command_exists()` - Check if command is available
- `is_newer()` - File timestamp comparison
- `run_safe()` - Execute commands with error handling
- `check_project_root()` - Validate we're in project directory
- `get_project_root()` - Get absolute project path

### Usage

All shell scripts source this file:
```bash
#!/usr/bin/env bash
# Source common utilities
source "$(dirname "$0")/scripts/common.sh"

check_project_root
print_header "Script Title" "Description"

log_info "Starting operation..."
run_safe "Building project" make
log_success "Operation completed!"
```

### Benefits

- **DRY Principle**: No duplicate code across scripts
- **Consistency**: Unified visual style and behavior
- **Maintainability**: Update colors/functions in one place
- **Reliability**: Consistent error handling and validation
- **User Experience**: Clear, professional script output

## Integration

This common utilities system is automatically loaded by all project shell scripts, providing a solid foundation for reliable, maintainable script development.
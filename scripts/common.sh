#!/usr/bin/env bash
# Common utilities and functions for PyClaudeCli shell scripts

# Strict mode
set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Icons/Emojis for consistent output
readonly ICON_SUCCESS="✅"
readonly ICON_ERROR="❌"
readonly ICON_WARNING="⚠️"
readonly ICON_INFO="ℹ️"
readonly ICON_BUILD="🔨"
readonly ICON_TEST="🧪"
readonly ICON_RUN="🚀"
readonly ICON_CONFIG="🔧"

# Get the absolute path to the PyClaudeCli directory
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Logging functions
log_info() {
    echo -e "${BLUE}${ICON_INFO} $*${NC}"
}

log_success() {
    echo -e "${GREEN}${ICON_SUCCESS} $*${NC}"
}

log_error() {
    echo -e "${RED}${ICON_ERROR} $*${NC}" >&2
}

log_warning() {
    echo -e "${YELLOW}${ICON_WARNING} $*${NC}"
}

log_build() {
    echo -e "${BLUE}${ICON_BUILD} $*${NC}"
}

log_test() {
    echo -e "${CYAN}${ICON_TEST} $*${NC}"
}

log_run() {
    echo -e "${GREEN}${ICON_RUN} $*${NC}"
}

log_config() {
    echo -e "${MAGENTA}${ICON_CONFIG} $*${NC}"
}

# Header function for consistent script headers
print_header() {
    local title="$1"
    local description="${2:-}"
    
    echo -e "${BLUE}${title}${NC}"
    echo "$(printf '=%.0s' $(seq 1 ${#title}))"
    if [[ -n "$description" ]]; then
        echo "$description"
        echo ""
    fi
}

# Progress indicator
show_progress() {
    local message="$1"
    echo -e "${YELLOW}📋 $message${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if file is newer than another file
is_newer() {
    local file1="$1"
    local file2="$2"
    
    [[ "$file1" -nt "$file2" ]]
}

# Run command with error handling
run_safe() {
    local description="$1"
    shift
    
    show_progress "$description"
    if "$@"; then
        log_success "$description completed"
        return 0
    else
        log_error "$description failed"
        return 1
    fi
}

# Check if we're in the project root
check_project_root() {
    if [[ ! -f "ai/utils/variables.py" ]] || [[ ! -f "CMakeLists.txt" ]]; then
        log_error "Must be run from PyClaudeCli project root directory"
        exit 1
    fi
}

# Get project root directory
get_project_root() {
    echo "$SCRIPT_DIR"
}

# Export functions for use in other scripts
export -f log_info log_success log_error log_warning log_build log_test log_run log_config
export -f print_header show_progress command_exists is_newer run_safe check_project_root get_project_root
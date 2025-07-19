#!/usr/bin/env bash
# Install v8c alias for PyClaudeCli in bash and/or zsh

# Source common utilities
source "$(dirname "$0")/scripts/common.sh"

check_project_root

readonly ALIAS_COMMAND="alias v8c='$(get_project_root)/r'"

print_header "PyClaudeCli Alias Installer" "Adds 'v8c' alias to your shell configuration"
log_info "Alias command: ${ALIAS_COMMAND}"
echo ""

# Function to add alias to a shell config file
add_alias_to_file() {
    local shell_name="$1"
    local config_file="$2"
    
    log_config "Adding alias to $shell_name ($config_file)"
    
    if [[ ! -f "$config_file" ]]; then
        log_warning "Creating $config_file (didn't exist)"
        touch "$config_file"
    fi
    
    # Check if alias already exists
    if grep -q "alias v8c=" "$config_file"; then
        log_warning "v8c alias already exists in $config_file"
        log_info "Updating existing alias..."
        
        # Remove existing alias and add new one
        grep -v "alias v8c=" "$config_file" > "${config_file}.tmp" || true
        echo "$ALIAS_COMMAND" >> "${config_file}.tmp"
        mv "${config_file}.tmp" "$config_file"
    else
        # Add new alias
        echo "" >> "$config_file"
        echo "# PyClaudeCli v8c alias" >> "$config_file"
        echo "$ALIAS_COMMAND" >> "$config_file"
    fi
    
    log_success "Added v8c alias to $config_file"
}

# Function to detect and install for a specific shell
install_for_shell() {
    local shell_name="$1"
    local config_file="$2"
    
    if [ -f "$config_file" ] || [ "$shell_name" = "bash" ] || [ "$shell_name" = "zsh" ]; then
        echo -e "${BLUE}🔍 Found $shell_name configuration${NC}"
        add_alias_to_file "$shell_name" "$config_file"
        return 0
    else
        return 1
    fi
}

# Auto-detect shells and install
declare -i installed_count=0

# Try bash
if command -v bash >/dev/null 2>&1; then
    bash_config="$HOME/.bashrc"
    if [ "$(uname)" = "Darwin" ]; then
        # macOS uses .bash_profile by default
        bash_config="$HOME/.bash_profile"
    fi
    
    if install_for_shell "bash" "$bash_config"; then
        ((installed_count++))
    fi
fi

# Try zsh
if command -v zsh >/dev/null 2>&1; then
    if install_for_shell "zsh" "$HOME/.zshrc"; then
        ((installed_count++))
    fi
fi

echo ""
echo -e "${GREEN}📊 Installation Summary${NC}"
echo "======================="

if [ $installed_count -eq 0 ]; then
    echo -e "${RED}❌ No shell configurations found or updated${NC}"
    echo "Manual installation required:"
    echo "  Add this line to your shell config file:"
    echo "  ${ALIAS_COMMAND}"
    exit 1
else
    echo -e "${GREEN}✅ Successfully installed v8c alias to $installed_count shell(s)${NC}"
    echo ""
    echo -e "${YELLOW}🔄 To use the alias immediately:${NC}"
    
    if [ -f "$HOME/.bashrc" ] && [ $installed_count -gt 0 ]; then
        echo "  source ~/.bashrc"
    fi
    if [ -f "$HOME/.bash_profile" ] && [ $installed_count -gt 0 ]; then
        echo "  source ~/.bash_profile"
    fi
    if [ -f "$HOME/.zshrc" ] && [ $installed_count -gt 0 ]; then
        echo "  source ~/.zshrc"
    fi
    
    echo "  OR restart your terminal"
    echo ""
    echo -e "${GREEN}🚀 Then you can use: ${NC}${BLUE}v8c${NC}"
    echo ""
    echo -e "${YELLOW}💡 What v8c does:${NC}"
    echo "  - Builds PyClaudeCli if needed"
    echo "  - Starts the best available console (v8console → node → python)"
    echo "  - Loads the variable system for persistent storage"
fi

# Test the alias immediately if possible
echo ""
echo -e "${BLUE}🧪 Testing alias...${NC}"
if [ -x "$SCRIPT_DIR/r" ]; then
    echo -e "${GREEN}✅ v8c command will work (./r script is executable)${NC}"
else
    echo -e "${RED}❌ Warning: ./r script not found or not executable${NC}"
    echo "  Run: chmod +x $SCRIPT_DIR/r"
fi
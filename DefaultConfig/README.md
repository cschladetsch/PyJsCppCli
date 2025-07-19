# DefaultConfig Directory

Default configuration files for AI CLI with variable system support.

## Files

- `aliases.json` - Command aliases configuration
- `models.json` - Available AI models configuration
- `system` - System prompt configuration
- `templates.json` - Response templates configuration

## Description

This directory contains the default configuration files that define the behavior and capabilities of the AI CLI. These files can be customized to modify aliases, available models, system prompts, and response templates.

## Configuration Locations

When the AI CLI runs, it creates user-specific configuration in:
- `~/.config/ai-cli/` - User configuration directory
- `~/.config/ai-cli/variables.json` - **Persistent variable storage**
- `~/.config/ai-cli/conversations.json` - Conversation history
- `~/.config/ai-cli/system` - Custom system prompt
- `~/.config/ai-cli/aliases.json` - Custom aliases
- `~/.config/ai-cli/models.json` - Model preferences
- `~/.config/ai-cli/templates.json` - Response templates

## Variable System

The variable system automatically creates and manages:
- **Storage**: `~/.config/ai-cli/variables.json`
- **Format**: JSON with variable name/value pairs
- **Access**: Available in interactive mode via `vars` command
- **Persistence**: Variables survive CLI restarts and system reboots

### Example Variable File
```json
{
  "name": "Alice",
  "age": 25,
  "hobbies": ["reading", "coding", "hiking"],
  "config": {
    "theme": "dark",
    "notifications": true
  }
}
```
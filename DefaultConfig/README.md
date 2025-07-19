# DefaultConfig Directory

Default configuration files for PyClaudeCli with variable system support.

## Files

- `aliases.json` - Command aliases configuration
- `models.json` - Available AI models configuration
- `system` - System prompt configuration
- `templates.json` - Response templates configuration

## Description

This directory contains the default configuration files that define the behavior and capabilities of PyClaudeCli. These files can be customized to modify aliases, available models, system prompts, and response templates.

## Configuration Locations

When PyClaudeCli runs, it creates user-specific configuration in:
- `~/.config/claude/` - User configuration directory
- `~/.config/claude/variables.json` - **Persistent variable storage**
- `~/.config/claude/conversations.json` - Conversation history
- `~/.config/claude/system` - Custom system prompt
- `~/.config/claude/aliases.json` - Custom aliases
- `~/.config/claude/models.json` - Model preferences
- `~/.config/claude/templates.json` - Response templates

## Variable System

The variable system automatically creates and manages:
- **Storage**: `~/.config/claude/variables.json`
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
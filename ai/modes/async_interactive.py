"""Async interactive mode with streaming support"""

import asyncio
import sys
from typing import Optional, List
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory

from ..api.async_client import AsyncClaudeClient
from ..utils.output_formatter import OutputFormatter, print_error, print_success, print_info
from ..utils.colors import Colors
from ..utils.theme_config import theme_config
from ..utils.io import (
    load_conversation_state,
    save_conversation_state,
    append_to_conversation_log,
    prepare_files_for_upload,
    resolve_file_paths
)
from ..models import Interaction
from ..constants import HISTORY_FILE, DEFAULT_SYSTEM_PROMPT


class AsyncInteractiveMode:
    """Asynchronous interactive mode with streaming responses"""
    
    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.system_prompt = system_prompt
        self.interactions = load_conversation_state()
        self.session: Optional[PromptSession] = None
        self.client: Optional[AsyncClaudeClient] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        use_asyncio_event_loop()
        self.session = PromptSession(
            history=FileHistory(HISTORY_FILE),
            vi_mode=True
        )
        self.client = await AsyncClaudeClient().__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
            
    def _get_prompt(self) -> ANSI:
        """Get formatted prompt"""
        return ANSI(OutputFormatter.format_prompt('> '))
        
    async def handle_query(self, query: str) -> bool:
        """Handle a user query. Returns False to exit."""
        # Check for exit commands
        if query.lower() in ['exit', 'quit']:
            return False
            
        # Check for special commands
        if query.lower() == 'help' or query == '?':
            self.show_help()
            return True
            
        if query.lower() == 'clear':
            await self.clear_conversation()
            return True
            
        if query.lower().startswith('c'):
            self.show_conversation(query)
            return True
            
        if query.lower().startswith('upload '):
            await self.handle_upload(query)
            return True
            
        # Regular query - stream the response
        try:
            print()  # New line before response
            full_response = ""
            
            # Stream response
            async for chunk in self.client.stream_response(
                query,
                system_prompt=self.system_prompt,
                interactions=self.interactions
            ):
                print(chunk, end='', flush=True)
                full_response += chunk
                
            print("\n")  # New lines after response
            
            # Save interaction
            interaction = Interaction(
                query=query,
                response=full_response,
                timestamp=datetime.now().isoformat()
            )
            self.interactions.append(interaction)
            
            # Save state
            save_conversation_state(self.interactions)
            append_to_conversation_log(interaction)
            
            # Generate MIDI from query and response
            try:
                from ..utils.midi_music import MidiMusicGenerator
                MidiMusicGenerator.generate_and_save(query, full_response)
            except Exception as e:
                # Don't fail the interaction if MIDI generation fails
                pass
            
        except Exception as e:
            print_error(f"Error: {str(e)}")
            
        return True
        
    def show_help(self):
        """Display help information"""
        print("\nAvailable commands:")
        print("  help, ?                      - Show this help")
        print("  c [N]                        - Show last N conversation exchanges")
        print("  clear                        - Clear conversation history")
        print("  upload <file1> [file2] ...   - Upload files for analysis")
        print("    Options:")
        print("      --recursive, -r          - Include all files in directories")
        print("  exit, quit                   - Exit the program")
        print()
        
    def show_conversation(self, query: str):
        """Show conversation history"""
        parts = query.split()
        limit = None
        
        if len(parts) > 1 and parts[1].isdigit():
            limit = int(parts[1])
            
        if not self.interactions:
            print("No conversation history.")
            return
            
        interactions = self.interactions[-limit:] if limit else self.interactions
        
        for i, interaction in enumerate(interactions, 1):
            user_color = theme_config.get_color("user")
            assistant_color = theme_config.get_color("assistant")
            user_short = interaction.query[:50] + "..." if len(interaction.query) > 50 else interaction.query
            assistant_short = interaction.response[:50] + "..." if len(interaction.response) > 50 else interaction.response
            
            print(f"{Colors.BRIGHT_CYAN}{i}.{Colors.RESET} {user_color}User:{Colors.RESET} {user_short}")
            print(f"   {assistant_color}Assistant:{Colors.RESET} {assistant_short}")
            print()
                
    async def clear_conversation(self):
        """Clear conversation history"""
        self.interactions = []
        save_conversation_state([])
        print_success("Conversation history cleared.")
        
    async def handle_upload(self, query: str):
        """Handle file upload command"""
        args = query.split()[1:]  # Remove 'upload' command
        
        if not args:
            print("Usage: upload [--recursive|-r] <file1> [file2] ...")
            return
            
        recursive = False
        file_args = args
        
        if args[0] in ['--recursive', '-r']:
            recursive = True
            file_args = args[1:]
            
        if not file_args:
            print("No files specified.")
            return
            
        # Resolve file paths
        file_paths = resolve_file_paths(file_args, recursive=recursive)
        
        if not file_paths:
            return
            
        # Prepare files
        contents, images = prepare_files_for_upload(file_paths)
        
        # Add to context
        if contents or images:
            print_success(f"Uploaded {len(contents)} text files and {len(images)} images")
            # In a real implementation, these would be added to the context
            
    async def run(self):
        """Run the interactive mode"""
        print_info("Ask CLI - Interactive Mode (Streaming)")
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                # Get user input
                query = await self.session.prompt_async(self._get_prompt())
                
                # Handle the query
                should_continue = await self.handle_query(query)
                if not should_continue:
                    break
                    
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")
                
                
async def main():
    """Main entry point for async interactive mode"""
    try:
        async with AsyncInteractiveMode() as mode:
            await mode.run()
    except Exception as e:
        print_error(f"Failed to start interactive mode: {str(e)}")
        sys.exit(1)
        
        
if __name__ == "__main__":
    asyncio.run(main())
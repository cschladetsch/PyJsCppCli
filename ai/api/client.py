"""
Anthropic API client wrapper with improved text file handling
"""

from anthropic import Anthropic
from ..constants import DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_SYSTEM_PROMPT
from ..utils.io import read_token, format_file_for_upload

class ClaudeClient:
    """Wrapper for Anthropic's API client"""
    
    def __init__(self, api_key=None, model=DEFAULT_MODEL):
        """Initialize the Claude client"""
        self.api_key = api_key or read_token()
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        
    def generate_response(self, prompt, system_prompt=DEFAULT_SYSTEM_PROMPT, 
                          message_history=None, files=None, text_files_content=None, 
                          max_tokens=DEFAULT_MAX_TOKENS):
        """
        Generates a response using Claude, maintaining conversation history.
        
        Args:
            prompt (str): The user's input prompt
            system_prompt (str): System prompt for Claude
            message_history (list): Previous message history
            files (list): List of file objects to include
            text_files_content (str): Content of text files to include in the message
            max_tokens (int): Maximum tokens in response
            
        Returns:
            tuple: (response_text, updated_message_history)
        """
        if message_history is None:
            message_history = []
        
        # Combine text files content with the prompt if present
        combined_prompt = prompt
        if text_files_content:
            combined_prompt = f"{prompt}\n\n{text_files_content}"
            
        # Prepare the user message with files if provided
        user_message = {"role": "user", "content": []}
        
        # Add text content
        user_message["content"].append({"type": "text", "text": combined_prompt})
        
        # Add image files if provided
        if files and len(files) > 0:
            for file_obj in files:
                file_content = format_file_for_upload(file_obj)
                user_message["content"].append(file_content)
        
        # Build the messages array
        messages = message_history.copy()
        
        # Add the new user message
        if files and len(files) > 0:
            # For messages with files, we need to use the structured format
            messages.append(user_message)
        else:
            # For text-only messages, use the simple format
            messages.append({"role": "user", "content": combined_prompt})
        
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=messages,
                max_tokens=max_tokens
            )
            current_response = response.content[0].text
            
            # Add this exchange to history
            if files and len(files) > 0:
                # For messages with files, store a simplified version in history
                file_names = [file_obj["file_name"] for file_obj in files]
                file_list = ", ".join(file_names)
                if text_files_content:
                    history_prompt = f"{prompt}\n[Files: {file_list} and text files]"
                else:
                    history_prompt = f"{prompt}\n[Files: {file_list}]"
                message_history.append({"role": "user", "content": history_prompt})
            else:
                message_history.append({"role": "user", "content": combined_prompt})
                
            message_history.append({"role": "assistant", "content": current_response})
            return current_response, message_history
        except Exception as e:
            return f"Error while generating response: {e}", message_history

"""
Anthropic API client wrapper with improved text file handling
"""

from anthropic import Anthropic

from ..constants import DEFAULT_MAX_TOKENS, DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT
from ..models import Interaction
from ..utils.io import format_file_for_upload, read_token


class ClaudeClient:
    """Wrapper for Anthropic's API client"""

    def __init__(self, api_key=None, model=DEFAULT_MODEL):
        """Initialize the Claude client"""
        self.api_key = api_key or read_token()
        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def generate_response(
        self,
        prompt,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        interactions=None,
        files=None,
        text_files_content=None,
        max_tokens=DEFAULT_MAX_TOKENS,
    ):
        """
        Generates a response using Claude, maintaining conversation history.

        Args:
            prompt (str): The user's input prompt
            system_prompt (str): System prompt for Claude
            interactions (list[Interaction]): Previous interactions
            files (list): List of file objects to include
            text_files_content (str): Content of text files to include in the message
            max_tokens (int): Maximum tokens in response

        Returns:
            tuple: (response_text, updated_interactions)
        """
        if interactions is None:
            interactions = []

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

        # Build the messages array from interactions
        messages = []
        for interaction in interactions:
            messages.append({"role": "user", "content": interaction.query})
            messages.append({"role": "assistant", "content": interaction.response})

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
                max_tokens=max_tokens,
            )
            current_response = response.content[0].text

            # Create the query string for the interaction
            if files and len(files) > 0:
                # For messages with files, store a simplified version in history
                file_names = [file_obj["file_name"] for file_obj in files]
                file_list = ", ".join(file_names)
                if text_files_content:
                    query_for_history = f"{prompt}\n[Files: {file_list} and text files]"
                else:
                    query_for_history = f"{prompt}\n[Files: {file_list}]"
            else:
                query_for_history = combined_prompt

            # Create new interaction and add to history
            new_interaction = Interaction(query_for_history, current_response)
            interactions.append(new_interaction)

            return current_response, interactions
        except Exception as e:
            return f"Error while generating response: {e}", interactions

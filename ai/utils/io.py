"""
File I/O utilities for AI CLI with improved text file handling
"""

import os
import json
import mimetypes
import glob
import base64
from ..constants import (
    TOKEN_FILE, LEGACY_TOKEN_FILE,
    CONVERSATION_STATE_FILE, LEGACY_CONVERSATION_STATE_FILE,
    UPLOAD_CACHE_DIR
)

def read_token():
    """
    Reads the API key from environment variable or token files.
    Checks in order: environment variable, new token file, legacy token file.
    """
    if "CLAUDE_API_KEY" in os.environ:
        return os.environ["CLAUDE_API_KEY"]
    
    # Try new location first
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            return file.read().strip()
    
    # Fall back to legacy location
    if os.path.exists(LEGACY_TOKEN_FILE):
        with open(LEGACY_TOKEN_FILE, "r") as file:
            return file.read().strip()
            
    raise FileNotFoundError("Token file not found and 'CLAUDE_API_KEY' environment variable is not set.")

def load_conversation_state():
    """
    Load conversation history from state file.
    Checks both new and legacy file paths.
    """
    # Check new location first
    if os.path.exists(CONVERSATION_STATE_FILE):
        try:
            with open(CONVERSATION_STATE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse conversation state file. Starting fresh.")
            return []
    
    # Fall back to legacy location
    if os.path.exists(LEGACY_CONVERSATION_STATE_FILE):
        try:
            with open(LEGACY_CONVERSATION_STATE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    return []

def save_conversation_state(message_history):
    """Save conversation history to state file"""
    # Save to new location
    with open(CONVERSATION_STATE_FILE, 'w') as f:
        json.dump(message_history, f, indent=2)

def resolve_file_paths(patterns, allow_directories=False):
    """
    Resolves file path patterns to actual files
    
    Args:
        patterns (list): List of file patterns or paths
        allow_directories (bool): Whether to allow directory patterns
        
    Returns:
        list: List of resolved file paths
    """
    resolved_paths = []
    
    for pattern in patterns:
        # Expand user directory if present
        expanded_pattern = os.path.expanduser(pattern)
        
        # Get matching paths
        matching_paths = glob.glob(expanded_pattern, recursive=True)
        
        if not matching_paths:
            print(f"Warning: No files found matching '{pattern}'")
            continue
            
        for path in matching_paths:
            if os.path.isdir(path):
                if allow_directories:
                    # For directories, get all files within them
                    for root, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.path.isfile(file_path):
                                resolved_paths.append(file_path)
                else:
                    print(f"Warning: '{path}' is a directory, skipping")
            else:
                resolved_paths.append(path)
                
    return resolved_paths

def is_text_file(mime_type, file_path):
    """
    Determine if a file is a text file based on MIME type and content
    
    Args:
        mime_type (str): MIME type of the file
        file_path (str): Path to the file
        
    Returns:
        bool: True if it's a text file, False otherwise
    """
    # Common text MIME types
    text_mime_types = [
        'text/', 'application/json', 'application/xml', 'application/javascript',
        'application/x-javascript', 'application/csv', 'text/csv', 'text/markdown',
        'text/plain', 'text/html', 'text/css', 'application/x-python'
    ]
    
    # Check if any text MIME type prefix matches
    if any(mime_type.startswith(prefix) for prefix in text_mime_types):
        return True
    
    # For uncertain cases, try to open as text
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to read a few lines to see if it's text
            f.read(1024)
        return True
    except UnicodeDecodeError:
        # If we get a decode error, it's probably binary
        return False
    
    return False

def prepare_files_for_upload(file_paths):
    """
    Prepares files for upload to Claude API
    
    Args:
        file_paths (list): List of file paths to prepare
        
    Returns:
        tuple: (prepared_files, text_files_content)
            - prepared_files: List of prepared file objects for API upload
            - text_files_content: String with content of text files to include in the message
    """
    # Ensure upload cache directory exists
    os.makedirs(UPLOAD_CACHE_DIR, exist_ok=True)
    
    prepared_files = []
    text_files_content = ""
    
    for file_path in file_paths:
        try:
            # Get file size and MIME type
            file_size = os.path.getsize(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if mime_type is None:
                # Default to binary if can't determine type
                mime_type = "application/octet-stream"
            
            # Get just the filename without path
            file_name = os.path.basename(file_path)
            
            # Check if this is a text file
            if is_text_file(mime_type, file_path):
                # For text files, read content and add to text_files_content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                text_files_content += f"\n\n# File: {file_name}\n```{file_name.split('.')[-1]}\n{content}\n```\n\n"
                print(f"  Added text file: {file_name} ({file_size/1024:.1f} KB, {mime_type})")
            else:
                # For binary/image files that Claude API can handle
                if mime_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                    # Read file content
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    
                    prepared_files.append({
                        "file_path": file_path,
                        "file_name": file_name,
                        "mime_type": mime_type,
                        "size": file_size,
                        "content": file_content
                    })
                else:
                    print(f"  Warning: File type not supported by Claude API: {file_name} ({mime_type})")
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
            
    return prepared_files, text_files_content

def format_file_for_upload(file_obj):
    """
    Formats a file object for the Claude API
    
    Args:
        file_obj (dict): File object with content and metadata
        
    Returns:
        dict: Formatted file content for Claude API
    """
    return {
        "type": "image",  # Claude API uses 'image' type for all file uploads
        "source": {
            "type": "base64",
            "media_type": file_obj["mime_type"],
            "data": base64.b64encode(file_obj["content"]).decode("utf-8")
        }
    }

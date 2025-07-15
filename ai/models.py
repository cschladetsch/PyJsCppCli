"""
Data models for Ask CLI with full type annotations

This module contains all the data models used throughout the Ask CLI application,
including conversation state, interactions, file uploads, and API responses.
All models are properly typed and include serialization methods.
"""

from typing import Optional, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Interaction:
    """Represents a single interaction between user and assistant.
    
    This class encapsulates a single question-answer exchange, including
    the user's query, the assistant's response, and timing information.
    
    Attributes:
        query: The user's input/question
        response: The assistant's response
        timestamp: When the interaction occurred
    """
    
    query: str
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "query": self.query,
            "response": self.response,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Interaction":
        """Create from dictionary (for JSON deserialization).
        
        Args:
            data: Dictionary containing interaction data
            
        Returns:
            Interaction instance created from dictionary data
        """
        timestamp_str = data.get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()
            
        return cls(
            query=data["query"],
            response=data["response"],
            timestamp=timestamp
        )
    
    def __repr__(self) -> str:
        query_preview = self.query[:30] + "..." if len(self.query) > 30 else self.query
        response_preview = self.response[:30] + "..." if len(self.response) > 30 else self.response
        return f"Interaction(query='{query_preview}', response='{response_preview}')"


@dataclass
class FileUpload:
    """Represents an uploaded file with metadata.
    
    This class stores information about files uploaded by the user,
    including file content, type, and size information.
    
    Attributes:
        path: Original file path
        content: File content as string
        file_type: MIME type or file extension
        size: File size in bytes
    """
    
    path: str
    content: str
    file_type: str
    size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation of the file upload
        """
        return {
            "path": self.path,
            "content": self.content,
            "file_type": self.file_type,
            "size": self.size
        }


@dataclass
class ConversationState:
    """Represents the complete conversation state.
    
    This class manages the entire conversation history, including all
    interactions, system prompts, and timing information.
    
    Attributes:
        interactions: List of all interactions in the conversation
        system_prompt: Optional system prompt for the conversation
        created_at: When the conversation was created
        updated_at: When the conversation was last updated
    """
    
    interactions: list[Interaction] = field(default_factory=list)
    system_prompt: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_interaction(self, interaction: Interaction) -> None:
        """Add a new interaction and update timestamp.
        
        Args:
            interaction: The interaction to add to the conversation
        """
        self.interactions.append(interaction)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "interactions": [i.to_dict() for i in self.interactions],
            "system_prompt": self.system_prompt,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationState":
        """Create from dictionary data.
        
        Args:
            data: Dictionary containing conversation state data
            
        Returns:
            ConversationState instance created from dictionary data
        """
        interactions = [
            Interaction.from_dict(i) for i in data.get("interactions", [])
        ]
        
        return cls(
            interactions=interactions,
            system_prompt=data.get("system_prompt"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )
"""
Data models for Ask CLI with full type annotations
"""

from typing import Optional, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Interaction:
    """Represents a single interaction between user and assistant"""
    
    query: str
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "query": self.query,
            "response": self.response,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Interaction":
        """Create from dictionary (for JSON deserialization)"""
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
    """Represents an uploaded file"""
    
    path: str
    content: str
    file_type: str
    size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "path": self.path,
            "content": self.content,
            "file_type": self.file_type,
            "size": self.size
        }


@dataclass
class ConversationState:
    """Represents the complete conversation state"""
    
    interactions: list[Interaction] = field(default_factory=list)
    system_prompt: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_interaction(self, interaction: Interaction) -> None:
        """Add a new interaction and update timestamp"""
        self.interactions.append(interaction)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "interactions": [i.to_dict() for i in self.interactions],
            "system_prompt": self.system_prompt,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationState":
        """Create from dictionary"""
        interactions = [
            Interaction.from_dict(i) for i in data.get("interactions", [])
        ]
        
        return cls(
            interactions=interactions,
            system_prompt=data.get("system_prompt"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )
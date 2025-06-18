"""
Data models for AI CLI
"""

from typing import Optional
from datetime import datetime


class Interaction:
    """Represents a single interaction between user and assistant"""
    
    def __init__(self, query: str, response: str, timestamp: Optional[datetime] = None):
        self.query = query
        self.response = response
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "query": self.query,
            "response": self.response,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary (for JSON deserialization)"""
        return cls(
            query=data["query"],
            response=data["response"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )
    
    def __repr__(self):
        return f"Interaction(query='{self.query[:30]}...', response='{self.response[:30]}...')"
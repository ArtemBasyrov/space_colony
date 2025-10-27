# [file name]: message.py
# [file content begin]
from enum import Enum
from typing import List, Dict, Any, Callable

class MessageState(Enum):
    SCHEDULED = "scheduled"
    DISPLAYED = "displayed"
    ARCHIVED = "archived"

class Message:
    def __init__(self, 
                 message_id: str,
                 title: str,
                 sender: str,
                 portrait: str,
                 text: str,
                 triggers: List[Callable] = None,
                 day_trigger: int = None):
        self.message_id = message_id
        self.title = title
        self.sender = sender
        self.portrait = portrait
        self.text = text
        self.state = MessageState.SCHEDULED
        self.triggers = triggers or []
        self.day_trigger = day_trigger
        
    def should_display(self, game) -> bool:
        """Check if message should be displayed based on triggers"""
        if self.state != MessageState.SCHEDULED:
            return False
            
        # Check day trigger
        if self.day_trigger and game.day != self.day_trigger:
            return False
            
        # Check additional triggers
        if self.triggers and not all(trigger(game) for trigger in self.triggers):
            return False
            
        return True
    
    def mark_displayed(self):
        """Mark message as displayed"""
        self.state = MessageState.DISPLAYED
    
    def mark_archived(self):
        """Mark message as archived"""
        self.state = MessageState.ARCHIVED
# [file content end]
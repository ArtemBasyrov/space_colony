# [file name]: message_manager.py
# [file content begin]
from typing import Dict, List
from .message import Message, MessageState
from events import EventType, GameEvent

class MessageManager:
    def __init__(self, game):
        self.game = game
        self.messages: Dict[str, Message] = {}
        self.archived_messages: List[Message] = []
        self.pending_messages: List[Message] = []
        
        # Subscribe to game events
        self.game.event_manager.subscribe(EventType.DAY_ADVANCED, self.on_day_advanced)
    
    def add_message(self, message: Message):
        """Add a message to the manager"""
        self.messages[message.message_id] = message
    
    def on_day_advanced(self, event):
        """Check for messages when day advances"""
        self.check_pending_messages()
    
    def check_pending_messages(self):
        """Check for messages that should be displayed"""
        self.pending_messages = []
        
        for message in self.messages.values():
            if message.should_display(self.game):
                self.pending_messages.append(message)
    
    def get_next_pending_message(self) -> Message:
        """Get the next pending message to display"""
        if self.pending_messages:
            return self.pending_messages[0]
        return None
    
    def complete_current_message(self):
        """Mark the current message as completed and move to next"""
        if self.pending_messages:
            current_message = self.pending_messages.pop(0)
            current_message.mark_displayed()
            self.archived_messages.append(current_message)
    
    def has_pending_messages(self) -> bool:
        """Check if there are messages waiting to be displayed"""
        return len(self.pending_messages) > 0
# [file content end]
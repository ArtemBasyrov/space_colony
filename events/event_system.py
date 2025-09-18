# event_system.py
class EventManager:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type, callback):
        """Subscribe to events of a specific type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type, callback):
        """Unsubscribe from events of a specific type"""
        if event_type in self.subscribers:
            if callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
    
    def publish(self, event):
        """Publish an event to all subscribers"""
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                callback(event)
        
        # Also publish to "all" subscribers
        if "all" in self.subscribers:
            for callback in self.subscribers["all"]:
                callback(event)
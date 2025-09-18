# events.py
class EventType:
    POPULATION_INCREASE = "population_increase"
    POPULATION_DECREASE = "population_decrease"
    WAGE_WARNING = "wage_warning"
    BUILDING_WORKER_ADDED = "building_worker_added"
    BUILDING_WORKER_REMOVED = "building_worker_removed"
    RESOURCE_LOW = "resource_low"
    GAME_SAVED = "game_saved"
    DAY_ADVANCED = "day_advanced"
    # Add more event types as needed

class GameEvent:
    def __init__(self, event_type, message, data=None):
        self.type = event_type
        self.message = message
        self.data = data or {}
        
    def __str__(self):
        return f"Event({self.type}): {self.message}"
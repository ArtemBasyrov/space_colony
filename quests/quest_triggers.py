from events import EventType
from .quest import QuestState

def create_day_trigger(day_number: int):
    """Trigger when a specific day is reached"""
    return lambda game: game.day >= day_number

def create_resource_trigger(resource_type: str, amount: int):
    """Trigger when a resource reaches a certain amount"""
    return lambda game: getattr(game.resources, resource_type, 0) >= amount

def create_population_trigger(population_count: int):
    """Trigger when population reaches a certain count"""
    return lambda game: game.population.count >= population_count

def create_building_trigger(building_type, count: int = 1):
    """Trigger when a specific building type is constructed"""
    return lambda game: sum(1 for b in game.buildings if isinstance(b, building_type)) >= count

def create_event_trigger(event_type: EventType, data_condition: callable = None):
    """Trigger when a specific event occurs"""
    def trigger(game):
        # This would be connected to the event system
        # Implementation depends on how you want to track events
        return False  # Placeholder
    return trigger

def create_quest_completion_trigger(quest_id: str):
    """Trigger when another quest is completed"""
    return lambda game: any(q.quest_id == quest_id and q.state == QuestState.COMPLETED 
                           for q in game.quest_manager.quests.values())
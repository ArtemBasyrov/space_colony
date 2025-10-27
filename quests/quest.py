# [file name]: quest.py
# [file content begin]
from enum import Enum
from typing import List, Dict, Any, Callable

class QuestState(Enum):
    AVAILABLE = "available"  # Can be started but hasn't been
    ACTIVE = "active"        # Currently in progress
    COMPLETED = "completed"  # Successfully finished
    FAILED = "failed"        # Failed (if there are failure conditions)

class Quest:
    def __init__(self, 
                 quest_id: str,
                 title: str,
                 description: str,
                 detailed_text: str = "",
                 prerequisites: List['Quest'] = None,
                 triggers: List[Callable] = None,
                 objectives: List[Dict] = None,
                 rewards: List[Dict] = None,  # Now expects dictionaries, not functions
                 failure_conditions: List[Callable] = None):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.detailed_text = detailed_text
        self.state = QuestState.AVAILABLE
        self.prerequisites = prerequisites or []
        self.triggers = triggers or []  # Conditions for quest to become available
        self.objectives = objectives or []  # List of {type: str, target: any, current: any, required: any}
        self.rewards = rewards or []  # Now stores reward dictionaries
        self.failure_conditions = failure_conditions or []
        
    def update_state(self, game) -> bool:
        """Update quest state based on game conditions. Returns True if state changed."""
        old_state = self.state
        
        # Check if quest should become available
        if self.state == QuestState.AVAILABLE:
            if all(trigger(game) for trigger in self.triggers):
                # Check prerequisites
                if all(prereq.state == QuestState.COMPLETED for prereq in self.prerequisites):
                    self.state = QuestState.ACTIVE
        
        # Check objectives if active
        if self.state == QuestState.ACTIVE:
            self._update_objectives(game)
            if all(obj.get('completed', False) for obj in self.objectives):
                self.state = QuestState.COMPLETED
                
        # Check failure conditions
        if self.state == QuestState.ACTIVE:
            if any(condition(game) for condition in self.failure_conditions):
                self.state = QuestState.FAILED
                
        return old_state != self.state
    
    def _update_objectives(self, game):
        for objective in self.objectives:
            if not objective.get('completed', False):
                if self._check_objective_completion(objective, game):
                    objective['completed'] = True
    
    def _check_objective_completion(self, objective: Dict, game) -> bool:
        obj_type = objective['type']
        
        if obj_type == 'resource_amount':
            return getattr(game.resources, objective['resource_type'], 0) >= objective['required']
        elif obj_type == 'population_count':
            return game.population.count >= objective['required']
        elif obj_type == 'building_count':
            count = sum(1 for b in game.buildings if isinstance(b, objective['building_type']))
            return count >= objective['required']
        elif obj_type == 'day_reached':
            return game.day >= objective['required']
        # Add more objective types as needed
        
        return False
# [file content end]
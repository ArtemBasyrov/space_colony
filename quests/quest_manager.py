# [file name]: quest_manager.py
# [file content begin]
from typing import Dict, List
from .quest import Quest, QuestState
from events import EventType, GameEvent
from .quest_rewards import execute_reward  # NEW: Import the execute_reward function

class QuestManager:
    def __init__(self, game):
        self.game = game
        self.quests: Dict[str, Quest] = {}
        self.completed_quests: List[Quest] = []
        
        # Subscribe to game events
        self.game.event_manager.subscribe(EventType.DAY_ADVANCED, self.on_day_advanced)
        self.game.event_manager.subscribe("all", self.on_game_event)
    
    def add_quest(self, quest: Quest):
        self.quests[quest.quest_id] = quest
    
    def on_day_advanced(self, event):
        self.update_quests()
    
    def on_game_event(self, event: GameEvent):
        # Update quests when any game event occurs
        self.update_quests()
    
    def update_quests(self):
        """Update all quest states"""
        completed_quests = []
        
        for quest in self.quests.values():
            if quest.update_state(self.game):
                # Quest state changed - trigger appropriate events
                if quest.state == QuestState.COMPLETED:
                    self._grant_quest_rewards(quest)
                    completed_quests.append(quest)
                    self.game.event_manager.publish(GameEvent(
                        EventType.QUEST_COMPLETED,
                        f"Quest completed: {quest.title}",
                        {"quest": quest}
                    ))
                elif quest.state == QuestState.FAILED:
                    self.game.event_manager.publish(GameEvent(
                        EventType.QUEST_FAILED,
                        f"Quest failed: {quest.title}",
                        {"quest": quest}
                    ))
        
        # Move completed quests from active to completed list
        for quest in completed_quests:
            if quest in self.quests.values():
                self.completed_quests.append(quest)
    
    def _grant_quest_rewards(self, quest: Quest):
        """Grant rewards for a completed quest using the new dictionary system"""
        for reward_dict in quest.rewards:
            execute_reward(reward_dict, self.game)
    
    def get_active_quests(self) -> List[Quest]:
        return [q for q in self.quests.values() if q.state == QuestState.ACTIVE]
    
    def get_available_quests(self) -> List[Quest]:
        return [q for q in self.quests.values() if q.state == QuestState.AVAILABLE]
    
    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests (both from current session and previously completed)"""
        return self.completed_quests
# [file content end]
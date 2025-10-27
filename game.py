# [file name]: game.py
# [file content begin]
# game.py
import pygame

from resources import ResourceManager
from population import Population
from buildings import Mine, EnergyGenerator, OxygenGenerator, HydroponicFarm, Hospital, HabitatBlock
from market import Market
from stock_market import StockMarket 
from graphics import Graphics
from events.event_system import EventManager
from events import EventType, GameEvent
from quests import QuestManager
from quests.quest import Quest
from construction import ConstructionSystem
from quests import QuestManager
from quests.quest_definitions import get_initial_quests
from messages import MessageManager
from messages.message_definitions import get_initial_messages


# Initialize pygame
pygame.init()

class Game:
    def __init__(self):
        self.resources = ResourceManager()
        self.population = Population(self)
        self.buildings = [
            Mine(),
            EnergyGenerator(),
            OxygenGenerator(),
            HydroponicFarm(),
            Hospital(),
            HabitatBlock()
        ]
        self.market = Market()
        self.stock_market = StockMarket(self.market, self.resources)
        self.day = 1
        self.event_manager = EventManager()

        # Construction system
        self.construction_system = ConstructionSystem(self)
        
        # Quest system
        self.quest_manager = QuestManager(self)
        self._initialize_quests()
        
        # Message system
        self.message_manager = MessageManager(self)
        self._initialize_messages()
        
        # Check for initial messages - NEW
        self.message_manager.check_pending_messages()
        
        self.graphics = Graphics(self)
        
    def _initialize_quests(self):
        """Initialize starting quests"""
        for quest in get_initial_quests():
            self.quest_manager.add_quest(quest)

    def _initialize_messages(self):
        """Initialize starting messages"""
        for message in get_initial_messages():
            self.message_manager.add_message(message)

    def check_midgame_quests(self):
        """Check and add midgame quests when appropriate"""
        if self.day >= 20:
            for quest in get_midgame_quests():
                if quest.quest_id not in self.quest_manager.quests:
                    self.quest_manager.add_quest(quest)
        
    def next_day(self):
        """Advance to the next day"""
        self.resources.update(self.population, self.buildings)
        self.population.update(self.resources, self.buildings)
        self.market.update_market()
        self.stock_market.update_market(self.day)
        self.quest_manager.update_quests()
        
        self.day += 1
        
        # Publish day advanced event
        self.event_manager.publish(GameEvent(
            EventType.DAY_ADVANCED,
            f"Day {self.day} has begun",
            {"day": self.day}
        ))
        
        # Check for pending messages
        self.message_manager.check_pending_messages()
        
        # Check for game over
        if self.population.count <= 0:
            self.graphics.show_message("Game Over! Your colony has failed.")
            return False
        return True

    def run(self):
        """Run the game with graphical interface"""
        self.graphics.run()
# [file content end]
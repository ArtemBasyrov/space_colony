# game.py
import pygame
from resources import ResourceManager
from population import Population
from buildings import Mine, EnergyGenerator, OxygenGenerator, HydroponicFarm, Hospital, HabitatBlock
from market import Market
from graphics import Graphics
from events.event_system import EventManager
from events import EventType, GameEvent


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
        self.day = 1
        self.event_manager = EventManager()  # Add event manager

        # Construction system
        self.construction_mode = False
        self.selected_building_type = None
        self.pending_construction = None  # (building_type, cost)

        self.graphics = Graphics(self)
        
    def next_day(self):
        """Advance to the next day"""
        self.resources.update(self.population, self.buildings)
        self.population.update(self.resources, self.buildings)
        self.market.update_market()
        self.day += 1
        
        # Publish day advanced event
        self.event_manager.publish(GameEvent(
            EventType.DAY_ADVANCED,
            f"Day {self.day} has begun",
            {"day": self.day}
        ))
        
        # Check for game over
        if self.population.count <= 0:
            self.graphics.show_message("Game Over! Your colony has failed.")
            return False
        return True
        
        
    def run(self):
        """Run the game with graphical interface"""
        self.graphics.run()
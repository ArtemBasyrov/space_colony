# game.py
import pygame
from resources import ResourceManager
from population import Population
from buildings import Mine, EnergyGenerator, OxygenGenerator, HydroponicFarm, Hospital, HabitatBlock
from market import Market
from graphics import Graphics
from events.event_system import EventManager
from events import EventType, GameEvent
import sys
import os

def resource_path(relative_path):
    """ Get the absolute path to a resource """
    try:
        # PyInstaller and cx_Freeze use different methods
        # For cx_Freeze, the assets are in the same directory as the executable
        if hasattr(sys, 'frozen'):
            # Running as compiled executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(__file__)
        
        full_path = os.path.join(base_path, relative_path)
        
        return full_path
    except Exception as e:
        print(f"Error in resource_path: {e}")
        return relative_path  # Fallback to relative path

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
        self.resources.load_image('oxygen', resource_path('assets/images/oxygen.png'), (24, 24))
        self.resources.load_image('food', resource_path('assets/images/food.png'), (24, 24))
        self.resources.load_image('minerals', resource_path('assets/images/minerals.png'), (24, 24))
        self.resources.load_image('energy', resource_path('assets/images/energy.png'), (24, 24))
        self.resources.load_image('credits', resource_path('assets/images/credits.png'), (24, 24))

        
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
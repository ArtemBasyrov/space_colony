# graphics.py
import pygame
from pygame.locals import *

from .main_screen import MainScreen
from .market_screen import MarketScreen
from .wages_screen import WagesScreen
from events import EventType
from .construction_screen import ConstructionScreen 
from .stock_market_screen import StockMarketScreen
from .settings_menu import SettingsMenu
from .quest_screen import QuestScreen
from .message_screen import MessageScreen  

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

class Graphics:
    def __init__(self, game):
        self.game = game
        pygame.init()
        
        # Screen dimensions
        self.width, self.height = 1024, 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Space Colony Manager - Extreme Capitalism")
        
        # Colors
        self.colors = {
            'background': (10, 20, 40),
            'panel': (30, 40, 60),
            'text': (220, 220, 220),
            'highlight': (0, 150, 255),
            'panel_warning': (120, 40, 40),
            'highlight_warning': (200, 50, 50),
            'warning': (255, 100, 100),
            'success': (100, 255, 100),
            'resource': (150, 200, 255),
            'button': (50, 80, 120),
            'button_hover': (70, 100, 140),
            'button_text': (220, 220, 220)
        }
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.header_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.normal_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)

        self.icons = {}
        self.load_icons()
        
        # Screens
        self.screens = {
            'main': MainScreen(self),
            'market': MarketScreen(self),
            'wages': WagesScreen(self),
            'construction': ConstructionScreen(self),
            'stock_market': StockMarketScreen(self),
            'quests': QuestScreen(self),
            'message': MessageScreen(self),
        }
        self.current_screen = 'main'

        # Add settings menu
        self.settings_menu = SettingsMenu(self)
        
        # UI state
        self.message = ""
        self.message_timer = 0
        
        # Subscribe to events
        self.setup_event_handlers()

    def format_number(self, value):
        """Format numbers for display"""
        if isinstance(value, (int, float)):
            if value == int(value):
                return str(int(value))
            return f"{value:.2f}"
        return str(value)
        
    def setup_event_handlers(self):
        """Subscribe to game events"""
        # Subscribe to all population events
        self.game.event_manager.subscribe(EventType.POPULATION_INCREASE, self.handle_event)
        self.game.event_manager.subscribe(EventType.POPULATION_DECREASE, self.handle_event)
        self.game.event_manager.subscribe(EventType.WAGE_WARNING, self.handle_event)
        
        # You can add more event subscriptions here as needed
        
    def handle_event(self, event):
        """Handle incoming game events"""
        self.show_message(event.message)

    # graphics.py - update the load_icons method
    def load_icons(self):
        """Load all resource icons"""
        icon_paths = {
            'oxygen': 'assets/images/oxygen.png',
            'food': 'assets/images/food.png', 
            'energy': 'assets/images/energy.png',
            'credits': 'assets/images/credits.png',
            'hydrogen': 'assets/images/hydrogen.png',
            'fuel': 'assets/images/fuel.png',
            'regolith': 'assets/images/minerals.png'
        }
        
        for resource, path in icon_paths.items():
            try:
                icon = pygame.image.load(path)
                if icon.get_alpha():
                    icon = icon.convert_alpha()
                else:
                    icon = icon.convert()
                # Scale to consistent size if needed
                icon = pygame.transform.scale(icon, (24, 24))
                self.icons[resource] = icon
            except pygame.error:
                print(f"Warning: Could not load icon {path}")
                # Create fallback icon
                fallback = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(fallback, (200, 200, 200), (12, 12), 10)
                text = self.small_font.render(resource[0].upper(), True, (255, 255, 255))
                text_rect = text.get_rect(center=(12, 12))
                fallback.blit(text, text_rect)
                self.icons[resource] = fallback
        
    def set_screen(self, screen_name):
        """Switch to a different screen"""
        if screen_name in self.screens:
            self.current_screen = screen_name
            
    def show_message(self, message):
        """Display a temporary message"""
        self.message = message
        self.message_timer = 120  # Show for 2 seconds at 60 FPS

    def check_pending_messages(self):  # NEW
        """Check if there are pending messages to display"""
        if self.game.message_manager.has_pending_messages():
            next_message = self.game.message_manager.get_next_pending_message()
            if next_message:
                message_screen = self.screens['message']
                message_screen.set_message(next_message)
                self.set_screen('message')
                return True
        return False
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                # Check for pending messages first - NEW
                if self.current_screen == 'main' and self.game.message_manager.has_pending_messages():
                    if self.check_pending_messages():
                        continue  # Skip other event handling when showing message
                
                # Handle settings menu first if it's visible
                if self.settings_menu.visible:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        action = self.settings_menu.handle_click(event.pos)
                        if action:
                            self.handle_settings_action(action)
                    elif event.type == pygame.KEYDOWN:
                        if self.settings_menu.handle_keydown(event):
                            continue  # Event was handled by settings menu
                else:
                    # Pass events to current screen only if settings menu is not visible
                    current_screen = self.screens[self.current_screen]
                    if hasattr(current_screen, 'handle_event'):
                        current_screen.handle_event(event)
            
            # Draw the current screen
            self.screens[self.current_screen].draw()
            
            # Draw settings menu on top if visible
            self.settings_menu.draw()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

    def handle_settings_action(self, action):
        """Handle actions from the settings menu"""
        if action == "save":
            self.show_message("Game saved!")
            # Add your actual save game logic here
            self.settings_menu.hide()
            
        elif action == "quit":
            pygame.quit()
            import sys
            sys.exit()
            
        elif action == "back":
            self.settings_menu.hide()
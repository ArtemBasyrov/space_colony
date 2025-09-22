import pygame
import math
from abc import ABC, abstractmethod

class Screen(ABC):
    # screen.py - update the __init__ method
    def __init__(self, graphics):
        self.graphics = graphics
        self.game = graphics.game
        self.buttons = {}
        self.last_mouse_state = False
        
        # Add hex map colors
        self.hex_colors = {
            'hex_default': (60, 70, 90),
            'hex_selected': (80, 100, 130),
            'hex_border': (30, 40, 60),
            'hex_building': (100, 120, 150)
        }
        
        # Merge with existing colors
        self.all_colors = {**self.graphics.colors, **self.hex_colors}
        
        
    @abstractmethod
    def draw(self):
        pass
    
    def handle_event(self, event):
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
    
    def handle_click(self, mouse_pos):
        """Handle mouse click on buttons"""
        for action, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                self.on_button_click(action)
                break
    
    def on_button_click(self, action):
        """Override this method in subclasses to handle button clicks"""
        pass
    
    def format_number(self, value):
        """Format numbers for display"""
        if isinstance(value, (int, float)):
            if value == int(value):
                return str(int(value))
            return f"{value:.2f}"
        return str(value)
    
    def draw_panel(self, x, y, width, height, title=None, warning=False):
        """Draw a UI panel with optional title"""
        if warning:
            panel_color = self.graphics.colors['panel_warning']
            border_color = self.graphics.colors['highlight_warning']
        else:
            panel_color = self.graphics.colors['panel']
            border_color = self.graphics.colors['highlight']

        pygame.draw.rect(self.graphics.screen, panel_color, (x, y, width, height), border_radius=5)
        pygame.draw.rect(self.graphics.screen, border_color, (x, y, width, height), 2, border_radius=5)
        
        if title:
            title_text = self.graphics.header_font.render(title, True, self.graphics.colors['text'])
            self.graphics.screen.blit(title_text, (x + 10, y + 10))
    
    def draw_button(self, x, y, width, height, text, action=None):
        """Draw a button and return hover state"""
        button_rect = pygame.Rect(x, y, width, height)
        hover = button_rect.collidepoint(pygame.mouse.get_pos())
        
        # Draw button
        color = self.graphics.colors['button_hover'] if hover else self.graphics.colors['button']
        pygame.draw.rect(self.graphics.screen, color, button_rect, border_radius=3)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], button_rect, 1, border_radius=3)
        
        # Draw text
        text_surf = self.graphics.normal_font.render(text, True, self.graphics.colors['button_text'])
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.graphics.screen.blit(text_surf, text_rect)
        
        # Store button for click detection
        if action:
            self.buttons[action] = button_rect
            
        return hover
    
    def draw_resource_bar(self, x, y, width, value, max_value, label, color):
        """Draw a resource bar"""
        # Background
        pygame.draw.rect(self.graphics.screen, (50, 50, 50), (x, y, width, 20), border_radius=3)
        
        # Fill
        fill_width = max(0, min(width, (value / max_value) * width)) if max_value > 0 else 0
        pygame.draw.rect(self.graphics.screen, color, (x, y, fill_width, 20), border_radius=3)
        
        # Border
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['text'], (x, y, width, 20), 1, border_radius=3)
        
        # Text
        text = f"{label}: {self.format_number(value)}"
        if max_value > 0:
            text += f"/{self.format_number(max_value)}"
        
        text_surf = self.graphics.small_font.render(text, True, self.graphics.colors['text'])
        self.graphics.screen.blit(text_surf, (x + 5, y + 2))
    
    def draw_resource_indicator(self, x, y, resource_name, value, change, color, resource_key):
        """Draw a resource indicator with icon, value, and expected change"""
        # Background panel
        pygame.draw.rect(self.graphics.screen, (40, 50, 70), (x, y, 180, 40), border_radius=5)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (x, y, 180, 40), 1, border_radius=5)
        
        # Icon
        if resource_key in self.graphics.icons:
            self.graphics.screen.blit(self.graphics.icons[resource_key], (x + 8, y + 8))
        
        # Resource name and value
        name_text = self.graphics.small_font.render(f"{resource_name}: {self.format_number(value)}", True, self.graphics.colors['text'])
        self.graphics.screen.blit(name_text, (x + 40, y + 5))
        
        # Change indicator
        change_text = f"{change:+.1f}"
        change_color = self.graphics.colors['success'] if change >= 0 else self.graphics.colors['warning']
        change_surf = self.graphics.small_font.render(change_text, True, change_color)
        self.graphics.screen.blit(change_surf, (x + 40, y + 20))
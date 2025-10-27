import pygame
import math
import random
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

    def draw_animated_background(self):
        """Draw an animated grid background with distortion wave"""
        screen = self.graphics.screen
        width, height = self.graphics.width, self.graphics.height
        
        # Use the original background color as base
        screen.fill(self.graphics.colors['background'])
        
        # Grid parameters - match original color scheme but slightly lighter
        grid_size = 40
        base_grid_color = (30, 50, 70)  # Slightly lighter than background
        distortion_color = (60, 100, 140)  # Even lighter for distortion effect
        
        # Wave parameters
        current_time = pygame.time.get_ticks() / 1000.0
        wave_speed = 1.5
        wave_frequency = 0.015
        wave_amplitude = 4.0
        wave_width = 120  # Width of the distortion area
        
        # Extended range for wave starting position (starts earlier)
        extended_width = width + 200
        
        # Calculate wave cycle with waiting time
        pause_duration = 3.0  # Duration of pause between waves
        wave_duration = 13.0   # Duration of the actual wave movement
        cycle_duration = wave_duration + pause_duration # Total duration of one complete cycle (wave + pause)
        
        # Calculate position in cycle
        cycle_position = current_time % cycle_duration
        
        if cycle_position <= wave_duration:
            # Wave is active - calculate position across extended range
            progress = cycle_position / wave_duration
            wave_x = progress * extended_width - 100  # Start 100px left of screen
        else:
            # Pause period - no wave visible
            wave_x = -wave_width - 100  # Positioned completely off-screen
        
        # Draw base grid (static)
        for x in range(0, width, grid_size):
            pygame.draw.line(screen, base_grid_color, (x, 0), (x, height), 1)
        
        for y in range(0, height, grid_size):
            pygame.draw.line(screen, base_grid_color, (0, y), (width, y), 1)
        
        # Only draw distortion wave if wave is active (not in pause period)
        if cycle_position <= wave_duration:
            # Draw distortion wave effect
            for x in range(0, width, 2):  # More detailed sampling for smooth wave
                # Calculate distance from wave center and intensity
                dist_from_wave = abs(x - wave_x)
                if dist_from_wave < wave_width:
                    # Calculate wave intensity (1 at center, 0 at edges)
                    intensity = 1.0 - (dist_from_wave / wave_width)
                    
                    # Calculate distortion offset using sine wave
                    distortion_offset = math.sin(x * wave_frequency - current_time * wave_speed) * wave_amplitude * intensity
                    
                    # Draw distorted vertical lines within wave area
                    if x % grid_size == 0:
                        start_y = 0
                        end_y = height
                        # Draw the distorted line
                        pygame.draw.line(screen, distortion_color, 
                                    (x + distortion_offset, start_y), 
                                    (x + distortion_offset, end_y), 
                                    1)
                    
                    # Draw distorted horizontal lines within wave area
                    for y in range(0, height, grid_size):
                        if y % grid_size == 0:
                            # Each horizontal line gets its own distortion based on y position
                            h_distortion = math.sin(y * 0.02 + current_time * 2) * wave_amplitude * intensity * 0.5
                            start_x = max(0, x - 10)
                            end_x = min(width, x + 10)
                            pygame.draw.line(screen, distortion_color,
                                        (start_x, y + h_distortion),
                                        (end_x, y + h_distortion),
                                        1)
        
        # Add subtle scanlines for that monitor feel
        scanline_color = (15, 25, 35, 50)  # Very subtle dark scanlines
        for y in range(0, height, 3):
            scan_surface = pygame.Surface((width, 1), pygame.SRCALPHA)
            scan_surface.fill(scanline_color)
            screen.blit(scan_surface, (0, y))

        # Add some random "static" dots for that old monitor feel
        for _ in range(5):  # Only a few dots for performance
            dot_x = random.randint(0, width)
            dot_y = random.randint(0, height)
            dot_size = random.randint(1, 2)
            brightness = random.randint(30, 60)
            pygame.draw.circle(screen, (brightness, brightness + 20, brightness), 
                            (dot_x, dot_y), dot_size)

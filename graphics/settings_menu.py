# settings_menu.py
import pygame

class SettingsMenu:
    def __init__(self, graphics):
        self.graphics = graphics
        self.visible = False
        self.buttons = {}
        
    def show(self):
        """Show the settings menu"""
        self.visible = True
        
    def hide(self):
        """Hide the settings menu"""
        self.visible = False
        
    def draw(self):
        """Draw the settings menu"""
        if not self.visible:
            return
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.graphics.width, self.graphics.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.graphics.screen.blit(overlay, (0, 0))
        
        # Calculate menu dimensions and position
        menu_width = 260
        menu_height = 300
        menu_x = (self.graphics.width - menu_width) // 2
        menu_y = (self.graphics.height - menu_height) // 2
        
        # Draw menu background
        pygame.draw.rect(self.graphics.screen, (25, 35, 55), 
                        (menu_x, menu_y, menu_width, menu_height), 
                        border_radius=10)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], 
                        (menu_x, menu_y, menu_width, menu_height), 
                        2, border_radius=10)
        
        # Draw title
        title_text = self.graphics.header_font.render("Game Menu", True, self.graphics.colors['text'])
        title_rect = title_text.get_rect(center=(menu_x + menu_width // 2, menu_y + 30))
        self.graphics.screen.blit(title_text, title_rect)
        
        # Button dimensions
        button_width = 200
        button_height = 40
        button_x = menu_x + (menu_width - button_width) // 2
        
        # Calculate vertical positions for buttons
        button_start_y = menu_y + 80
        button_spacing = 60
        
        # Draw buttons
        self.draw_button(button_x, button_start_y, button_width, button_height, "Save Game", "save")
        self.draw_button(button_x, button_start_y + button_spacing, button_width, button_height, "Quit", "quit")
        
        # Back button positioned lower with more spacing
        back_button_y = button_start_y + button_spacing * 2 + 20
        self.draw_button(button_x, back_button_y, button_width, button_height, "Back", "back")
        
    def draw_button(self, x, y, width, height, text, action):
        """Draw a button and store its rect for click detection"""
        button_rect = pygame.Rect(x, y, width, height)
        hover = button_rect.collidepoint(pygame.mouse.get_pos())
        
        # Draw button
        color = self.graphics.colors['button_hover'] if hover else self.graphics.colors['button']
        pygame.draw.rect(self.graphics.screen, color, button_rect, border_radius=5)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], button_rect, 1, border_radius=5)
        
        # Draw text
        text_surf = self.graphics.normal_font.render(text, True, self.graphics.colors['button_text'])
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.graphics.screen.blit(text_surf, text_rect)
        
        # Store button for click detection
        self.buttons[action] = button_rect
        
        return hover
        
    def handle_click(self, pos):
        """Handle clicks on settings menu buttons"""
        if not self.visible:
            return None
            
        for action, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return action
        return None
        
    def handle_keydown(self, event):
        """Handle keyboard events for settings menu"""
        if not self.visible:
            return False
            
        if event.key == pygame.K_ESCAPE:
            self.hide()
            return True
            
        return False
import pygame

class BottomBar:
    def __init__(self, graphics):
        self.graphics = graphics
        self.width = graphics.width
        self.height = 60
        self.panel_y = graphics.height - self.height
        self.buttons = {}
    
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
    
    def draw(self):
        """Draw the bottom action bar"""
        # Draw background panel
        pygame.draw.rect(self.graphics.screen, (25, 35, 55), (0, self.panel_y, self.width, self.height))
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (0, self.panel_y, self.width, self.height), 1)
        
        # Draw buttons - add construction button
        button_y = self.panel_y + 10
        button_spacing = 160
        
        self.draw_button(40, button_y, 150, 40, "Next Day", "next_day")
        self.draw_button(40 + button_spacing, button_y, 150, 40, "Market", "market")
        self.draw_button(40 + button_spacing * 2, button_y, 150, 40, "Wages", "wages")
        self.draw_button(40 + button_spacing * 3, button_y, 150, 40, "Construct", "construct")  # New button
        self.draw_button(40 + button_spacing * 4, button_y, 150, 40, "Save Game", "save")
        self.draw_button(40 + button_spacing * 5, button_y, 150, 40, "Quit", "quit")
    
    def handle_click(self, pos):
        """Handle clicks on bottom bar buttons"""
        for action, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return action
        return None
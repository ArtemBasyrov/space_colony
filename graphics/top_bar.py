import pygame

class TopBar:
    def __init__(self, graphics):
        self.graphics = graphics
        self.width = graphics.width
        self.height = 50
    
    def draw_resource_indicator(self, x, y, resource_name, value, change, color, resource_key):
        """Draw a resource indicator with icon, value, and expected change"""
        # Background panel
        pygame.draw.rect(self.graphics.screen, (40, 50, 70), (x, y, 180, 40), border_radius=5)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (x, y, 180, 40), 1, border_radius=5)
        
        # Icon - get from the current screen's icons
        current_screen = self.graphics.screens[self.graphics.current_screen]
        if hasattr(current_screen, 'icons') and resource_key in current_screen.graphics.icons:
            self.graphics.screen.blit(current_screen.graphics.icons[resource_key], (x + 8, y + 8))
        
        # Resource name and value
        name_text = self.graphics.small_font.render(f"{resource_name}: {self.graphics.format_number(value)}", True, self.graphics.colors['text'])
        self.graphics.screen.blit(name_text, (x + 40, y + 5))
        
        # Change indicator
        change_text = f"{change:+.1f}"
        change_color = self.graphics.colors['success'] if change >= 0 else self.graphics.colors['warning']
        change_surf = self.graphics.small_font.render(change_text, True, change_color)
        self.graphics.screen.blit(change_surf, (x + 40, y + 20))
    
    def draw(self, resources, calculated_changes):
        """Draw the top resource bar"""
        # Background
        pygame.draw.rect(self.graphics.screen, (25, 35, 55), (0, 0, self.width, self.height))
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (0, 0, self.width, self.height), 1)
        
        # Draw resource indicators
        self.draw_resource_indicator(10, 5, "Oxygen", resources.oxygen, calculated_changes['oxygen'], (100, 200, 255), 'oxygen')
        self.draw_resource_indicator(200, 5, "Food", resources.food, calculated_changes['food'], (150, 255, 100), 'food')
        self.draw_resource_indicator(390, 5, "Minerals", resources.minerals, calculated_changes['minerals'], (200, 150, 100), 'minerals')
        self.draw_resource_indicator(580, 5, "Energy", resources.energy, calculated_changes['energy'], (255, 200, 50), 'energy')
        self.draw_resource_indicator(770, 5, "Credits", resources.credits, calculated_changes['credits'], (255, 215, 0), 'credits')
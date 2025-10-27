import pygame

class TopBar:
    def __init__(self, graphics):
        self.graphics = graphics
        self.width = graphics.width
        self.height = 50
        self.resource_panel_width = self.width - 20
    
    def draw_resource_indicator(self, x, y, resource_name, value, change, resource_key, width):
        """Draw a resource indicator with icon, value, and expected change"""
        # Background panel - highlight in red if resource is zero
        if value <= 0 and change < 0:
            panel_color = self.graphics.colors['panel_warning']  # Red background for critical resources
            border_color = self.graphics.colors['highlight_warning']  # Red border
        else:
            panel_color = self.graphics.colors['panel']   # Normal background
            border_color = self.graphics.colors['highlight']  # Normal border
        
        pygame.draw.rect(self.graphics.screen, panel_color, (x, y, width, self.height-10), border_radius=5)
        pygame.draw.rect(self.graphics.screen, border_color, (x, y, width, self.height-10), 1, border_radius=5)
        
        # Icon - get from the graphics's icons
        if hasattr(self.graphics, 'icons') and resource_key in self.graphics.icons:
            self.graphics.screen.blit(self.graphics.icons[resource_key], (x + 8, y + 8))
        
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
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['panel'], (0, 0, self.width, self.height))
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (0, 0, self.width, self.height), 1)
        
        # Get number of resources to display and calculate spacing
        num_resources = len(calculated_changes.keys())
        spacing = (self.resource_panel_width-10*num_resources) // num_resources

        # Draw resource indicators
        self.draw_resource_indicator(10, 5, "Oxygen", resources.oxygen, calculated_changes['oxygen'], 'oxygen', spacing)
        self.draw_resource_indicator(1*spacing+20, 5, "Hydrogen", resources.hydrogen, calculated_changes['hydrogen'], 'hydrogen', spacing)
        self.draw_resource_indicator(2*spacing+30, 5, "Food", resources.food, calculated_changes['food'], 'food', spacing)
        self.draw_resource_indicator(3*spacing+40, 5, "Regolith", resources.regolith, calculated_changes['regolith'], 'regolith', spacing)
        self.draw_resource_indicator(4*spacing+50, 5, "Energy", resources.energy, calculated_changes['energy'], 'energy', spacing)
        self.draw_resource_indicator(5*spacing+60, 5, "Fuel", resources.fuel, calculated_changes['fuel'], 'fuel', spacing)
        self.draw_resource_indicator(6*spacing+70, 5, "Credits", resources.credits, calculated_changes['credits'], 'credits', spacing)
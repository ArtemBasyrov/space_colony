import pygame

class BuildingMenu:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.selected_building = None
        self.rect = pygame.Rect(840, 420, 164, 180)
        
        # Store button rectangles for click handling
        self.add_button_rect = pygame.Rect(850, 550, 70, 25)
        self.remove_button_rect = pygame.Rect(930, 550, 70, 25)
        self.close_button_rect = pygame.Rect(890, 580, 70, 25)
    
    def format_resource_value(self, value):
        """Format resource values to 2 decimal places"""
        return f"{value:.2f}"
    
    def show(self, building):
        """Show the building menu"""
        self.visible = True
        self.selected_building = building
    
    def hide(self):
        """Hide the building menu"""
        self.visible = False
        self.selected_building = None
    
    def handle_click(self, pos):
        """Handle clicks on building menu buttons - returns action if handled, None otherwise"""
        if not self.visible or not self.selected_building:
            return None
        
        # Check if click is on any of the building menu buttons
        if self.add_button_rect.collidepoint(pos):
            return "add_worker"
        elif self.remove_button_rect.collidepoint(pos):
            return "remove_worker"
        elif self.close_button_rect.collidepoint(pos):
            return "close_building_menu"
        
        return None
    
    # building_menu.py - update the draw method
    def draw(self):
        """Draw the building menu if visible"""
        if not self.visible or not self.selected_building:
            return
        
        # Draw menu panel
        self.screen.draw_panel(self.rect.x, self.rect.y, self.rect.width, self.rect.height, self.selected_building.name)
        y_offset = self.rect.y + 60

        # Add housing info for Habitat Blocks
        if hasattr(self.selected_building, 'residents'):
            y_offset -= 20
            housing_text = self.screen.graphics.small_font.render(f"Residents: {len(self.selected_building.residents)}/{self.selected_building.capacity}", True, self.screen.graphics.colors['text'])
            self.screen.graphics.screen.blit(housing_text, (self.rect.x + 10, y_offset))
            
            y_offset += 25
            quality_text = self.screen.graphics.small_font.render(f"Quality: {self.screen.format_number(self.selected_building.quality)}", True, self.screen.graphics.colors['text'])
            self.screen.graphics.screen.blit(quality_text, (self.rect.x + 10, y_offset))
            
            y_offset += 25
            rent_text = self.screen.graphics.small_font.render(f"Rent:", True, self.screen.graphics.colors['text'])
            self.screen.graphics.screen.blit(rent_text, (self.rect.x + 10, y_offset))
            icon = self.screen.graphics.icons["credits"]
            self.screen.graphics.screen.blit(icon, (self.rect.x + 50, y_offset-3))
            rent_text = self.screen.graphics.small_font.render(f"{self.selected_building.rent}", True, self.screen.graphics.colors['text'])
            self.screen.graphics.screen.blit(rent_text, (self.rect.x + 78, y_offset))

            self.draw_button(self.close_button_rect, "Close")
            return  # Skip worker and resource info for habitats
        
        # Draw worker count
        text = self.screen.graphics.small_font.render(f"Workers: {self.selected_building.assigned_workers}/{self.selected_building.max_workers}", True, self.screen.graphics.colors['text'])
        self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 40))
        
        # Show production/consumption info with ICONS instead of symbols
        production = self.selected_building.calculate_production()
        consumption = self.selected_building.calculate_consumption()
    
        for resource, amount in production.items():
            if amount > 0:
                # Use icon instead of symbol
                if resource in self.screen.graphics.icons:
                    icon = self.screen.graphics.icons[resource]
                    self.screen.graphics.screen.blit(icon, (self.rect.x + 10, y_offset))
                
                formatted_amount = self.format_resource_value(amount)
                text = self.screen.graphics.small_font.render(f"+{formatted_amount}", True, self.screen.graphics.colors['success'])
                self.screen.graphics.screen.blit(text, (self.rect.x + 35, y_offset + 4))  # Offset text to right of icon
                y_offset += 25  # Slightly more spacing for icons
        
        for resource, amount in consumption.items():
            if amount > 0:
                # Use icon instead of symbol
                if resource in self.screen.graphics.icons:
                    icon = self.screen.graphics.icons[resource]
                    self.screen.graphics.screen.blit(icon, (self.rect.x + 10, y_offset))
                
                formatted_amount = self.format_resource_value(amount)
                text = self.screen.graphics.small_font.render(f"-{formatted_amount}", True, self.screen.graphics.colors['warning'])
                self.screen.graphics.screen.blit(text, (self.rect.x + 35, y_offset + 4))  # Offset text to right of icon
                y_offset += 25  # Slightly more spacing for icons
        
        # Draw worker management buttons
        self.draw_button(self.add_button_rect, "Add")
        self.draw_button(self.remove_button_rect, "Remove")
        self.draw_button(self.close_button_rect, "Close")
        
    def draw_button(self, rect, text):
        """Draw a button without adding it to the screen's button system"""
        hover = rect.collidepoint(pygame.mouse.get_pos())
        
        # Draw button
        color = self.screen.graphics.colors['button_hover'] if hover else self.screen.graphics.colors['button']
        pygame.draw.rect(self.screen.graphics.screen, color, rect, border_radius=3)
        pygame.draw.rect(self.screen.graphics.screen, self.screen.graphics.colors['highlight'], rect, 1, border_radius=3)
        
        # Draw text
        text_surf = self.screen.graphics.normal_font.render(text, True, self.screen.graphics.colors['button_text'])
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.graphics.screen.blit(text_surf, text_rect)

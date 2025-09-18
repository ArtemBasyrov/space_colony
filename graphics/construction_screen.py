# construction_screen.py
import pygame
from .screen import Screen
from buildings import get_building_price, create_building_from_name, BUILDING_CATALOG, get_building_name, get_building_description

class ConstructionScreen(Screen):
    def __init__(self, graphics):
        super().__init__(graphics)
        self.selected_building = None
        self.scroll_offset = 0
        self.max_visible_buildings = 4  # Number of buildings that can fit in the visible area
    
    def on_button_click(self, action):
        """Handle button clicks in construction screen"""
        if action == "back":
            self.graphics.set_screen('main')
            
        elif action.startswith("select_"):
            building_type = action.split("_")[1]
            self.selected_building = building_type
            
        elif action == "confirm_purchase" and self.selected_building:
            self.purchase_building()
            
        elif action == "scroll_up":
            self.scroll_offset = max(0, self.scroll_offset - 1)
            
        elif action == "scroll_down":
            max_offset = max(0, len(BUILDING_CATALOG) - self.max_visible_buildings)
            self.scroll_offset = min(max_offset, self.scroll_offset + 1)
    
    # construction_screen.py - update the purchase_building method
    def purchase_building(self):
        """Purchase the selected building"""
        
        building_type = self.selected_building
        price = get_building_price(building_type)
        
        if self.game.resources.credits >= price:
            # Deduct credits and enter construction mode
            self.game.resources.credits -= price
            self.game.construction_mode = True
            self.game.selected_building_type = building_type
            self.game.pending_construction = (building_type, price)
            
            # Store building info for potential refund
            from buildings import get_building_name
            building_name = get_building_name(building_type)
            self.game.graphics.show_message(f"Purchased {building_name} for {price} credits. Click on an empty hexagon to place it. Press ESC to cancel.")
            self.graphics.set_screen('main')
        else:
            self.graphics.show_message("Not enough credits to purchase this building!")
    
    def calculate_max_production(self, building_instance):
        """Calculate production at maximum worker capacity"""
        # Temporarily set workers to max to calculate production
        original_workers = building_instance.assigned_workers
        building_instance.assigned_workers = building_instance.max_workers
        production = building_instance.calculate_production()
        consumption = building_instance.calculate_consumption()
        # Restore original worker count
        building_instance.assigned_workers = original_workers
        return production, consumption
    
    def draw(self):
        """Draw the construction screen"""
        
        # Background
        self.graphics.screen.fill(self.graphics.colors['background'])
        
        # Title
        title_text = self.graphics.title_font.render("Construction Menu", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (20, 20))
        
        # Available credits with icon and text combined
        credits_text = f"Available credits:"
        credits_surface = self.graphics.header_font.render(credits_text, True, self.graphics.colors['text'])
        self.graphics.screen.blit(credits_surface, (50, 60))
        
        # Draw credits icon next to text
        if 'credits' in self.graphics.icons:
            self.graphics.screen.blit(self.graphics.icons['credits'], (250, 60))

        credits_text = f"{self.format_number(self.game.resources.credits)}"
        credits_surface = self.graphics.header_font.render(credits_text, True, self.graphics.colors['text'])
        self.graphics.screen.blit(credits_surface, (275, 60))
        
        # Buildings panel
        self.draw_panel(20, 100, 984, 500, "Available Buildings")
        
        # Scroll buttons if needed
        if len(BUILDING_CATALOG) > self.max_visible_buildings:
            # Up button
            self.draw_button(950, 110, 40, 30, "↑", "scroll_up", 
                            enabled=self.scroll_offset > 0)
            
            # Down button
            self.draw_button(950, 560, 40, 30, "↓", "scroll_down", 
                            enabled=self.scroll_offset < len(BUILDING_CATALOG) - self.max_visible_buildings)
        
        # List available buildings (only visible ones)
        y_offset = 160
        building_items = list(BUILDING_CATALOG.items())
        
        for i in range(self.scroll_offset, min(self.scroll_offset + self.max_visible_buildings, len(building_items))):
            building_name, building_info = building_items[i]
            building_instance = building_info["class"]()
            price = building_info["price"]
            
            # Building card
            card_color = self.graphics.colors['button_hover'] if building_name == self.selected_building else self.graphics.colors['button']
            pygame.draw.rect(self.graphics.screen, card_color, (30, y_offset, 944, 80), border_radius=5)
            pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (30, y_offset, 944, 80), 1, border_radius=5)
            
            # Building name
            name_text = self.graphics.header_font.render(get_building_name(building_name), True, self.graphics.colors['text'])
            self.graphics.screen.blit(name_text, (40, y_offset + 10))
            
            # Price with credits icon - "Price: {credits icon} {amount}"
            price_text = self.graphics.normal_font.render(f"Price:", True, self.graphics.colors['text'])
            self.graphics.screen.blit(price_text, (60, y_offset + 40))
            if 'credits' in self.graphics.icons:
                self.graphics.screen.blit(self.graphics.icons['credits'], (110, y_offset + 37))
            price_text = self.graphics.normal_font.render(f"{price}", True, self.graphics.colors['text'])
            self.graphics.screen.blit(price_text, (137, y_offset + 40))
            
            # Building description
            desc_text = self.graphics.small_font.render(get_building_description(building_name), True, self.graphics.colors['text'])
            self.graphics.screen.blit(desc_text, (290, y_offset + 15))
            
            # Calculate max production and consumption
            max_production, max_consumption = self.calculate_max_production(building_instance)
            
            # Build the bottom line: "Max workers: X | Max production: {icon} Y"
            if hasattr(building_instance, 'residents'):
                bottom_line_parts = [f"Max residents: {building_instance.capacity}"]
            else:
                bottom_line_parts = [f"Max workers: {building_instance.max_workers}"]
            
            # Add production info
            production_items = []
            for resource, amount in max_production.items():
                if amount > 0:
                    production_items.append((resource, amount, True))
            
            # Add consumption info (as negative production)
            for resource, amount in max_consumption.items():
                if amount > 0:
                    production_items.append((resource, -amount, False))
            
            if production_items:
                bottom_line_parts.append("Max production:")
            elif hasattr(building_instance, 'residents'):
                bottom_line_parts.append("Quality:")
            
            # Draw the bottom line
            bottom_line_y = y_offset + 40
            bottom_line_x = 290
            
            # Draw "Max workers: X"
            workers_text = self.graphics.small_font.render(bottom_line_parts[0], True, self.graphics.colors['text'])
            self.graphics.screen.blit(workers_text, (bottom_line_x, bottom_line_y))
            bottom_line_x += workers_text.get_width() + 10
            
            # Draw separator and "Max production:"
            if len(bottom_line_parts) > 1:
                separator_text = self.graphics.small_font.render("|", True, self.graphics.colors['text'])
                self.graphics.screen.blit(separator_text, (bottom_line_x, bottom_line_y))
                bottom_line_x += separator_text.get_width() + 10
                
                production_label = self.graphics.small_font.render(bottom_line_parts[1], True, self.graphics.colors['text'])
                self.graphics.screen.blit(production_label, (bottom_line_x, bottom_line_y))
                bottom_line_x += production_label.get_width() + 5
            
            if hasattr(building_instance, 'residents'):
                # Draw quality for residential buildings
                quality_text = self.graphics.small_font.render(f"{self.format_number(building_instance.quality)}", True, self.graphics.colors['text'])
                self.graphics.screen.blit(quality_text, (bottom_line_x, bottom_line_y))
                bottom_line_x += quality_text.get_width() + 10

            # Draw production/consumption icons and values
            for resource, amount, is_production in production_items:
                # Draw resource icon
                if resource in self.graphics.icons:
                    self.graphics.screen.blit(self.graphics.icons[resource], (bottom_line_x, bottom_line_y))
                    bottom_line_x += 25
                
                # Draw value with appropriate color
                color = self.graphics.colors['success'] if is_production else self.graphics.colors['warning']
                value_text = self.graphics.small_font.render(f"{amount:+.1f}", True, color)
                self.graphics.screen.blit(value_text, (bottom_line_x, bottom_line_y))
                bottom_line_x += value_text.get_width() + 10
            
            # Select button
            self.draw_button(850, y_offset + 25, 100, 30, "Select", f"select_{building_name}")
            
            y_offset += 90
        
        # Purchase button (if building selected)
        if self.selected_building:
            price = get_building_price(self.selected_building)
            
            # Create button with text and icon: "Purchase for {credit icon} {credit amount}"
            button_text = f"Purchase for {price}"
            text_width = self.graphics.normal_font.size(button_text)[0]
            button_width = text_width + 60  # Space for icon and padding
            
            button_rect = pygame.Rect(400, 620, button_width, 40)
            hover = button_rect.collidepoint(pygame.mouse.get_pos())
            
            # Draw button
            color = self.graphics.colors['button_hover'] if hover else self.graphics.colors['button']
            pygame.draw.rect(self.graphics.screen, color, button_rect, border_radius=3)
            pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], button_rect, 1, border_radius=3)
            
            # Draw text
            text_surf = self.graphics.normal_font.render(button_text, True, self.graphics.colors['button_text'])
            text_rect = text_surf.get_rect(center=(button_rect.centerx + 10, button_rect.centery))
            self.graphics.screen.blit(text_surf, text_rect)
            
            # Draw credits icon
            if 'credits' in self.graphics.icons:
                icon_rect = self.graphics.icons['credits'].get_rect(center=(button_rect.centerx - text_width//2 - 10, button_rect.centery))
                self.graphics.screen.blit(self.graphics.icons['credits'], icon_rect)
            
            # Store button for click detection
            self.buttons["confirm_purchase"] = button_rect
        
        # Back button
        self.draw_button(40, 620, 150, 40, "Back", "back")
    
    def draw_button(self, x, y, width, height, text, action=None, enabled=True):
        """Draw a button and return hover state - extended to support disabled state"""
        button_rect = pygame.Rect(x, y, width, height)
        hover = button_rect.collidepoint(pygame.mouse.get_pos()) and enabled
        
        # Draw button
        if not enabled:
            color = (100, 100, 100)  # Gray for disabled
        else:
            color = self.graphics.colors['button_hover'] if hover else self.graphics.colors['button']
            
        pygame.draw.rect(self.graphics.screen, color, button_rect, border_radius=3)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], button_rect, 1, border_radius=3)
        
        # Draw text
        text_color = (150, 150, 150) if not enabled else self.graphics.colors['button_text']
        text_surf = self.graphics.normal_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.graphics.screen.blit(text_surf, text_rect)
        
        # Store button for click detection if enabled
        if action and enabled:
            self.buttons[action] = button_rect
            
        return hover
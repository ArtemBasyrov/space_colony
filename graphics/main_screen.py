import pygame
from .screen import Screen
from .hex_map import HexMap
from .top_bar import TopBar
from .bottom_bar import BottomBar
from .building_menu import BuildingMenu
from .population_panel import PopulationPanel
from .economy_panel import EconomyPanel
from events import EventType, GameEvent

class MainScreen(Screen):
    def __init__(self, graphics):
        super().__init__(graphics)
        self.calculated_changes = {}
        
        # Create hex map with proper positioning
        self.hex_map = HexMap(20, 100, 800, 400, 35)
        self.hex_map.game = self.game  # Pass game reference to hex map
        self.hex_map.place_buildings(self.game.buildings)
        
        # Create UI components - pass self (the screen instance) instead of graphics
        self.top_bar = TopBar(graphics)
        self.bottom_bar = BottomBar(graphics)
        self.building_menu = BuildingMenu(self)
        self.population_panel = PopulationPanel(self)
        self.economy_panel = EconomyPanel(self)
        
        # Track if we've already handled a click in this frame
        self.click_handled = False
    
    def calculate_next_day_changes(self):
        """Calculate expected resource changes for the next day"""
        # Reset changes
        self.calculated_changes = {
            'oxygen': 0,
            'food': 0,
            'minerals': 0,
            'energy': 0,
            'credits': 0
        }
        
        pop = self.game.population
        res = self.game.resources
        
        # Calculate base consumption by population
        self.calculated_changes['oxygen'] -= pop.count * 0.1
        self.calculated_changes['food'] -= pop.count * 0.2
        self.calculated_changes['energy'] -= pop.count * 0.05
        
        # Calculate building production and consumption
        for building in self.game.buildings:
            production = building.calculate_production()
            consumption = building.calculate_consumption()
            
            for resource, amount in production.items():
                self.calculated_changes[resource] += amount
                
            for resource, amount in consumption.items():
                self.calculated_changes[resource] -= amount
        
        # Calculate wage cost
        wage_cost = pop.calculate_total_wages()
        self.calculated_changes['credits'] -= wage_cost

        # Calculate rent income (positive change to credits)
        rent_income = 0
        for colonist in pop.colonists:
            if colonist.housing and colonist.can_afford_rent():
                rent_income += colonist.rent_cost
        
        self.calculated_changes['credits'] += rent_income
    
    # main_screen.py - update the handle_event method
    def handle_event(self, event):
        """Handle mouse events for hex map and building menu"""
        # Reset click handled flag at the start of each event
        self.click_handled = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # First check building menu clicks (highest priority)
            menu_action = self.building_menu.handle_click(event.pos)
            if menu_action:
                self.on_button_click(menu_action)
                self.click_handled = True
                return
            
            # Then check bottom bar clicks
            bottom_bar_action = self.bottom_bar.handle_click(event.pos)
            if bottom_bar_action:
                self.on_button_click(bottom_bar_action)
                self.click_handled = True
                return
            
            # Finally check if click is on the map (only if not already handled)
            if not self.click_handled:
                map_rect = pygame.Rect(20, 100, 800, 400)
                if map_rect.collidepoint(event.pos):
                    hexagon = self.hex_map.handle_click(event.pos)
                    if hexagon and hexagon.building:
                        self.building_menu.show(hexagon.building)
                    else:
                        self.building_menu.hide()
                # If click is outside both map and building menu, close the menu
                elif not self.building_menu.rect.collidepoint(event.pos):
                    self.building_menu.hide()
        
        # NEW: Handle escape key to cancel construction
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.game.construction_mode:
                self.cancel_construction()

    def cancel_construction(self):
        """Cancel the current construction and refund money"""
        if self.game.construction_mode and self.game.pending_construction:
            building_type, price = self.game.pending_construction
            
            # Refund the money
            self.game.resources.credits += price
            
            # Reset construction state
            self.game.construction_mode = False
            self.game.selected_building_type = None
            self.game.pending_construction = None
            
            self.graphics.show_message(f"Construction cancelled. {price} credits refunded.")
    
    # In main_screen.py, modify the on_button_click method
    def on_button_click(self, action):
        """Handle button clicks in main screen"""
        pop = self.game.population
        
        if action == "next_day":
            self.game.next_day()
            self.calculate_next_day_changes()
            
        elif action == "market":
            self.graphics.set_screen('market')
            
        elif action == "wages":
            self.graphics.set_screen('wages')
            
        elif action == "construct":  # New action
            self.graphics.set_screen('construction')
            
        elif action == "save":
            self.graphics.show_message("Game saved!")
            
        elif action == "quit":
            pygame.quit()
            import sys
            sys.exit()
            
        # Handle building worker buttons - now using individual colonists
        elif action == "add_worker" and self.building_menu.selected_building:
            building = self.building_menu.selected_building
            if pop.available_workers > 0 and building.assigned_workers < building.max_workers:
                # Find an unemployed colonist
                unemployed = pop.unemployed_colonists
                if unemployed:
                    colonist = unemployed[0]
                    if building.assign_colonist(colonist):
                        self.graphics.show_message(f"Assigned {colonist.id} to {building.name}")
                        # Publish worker added event
                        self.game.event_manager.publish(GameEvent(
                            EventType.BUILDING_WORKER_ADDED,
                            f"Assigned colonist to {building.name}",
                            {"building": building.name, "workers": building.assigned_workers}
                        ))
                        self.calculate_next_day_changes()
                else:
                    self.graphics.show_message("No available workers!")
            else:
                self.graphics.show_message("No available workers or building at capacity!")
                
        elif action == "remove_worker" and self.building_menu.selected_building:
            building = self.building_menu.selected_building
            if building.assigned_colonists:
                colonist = building.assigned_colonists[0]
                if building.remove_colonist(colonist):
                    self.graphics.show_message(f"Removed {colonist.id} from {building.name}")
                    # Publish worker removed event
                    self.game.event_manager.publish(GameEvent(
                        EventType.BUILDING_WORKER_REMOVED,
                        f"Removed colonist from {building.name}",
                        {"building": building.name, "workers": building.assigned_workers}
                    ))
                    self.calculate_next_day_changes()
            else:
                self.graphics.show_message("No workers assigned to this building!")
                
        elif action == "close_building_menu":
            self.building_menu.hide()
    
    def draw(self):
        # Calculate resource changes for next day
        self.calculate_next_day_changes()
        
        # Background
        self.graphics.screen.fill(self.graphics.colors['background'])
        
        # Draw UI components
        self.top_bar.draw(self.game.resources, self.calculated_changes)
        
        # Title
        title_text = self.graphics.title_font.render(f"Space Colony - Day {self.game.day}", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (20, 60))
        
        # Draw hex map panel
        self.hex_map.draw(self.graphics.screen, self.all_colors, {
            'small': self.graphics.small_font,
            'normal': self.graphics.normal_font
        })
        
        # Draw side panels
        self.population_panel.draw(self.game.population)
        self.economy_panel.draw(self.game.population)
        
        # Draw building menu
        self.building_menu.draw()
        
        # Draw bottom bar
        self.bottom_bar.draw()
        
        # Display message if any
        if self.graphics.message and self.graphics.message_timer > 0:
            message_y = self.graphics.height - 90  # Position above bottom bar
            message_text = self.graphics.normal_font.render(self.graphics.message, True, self.graphics.colors['text'])
            message_rect = message_text.get_rect(center=(self.graphics.width // 2, message_y))
            pygame.draw.rect(self.graphics.screen, (30, 40, 60), message_rect.inflate(20, 10), border_radius=5)
            self.graphics.screen.blit(message_text, message_rect)
            self.graphics.message_timer -= 1
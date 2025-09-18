import pygame
import math
from .hexagon import Hexagon

class HexMap:
    def __init__(self, x, y, width, height, hex_size=35):  # Added x, y position parameters
        self.x = x  # Top-left x position of the map area
        self.y = y  # Top-left y position of the map area
        self.width = width
        self.height = height
        self.hex_size = hex_size
        self.hexagons = []
        self.selected_hex = None
        self.create_map()
    
    def create_map(self):
        """Create a grid of hexagons"""
        self.hexagons = []
        hex_width = self.hex_size * math.sqrt(3)
        hex_height = self.hex_size * 1.5
        
        # Calculate starting position to center the map in its area
        map_center_x = self.x + self.width / 2
        map_center_y = self.y + self.height / 2
        
        # Calculate how many rows and columns fit in the available space
        max_cols = int(self.width / hex_width) - 1
        max_rows = int(self.height / hex_height) - 1
        
        for row in range(max_rows):
            for col in range(max_cols):
                x = col * hex_width
                y = row * hex_height
                
                # Offset every other row
                if row % 2 == 1:
                    x += hex_width / 2
                
                # Center the map within its area
                total_map_width = (max_cols - 0.5) * hex_width
                total_map_height = max_rows * hex_height
                
                x += self.x + (self.width - total_map_width) / 2
                y += self.y + (self.height - total_map_height) / 2
                
                hexagon = Hexagon(x, y, self.hex_size, col, row)
                self.hexagons.append(hexagon)
    
    def get_hex_at_position(self, pos):
        """Get the hexagon at a given screen position"""
        for hexagon in self.hexagons:
            if hexagon.contains_point(pos):
                return hexagon
        return None
    
    def place_buildings(self, buildings):
        """Place initial buildings on the map"""
        # Clear existing buildings
        for hexagon in self.hexagons:
            hexagon.building = None
        
        # Place buildings in specific positions (centered)
        building_positions = [
            (3, 2),  # Mine
            (5, 2),  # Energy Generator
            (7, 2),  # Oxygen Generator
            (4, 4),  # Hydroponic Farm
            (6, 4),  # Hospital
            (4, 3),  # Habitat
        ]
        
        for i, (col, row) in enumerate(building_positions):
            if i < len(buildings):
                hexagon = self.get_hex_at_grid(col, row)
                if hexagon:
                    hexagon.place_building(buildings[i])
    
    def get_hex_at_grid(self, col, row):
        """Get hexagon at grid coordinates"""
        for hexagon in self.hexagons:
            if hexagon.map_x == col and hexagon.map_y == row:
                return hexagon
        return None
    
    # hex_map.py - update the draw method to show cancellation hint
    def draw(self, screen, colors, fonts):
        """Draw the entire hex map"""
        # Draw map background
        pygame.draw.rect(screen, colors['panel'], (self.x, self.y, self.width, self.height), border_radius=5)
        pygame.draw.rect(screen, colors['highlight'], (self.x, self.y, self.width, self.height), 2, border_radius=5)
        
        # Draw construction mode overlay if active
        if hasattr(self, 'game') and self.game.construction_mode:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 30))  # Green tint with low opacity
            screen.blit(overlay, (self.x, self.y))
            
            # Instruction text
            instruction_font = fonts['normal']
            instruction_text = instruction_font.render("Click on an empty hexagon to place building", True, (255, 255, 255))
            text_rect = instruction_text.get_rect(center=(self.x + self.width // 2, self.y + 20))
            pygame.draw.rect(screen, (0, 0, 0, 180), text_rect.inflate(20, 10), border_radius=5)
            screen.blit(instruction_text, text_rect)
            
            # Cancel instruction
            cancel_text = instruction_font.render("Press ESC to cancel construction", True, (255, 255, 255))
            cancel_rect = cancel_text.get_rect(center=(self.x + self.width // 2, self.y + 45))
            pygame.draw.rect(screen, (0, 0, 0, 180), cancel_rect.inflate(20, 10), border_radius=5)
            screen.blit(cancel_text, cancel_rect)
        
        # Draw all hexagons
        for hexagon in self.hexagons:
            selected = (hexagon == self.selected_hex)
            # Highlight empty hexagons in construction mode
            construction_highlight = (self.game.construction_mode and not hexagon.building) if hasattr(self, 'game') else False
            
            if construction_highlight:
                # Use a special color for available construction sites
                hexagon.draw(screen, colors, fonts, True)
                # Draw a green outline around available hexagons
                pygame.draw.polygon(screen, (0, 255, 0), hexagon.vertices, 3)
            else:
                hexagon.draw(screen, colors, fonts, selected)
    
    def handle_click(self, pos):
        """Handle mouse click on the map"""
        # Only handle clicks within the map area
        map_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if map_rect.collidepoint(pos):
            hexagon = self.get_hex_at_position(pos)
            
            # If in construction mode, place building instead of selecting
            if hasattr(self, 'game') and self.game.construction_mode and self.game.selected_building_type:
                if hexagon and not hexagon.building:
                    self.place_new_building(hexagon)
                    return None  # Don't return the hexagon for selection
                elif hexagon and hexagon.building:
                    self.game.graphics.show_message("This hexagon already has a building!")
                    return None
            
            self.selected_hex = hexagon
            return hexagon
        return None

    def place_new_building(self, hexagon):
        """Place a new building on the selected hexagon"""
        from buildings import create_building_from_name
        
        building = create_building_from_name(self.game.selected_building_type)
        if building:
            hexagon.place_building(building)
            self.game.buildings.append(building)
            
            # Clear construction state
            building_type = self.game.selected_building_type
            self.game.construction_mode = False
            self.game.selected_building_type = None
            self.game.pending_construction = None
            
            self.game.graphics.show_message(f"{building_type} constructed successfully!")
        else:
            self.game.graphics.show_message("Error: Could not create building!")
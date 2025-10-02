# hex_map.py - Updated with road drawing functionality
import pygame
import math
import random
from .hexagon import Hexagon

class HexMap:
    def __init__(self, x, y, width, height, hex_size=35):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hex_size = hex_size
        self.hexagons = []
        self.selected_hex = None
        self.area_of_effect_hexes = []  # New: store hexes for AoE visualization
        self.create_map()
    
    def create_map(self):
        """Create a grid of hexagons with varied surfaces and elevations"""
        self.hexagons = []
        hex_width = self.hex_size * math.sqrt(3)
        hex_height = self.hex_size * 1.5
        
        # Calculate how many rows and columns fit in the available space
        max_cols = int(self.width / hex_width) - 1
        max_rows = int(self.height / hex_height) - 1
        
        # Generate elevation map first
        elevation_map = self.generate_elevation_map(max_cols, max_rows)
        
        # Generate surface map based on elevation
        surface_map = self.generate_surface_map(max_cols, max_rows, elevation_map)
        
        # Ensure at least 3 ice hexes
        self.ensure_minimum_ice(surface_map, elevation_map, max_cols, max_rows, 3)
        
        # Ensure no completely inaccessible hexes
        self.ensure_accessibility(elevation_map, max_cols, max_rows)
        
        # Ensure at least 3 regolith hexes for initial mine placement
        self.ensure_minimum_regolith(surface_map, max_cols, max_rows, 3)
        
        # Calculate total map dimensions to center the grid
        total_map_width = (max_cols - 0.5) * hex_width
        total_map_height = (max_rows-2) * hex_height + self.hex_size * 2
        
        # Calculate offset to center the map within the panel
        offset_x = (self.width - total_map_width) / 2
        offset_y = (self.height - total_map_height) / 2 
        
        for row in range(max_rows):
            for col in range(max_cols):
                x = col * hex_width
                y = row * hex_height
                
                # Offset every other row
                if row % 2 == 1:
                    x += hex_width / 2
                
                # Position within the map area with centering
                x += self.x + offset_x
                y += self.y + offset_y
                
                # Get surface type and elevation from our generated maps
                surface_type = surface_map[row][col]
                elevation = elevation_map[row][col]
                
                hexagon = Hexagon(x, y, self.hex_size, col, row, surface_type, elevation)
                self.hexagons.append(hexagon)
    
    def ensure_minimum_regolith(self, surface_map, cols, rows, min_regolith):
        """Ensure there are at least min_regolith regolith hexes on the map"""
        regolith_count = sum(1 for row in surface_map for cell in row if cell == "regolith")
        
        if regolith_count < min_regolith:
            # Find cells that aren't already regolith
            non_regolith_cells = []
            for row in range(rows):
                for col in range(cols):
                    if surface_map[row][col] != "regolith":
                        non_regolith_cells.append((row, col))
            
            # Convert some to regolith
            needed = min_regolith - regolith_count
            if needed > 0 and non_regolith_cells:
                # Convert the needed number of cells
                for _ in range(min(needed, len(non_regolith_cells))):
                    row, col = random.choice(non_regolith_cells)
                    surface_map[row][col] = "regolith"
                    non_regolith_cells.remove((row, col))
    
    def generate_elevation_map(self, cols, rows):
        """Generate a map with more frequent elevation changes"""
        # Create multiple noise layers for more varied elevation
        noise_layers = []
        for i in range(3):  # Three layers of noise
            scale = 2 ** i  # Different scales for each layer
            noise_map = [[random.random() * scale for _ in range(cols)] for _ in range(rows)]
            noise_layers.append(noise_map)
        
        # Combine noise layers
        combined = [[0 for _ in range(cols)] for _ in range(rows)]
        for row in range(rows):
            for col in range(cols):
                total = 0
                for layer in noise_layers:
                    total += layer[row][col]
                combined[row][col] = total / len(noise_layers)
        
        # Normalize to 0-1 range
        min_val = min(min(row) for row in combined)
        max_val = max(max(row) for row in combined)
        normalized = [[(val - min_val) / (max_val - min_val) for val in row] for row in combined]
        
        # Convert to elevation levels (0, 1, 2) with more frequent changes
        elevation_map = [[0 for _ in range(cols)] for _ in range(rows)]
        for row in range(rows):
            for col in range(cols):
                if normalized[row][col] < 0.3:
                    elevation_map[row][col] = 0  # Low
                elif normalized[row][col] < 0.6:
                    elevation_map[row][col] = 1  # Medium
                else:
                    elevation_map[row][col] = 2  # High
        
        return elevation_map
    
    def generate_surface_map(self, cols, rows, elevation_map):
        """Generate surface map based on elevation"""
        surface_map = [["regolith" for _ in range(cols)] for _ in range(rows)]
        
        for row in range(rows):
            for col in range(cols):
                elevation = elevation_map[row][col]
                
                # Higher elevation is more likely to be stone
                if elevation == 2:  # High elevation
                    surface_map[row][col] = "stone"
                elif elevation == 0:  # Low elevation
                    if random.random() < 0.3:  # 30% chance for ice at low elevation
                        surface_map[row][col] = "ice"
                elif elevation == 1:  # Medium elevation
                    if random.random() < 0.6:  # 60% chance for stone at medium elevation
                        surface_map[row][col] = "stone"
        
        return surface_map
    
    def ensure_minimum_ice(self, surface_map, elevation_map, cols, rows, min_ice):
        """Ensure there are at least min_ice ice hexes on the map"""
        ice_count = sum(1 for row in surface_map for cell in row if cell == "ice")
        
        if ice_count < min_ice:
            # Find low elevation cells that aren't already ice
            low_elevation_cells = []
            for row in range(rows):
                for col in range(cols):
                    if elevation_map[row][col] == 0 and surface_map[row][col] != "ice":
                        low_elevation_cells.append((row, col))
            
            # Convert some to ice
            needed = min_ice - ice_count
            if needed > 0 and low_elevation_cells:
                # Convert the needed number of cells
                for _ in range(min(needed, len(low_elevation_cells))):
                    row, col = random.choice(low_elevation_cells)
                    surface_map[row][col] = "ice"
                    low_elevation_cells.remove((row, col))
    
    def ensure_accessibility(self, elevation_map, cols, rows):
        """Ensure no hexes are completely inaccessible"""
        directions = [
            (0, -1), (1, 0), (0, 1), 
            (-1, 1), (-1, 0), (-1, -1),
        ]
        
        # Check each hex and fix if completely inaccessible
        for row in range(rows):
            for col in range(cols):
                current_elevation = elevation_map[row][col]
                inaccessible_count = 0
                
                # Count inaccessible neighbors
                for dx, dy in directions:
                    n_row, n_col = row + dy, col + dx
                    if 0 <= n_row < rows and 0 <= n_col < cols:
                        neighbor_elevation = elevation_map[n_row][n_col]
                        if abs(current_elevation - neighbor_elevation) >= 2:
                            inaccessible_count += 1
                    else:
                        inaccessible_count += 1  # Edge of map is inaccessible
                
                # If all sides are inaccessible, adjust elevation
                if inaccessible_count >= 6:
                    # Find the most common elevation among neighbors
                    neighbor_elevations = []
                    for dx, dy in directions:
                        n_row, n_col = row + dy, col + dx
                        if 0 <= n_row < rows and 0 <= n_col < cols:
                            neighbor_elevations.append(elevation_map[n_row][n_col])
                    
                    if neighbor_elevations:
                        # Set to the most common neighbor elevation
                        most_common = max(set(neighbor_elevations), key=neighbor_elevations.count)
                        elevation_map[row][col] = most_common
                    else:
                        # If no neighbors (shouldn't happen), set to medium elevation
                        elevation_map[row][col] = 1
    
    def get_hex_at_position(self, pos):
        """Get the hexagon at a given screen position"""
        for hexagon in self.hexagons:
            if hexagon.contains_point(pos):
                return hexagon
        return None
    
    def hex_distance(self, pos1, pos2):
        """Proper hex grid distance calculation using axial coordinates"""
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Convert to axial coordinates
        z1 = -x1 - y1
        z2 = -x2 - y2
        
        return (abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)) // 2
    
    def is_hex_accessible(self, from_hex, to_hex):
        """Check if a hex is accessible considering elevation differences"""
        if not from_hex or not to_hex:
            return False
        elevation_diff = abs(from_hex.elevation - to_hex.elevation)
        return elevation_diff < 2  # Accessible if elevation difference is 0 or 1

    def get_area_of_effect_hexes(self, center_pos, radius):
        """Get all hexes within radius of center position, considering accessibility"""
        center_hex = self.get_hex_at_grid(center_pos[0], center_pos[1])
        if not center_hex:
            return []
        
        visited = set()
        queue = [(center_hex, 0)]  # (hex, distance)
        affected_hexes = []
        
        while queue:
            current_hex, distance = queue.pop(0)
            
            if current_hex in visited:
                continue
                
            visited.add(current_hex)
            affected_hexes.append(current_hex)
            
            # If we haven't reached max distance, explore neighbors
            if distance < radius:
                # Get all neighbor positions
                neighbor_positions = self.get_neighbor_positions(current_hex.map_x, current_hex.map_y)
                
                for pos in neighbor_positions:
                    neighbor_hex = self.get_hex_at_grid(pos[0], pos[1])
                    if neighbor_hex and neighbor_hex not in visited:
                        # Check if this neighbor is accessible from current hex
                        if self.is_hex_accessible(current_hex, neighbor_hex):
                            queue.append((neighbor_hex, distance + 1))
        
        return affected_hexes
    
    def get_neighbor_positions(self, x, y):
        """Get neighboring hex positions"""
        directions = [
            (0, -1), (1, 0), (0, 1), 
            (-1, 1), (-1, 0), (-1, -1),
        ]
        
        neighbors = []
        for dx, dy in directions:
            neighbor_x = x + dx
            neighbor_y = y + dy
            
            # Adjust for odd/even rows
            if y % 2 == 1:  # odd row
                if dy == 1 or dy == -1:
                    neighbor_x = x + dx + 1
            
            neighbors.append((neighbor_x, neighbor_y))
            
        return neighbors

    def get_neighbor_buildings(self, hexagon):
        """Get neighboring buildings for a hexagon"""
        neighbor_buildings = []
        neighbor_positions = self.get_neighbor_positions(hexagon.map_x, hexagon.map_y)
        
        for pos in neighbor_positions:
            neighbor_hex = self.get_hex_at_grid(pos[0], pos[1])
            if neighbor_hex and neighbor_hex.building:
                if self.is_hex_accessible(hexagon, neighbor_hex):
                    neighbor_buildings.append(neighbor_hex.building)
                
        return neighbor_buildings
    
    def get_all_building_neighbors(self):
        """Get all building neighbors mapping for crime spreading"""
        building_neighbors = {}
        
        for hexagon in self.hexagons:
            if hexagon.building:
                neighbors = self.get_neighbor_buildings(hexagon)
                building_neighbors[hexagon.building] = neighbors
                
        return building_neighbors

    def get_neighbor_elevations(self, hexagon):
        """Get elevations of all neighbors for a hexagon - UPDATED to use get_neighbor_positions"""
        neighbor_elevations = []
        neighbor_positions = self.get_neighbor_positions(hexagon.map_x, hexagon.map_y)
        
        for pos in neighbor_positions:
            neighbor_hex = self.get_hex_at_grid(pos[0], pos[1])
            if neighbor_hex:
                neighbor_elevations.append(neighbor_hex.elevation)
            else:
                neighbor_elevations.append(None)
                
        return neighbor_elevations

    def place_buildings(self, buildings):
        """Place initial buildings on the map"""
        # Clear existing buildings
        for hexagon in self.hexagons:
            hexagon.building = None
        
        # Track occupied hexes to avoid duplicates
        occupied_hexes = set()
        
        # Find all regolith hexes for mine placement
        regolith_hexes = [hex for hex in self.hexagons if hex.surface_type == "regolith"]
        
        # Place buildings in specific positions, ensuring mine is on regolith
        building_positions = [
            (3, 2, "Mine"),          # Mine - must be on regolith
            (5, 2, "EnergyGenerator"),  # Energy Generator
            (7, 2, "OxygenGenerator"),  # Oxygen Generator
            (4, 4, "HydroponicFarm"),   # Hydroponic Farm
            (6, 4, "Hospital"),         # Hospital
            (4, 3, "HabitatBlock"),     # Habitat
        ]
        
        for i, (col, row, building_type) in enumerate(building_positions):
            if i < len(buildings):
                # For mine, find a regolith hex near the target position
                if building_type == "Mine" and regolith_hexes:
                    # Find the closest regolith hex to the target position that's not occupied
                    target_x, target_y = col, row
                    available_regolith_hexes = [
                        hex for hex in regolith_hexes 
                        if (hex.map_x, hex.map_y) not in occupied_hexes
                    ]
                    
                    if available_regolith_hexes:
                        closest_hex = min(available_regolith_hexes, key=lambda h: 
                                        abs(h.map_x - target_x) + abs(h.map_y - target_y))
                        closest_hex.place_building(buildings[i])
                        occupied_hexes.add((closest_hex.map_x, closest_hex.map_y))
                        regolith_hexes.remove(closest_hex)  # Remove from available regolith hexes
                    else:
                        # Fallback: use the specified position if no regolith hexes available
                        hexagon = self.get_hex_at_grid(col, row)
                        if hexagon and (col, row) not in occupied_hexes:
                            hexagon.place_building(buildings[i])
                            occupied_hexes.add((col, row))
                else:
                    # For other buildings, use the specified position if not occupied
                    hexagon = self.get_hex_at_grid(col, row)
                    if hexagon and (col, row) not in occupied_hexes:
                        hexagon.place_building(buildings[i])
                        occupied_hexes.add((col, row))
                    else:
                        # If the target position is occupied, find the nearest available hex
                        available_hexes = [
                            hex for hex in self.hexagons 
                            if (hex.map_x, hex.map_y) not in occupied_hexes
                        ]
                        if available_hexes:
                            # Find the closest available hex to the target position
                            closest_hex = min(available_hexes, key=lambda h: 
                                            abs(h.map_x - col) + abs(h.map_y - row))
                            closest_hex.place_building(buildings[i])
                            occupied_hexes.add((closest_hex.map_x, closest_hex.map_y))
    
    def get_hex_at_grid(self, col, row):
        """Get hexagon at grid coordinates"""
        for hexagon in self.hexagons:
            if hexagon.map_x == col and hexagon.map_y == row:
                return hexagon
        return None
    
    # hex_map.py - update the draw method and handle_click method
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
            
            # Get building info for placement requirements
            building_type = self.game.selected_building_type
            required_surface = None
            if building_type:
                from buildings import get_building_required_surface
                required_surface = get_building_required_surface(building_type)
            
            if required_surface:
                instruction_text = instruction_font.render(f"Click on a {required_surface} hexagon to place building. Press ESC to cancel construction", True, (255, 255, 255))
            elif self.game.selected_building_type == "REMOVAL":
                instruction_text = instruction_font.render("Click on a hexagon with a building to remove it. Press ESC to cancel removal", True, (255, 255, 255))
            else:
                instruction_text = instruction_font.render("Click on an empty hexagon to place building. Press ESC to cancel construction", True, (255, 255, 255))
                
            text_rect = instruction_text.get_rect(center=(self.x + self.width // 2, self.y+self.height - 20))
            pygame.draw.rect(screen, (0, 0, 0, 180), text_rect.inflate(20, 10), border_radius=5)
            screen.blit(instruction_text, text_rect)
            
        
        # Draw all hexagons with their neighbor elevations
        for hexagon in self.hexagons:
            selected = (hexagon == self.selected_hex)
            neighbor_elevations = self.get_neighbor_elevations(hexagon)

            # Highlight empty hexagons in construction mode
            construction_highlight = False
            construction_valid = False
            
            if hasattr(self, 'game') and self.game.construction_mode and not hexagon.building:
                construction_highlight = True
                
                # Check if this hexagon is valid for the selected building
                building_type = self.game.selected_building_type
                if building_type:
                    from buildings import get_building_required_surface
                    required_surface = get_building_required_surface(building_type)
                    
                    if required_surface:
                        # Building has surface requirement
                        construction_valid = (hexagon.surface_type == required_surface)
                    else:
                        # No surface requirement - always valid
                        construction_valid = True
            
            if construction_highlight:
                if construction_valid:
                    # Valid construction site - use normal highlighting
                    hexagon.draw(screen, colors, fonts, True, neighbor_elevations)
                    # Draw a green outline around available hexagons
                    pygame.draw.polygon(screen, (0, 255, 0), hexagon.vertices, 3)
                else:
                    # Invalid construction site - draw with red tint
                    hexagon.draw(screen, colors, fonts, False, neighbor_elevations)
                    # Draw a red outline
                    pygame.draw.polygon(screen, (255, 0, 0), hexagon.vertices, 3)
            else:
                hexagon.draw(screen, colors, fonts, selected, neighbor_elevations)
        
        # Draw area of effect highlights if a building with AoE is selected
        if (self.selected_hex and self.selected_hex.building and 
            hasattr(self.selected_hex.building, 'area_of_effect_radius') and 
            self.selected_hex.building.area_of_effect_radius > 0):
            
            self.draw_area_of_effect(screen, self.selected_hex.building)
    
    def draw_area_of_effect(self, screen, building):
        """Draw the area of effect for a building using hexagon's drawing method"""
        if not building.hex_position:
            return
            
        center_x, center_y = building.hex_position
        center_hex = self.get_hex_at_grid(center_x, center_y)
        if not center_hex:
            return
            
        # Get all hexes in area of effect using hex_map's method
        affected_hexes = building.get_area_of_effect_hexes(self)
        
        # Choose color based on building type
        if hasattr(building, "crime_reduction_per_worker"):
            base_color = (0, 100, 255)  # Blue for police
        else:
            base_color = (100, 255, 100)  # Green for others
        
        # Draw highlights on all affected hexes
        for hexagon in affected_hexes:
            # Use hex_map's distance calculation
            distance = self.hex_distance(building.hex_position, (hexagon.map_x, hexagon.map_y))
            
            # Calculate alpha based on distance
            max_alpha = 80
            alpha = max_alpha * (1 - (distance / building.area_of_effect_radius))
            alpha = max(20, alpha)
            
            # Use hexagon's built-in method to draw the highlight
            hexagon.draw_area_of_effect_highlight(screen, base_color, int(alpha))
        
        # Highlight the center building
        center_hex.draw_area_of_effect_highlight(screen, (255, 255, 0), 100)
        
        # Draw info text
        self.draw_area_of_effect_info(screen, building)

    def draw_area_of_effect_info(self, screen, building):
        """Draw information about the area of effect"""
        if hasattr(building, "crime_reduction_per_worker"):
            effect_text = f"Police Coverage: {building.assigned_workers}/{building.max_workers} workers"
            crime_reduction = building.calculate_crime_reduction()
            if crime_reduction > 0:
                effect_text += f" (-{crime_reduction} crime)"
        else:
            effect_text = f"Area of Effect: {building.area_of_effect_radius} hexes"
            
        text_surface = self.game.graphics.small_font.render(effect_text, True, self.game.graphics.colors['text'])
        text_bg = pygame.Surface((text_surface.get_width() + 10, text_surface.get_height() + 5), pygame.SRCALPHA)
        text_bg.fill((0, 0, 0, 180))
        screen.blit(text_bg, (self.x + 10, self.y + 10))
        screen.blit(text_surface, (self.x + 15, self.y + 12))

    # hex_map.py - updated handle_click method
    def handle_click(self, pos):
        """Handle mouse click on the map"""
        # Only handle clicks within the map area
        map_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if map_rect.collidepoint(pos):
            hexagon = self.get_hex_at_position(pos)
            
            # If in removal mode, remove building instead of selecting
            if hasattr(self, 'game') and self.game.construction_mode and self.game.selected_building_type == "REMOVAL":
                if hexagon and hexagon.building:
                    self.remove_building(hexagon)
                    return None
                elif hexagon and not hexagon.building:
                    self.game.graphics.show_message("No building to remove on this hexagon!")
                    return None
            
            # If in construction mode, place building instead of selecting
            elif hasattr(self, 'game') and self.game.construction_mode and self.game.selected_building_type:
                if hexagon and not hexagon.building:
                    # Check if the hexagon is valid for the selected building type
                    building_type = self.game.selected_building_type
                    from buildings import get_building_required_surface, get_building_name
                    required_surface = get_building_required_surface(building_type)
                    
                    if required_surface and hexagon.surface_type != required_surface:
                        self.game.graphics.show_message(f"{get_building_name(building_type)} can only be built on {required_surface} surfaces!")
                        return None
                    
                    # Check if the hexagon is accessible
                    neighbor_elevations = self.get_neighbor_elevations(hexagon)
                    accessible_sides = hexagon.get_accessible_sides(neighbor_elevations)
                    
                    if any(accessible_sides):  # At least one side is accessible
                        self.place_new_building(hexagon)
                    else:
                        self.game.graphics.show_message("This location is not accessible!")
                    return None
                elif hexagon and hexagon.building:
                    self.game.graphics.show_message("This hexagon already has a building!")
                    return None
            
            self.selected_hex = hexagon
            return hexagon
        return None

    def remove_building(self, hexagon):
        """Remove a building from the selected hexagon"""
        removal_cost = 200
        
        if self.game.resources.credits >= removal_cost:
            building = hexagon.building
            
            # Handle colonists in residential buildings
            if hasattr(building, 'residents') and building.residents:
                # Remove all residents from the habitat
                for colonist in building.residents[:]:  # Use slice copy to avoid modification during iteration
                    building.remove_resident(colonist)
            
            # Handle workers in production buildings
            if hasattr(building, 'assigned_colonists') and building.assigned_colonists:
                # Unassign all workers from the building
                for colonist in building.assigned_colonists[:]:  # Use slice copy
                    building.remove_colonist(colonist)
            
            # Remove building from game buildings list
            if building in self.game.buildings:
                self.game.buildings.remove(building)
            
            # Remove building from hexagon
            hexagon.remove_building()
            
            # Deduct removal cost
            self.game.resources.credits -= removal_cost
            
            # Clear removal mode
            self.game.construction_mode = False
            self.game.selected_building_type = None
            
            self.game.graphics.show_message(f"Building removed successfully! {removal_cost} credits deducted.")
        else:
            self.game.graphics.show_message(f"Not enough credits! Building removal costs {removal_cost} credits.")

    def place_new_building(self, hexagon):
        """Place a new building on the selected hexagon"""
        from buildings import create_building_from_name, get_building_name
        
        building = create_building_from_name(self.game.selected_building_type)
        if building:
            hexagon.place_building(building)
            self.game.buildings.append(building)
            
            # Clear construction state
            building_type = self.game.selected_building_type
            self.game.construction_mode = False
            self.game.selected_building_type = None
            self.game.pending_construction = None
            
            self.game.graphics.show_message(f"{get_building_name(building_type)} constructed successfully!")
        else:
            self.game.graphics.show_message("Error: Could not create building!")

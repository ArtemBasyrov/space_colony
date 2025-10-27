# hexagon.py
import pygame
import math

import sys
import os

def resource_path(relative_path):
    """ Get the absolute path to a resource """
    try:
        # PyInstaller and cx_Freeze use different methods
        # For cx_Freeze, the assets are in the same directory as the executable
        if hasattr(sys, 'frozen'):
            # Running as compiled executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(__file__)
        
        full_path = os.path.join(base_path, relative_path)
        
        return full_path
    except Exception as e:
        print(f"Error in resource_path: {e}")
        return relative_path  # Fallback to relative path

class Hexagon:
    def __init__(self, x, y, size, map_x, map_y, surface_type="regolith", elevation=0):
        self.x = x  # Screen x position (center of hexagon)
        self.y = y  # Screen y position (center of hexagon)
        self.size = size  # Size (radius from center to vertex)
        self.map_x = map_x  # Grid x coordinate
        self.map_y = map_y  # Grid y coordinate
        self.surface_type = surface_type  # "regolith", "stone", or "ice"
        self.elevation = elevation  # 0, 1, or 2 (low, medium, high)
        self.building = None  # Building placed on this hex
        
        # Define surface colors
        self.surface_colors = {
            "regolith": (180, 160, 140),  # Sandy brown
            "stone": (120, 120, 120),     # Gray
            "ice": (200, 220, 240)        # Light blue
        }
        
        # Define elevation offsets for visual representation
        self.elevation_offsets = {
            0: 0,
            1: -5,  # More raised for better visibility
            2: -10  # Even more raised for high elevation
        }

        self.vertices = self.calculate_vertices()
        self.rect = self.calculate_bounding_rect()

        # Texture support
        self.textures_loaded = False
        self.texture_surfaces = {}
        self.texture_rects = {}
        
        # Load textures
        self.load_textures()
        
    def load_textures(self):
        """Load textures for different surface types"""
        texture_paths = {
            "regolith": "assets/textures/regolithtexture.png",
            "stone": "assets/textures/stonetexture.png", 
            "ice": "assets/textures/icetexture.png"
        }
        
        for surface_type, path in texture_paths.items():
            try:
                # Use the resource_path function to handle different environments
                full_path = path
                texture = pygame.image.load(full_path).convert_alpha()
                
                # Scale texture to appropriate size for hexagon
                texture_size = self.size * 4  # Make texture larger than hex for better tiling
                self.texture_surfaces[surface_type] = pygame.transform.scale(
                    texture, (texture_size, texture_size)
                )
                self.texture_rects[surface_type] = self.texture_surfaces[surface_type].get_rect()
                
            except (pygame.error, FileNotFoundError):
                #print(f"Warning: Could not load texture {path}")
                # Fall back to solid colors if textures can't be loaded
                self.texture_surfaces[surface_type] = None
        
        self.textures_loaded = True

    def calculate_vertices(self):
        """Calculate the six vertices of the hexagon"""
        vertices = []
        elevation_offset = self.elevation_offsets[self.elevation]
        for i in range(6):
            angle_deg = 60 * i - 30  # Start at -30 degrees for flat-top hex
            angle_rad = math.pi / 180 * angle_deg
            vertex_x = self.x + self.size * math.cos(angle_rad)
            vertex_y = self.y + self.size * math.sin(angle_rad) + elevation_offset
            vertices.append((vertex_x, vertex_y))
        return vertices
    
    def calculate_bounding_rect(self):
        """Calculate the bounding rectangle for the hexagon"""
        min_x = min(v[0] for v in self.vertices)
        max_x = max(v[0] for v in self.vertices)
        min_y = min(v[1] for v in self.vertices)
        max_y = max(v[1] for v in self.vertices)
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    
    def contains_point(self, point):
        """Check if a point is inside the hexagon using ray casting algorithm"""
        x, y = point
        num_vertices = len(self.vertices)
        inside = False
        p1x, p1y = self.vertices[0]
        for i in range(num_vertices + 1):
            p2x, p2y = self.vertices[i % num_vertices]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def get_accessible_sides(self, neighbor_elevations):
        """Determine which sides are accessible based on elevation differences"""
        accessible = [True] * 6  # Start with all sides accessible
        
        for i, neighbor_elev in enumerate(neighbor_elevations):
            if neighbor_elev is not None:  # There is a neighbor
                elevation_diff = abs(self.elevation - neighbor_elev)
                if elevation_diff >= 2:  # Two or more levels difference - cannot be crossed
                    accessible[i] = False
                # If elevation difference is 1 or 0, it's accessible (no need to change)
                    
        return accessible
    
    def can_place_building(self, building):
        """Check if a building can be placed on this hexagon based on surface type"""
        if self.building is not None:
            return False  # Already has a building
        
        return building.can_be_placed_on(self)
    
    def place_building(self, building):
        """Place a building on this hexagon if valid"""
        if self.can_place_building(building):
            self.building = building
            # Set the building's hex position for area of effect calculations
            building.set_hex_position(self.map_x, self.map_y)
            return True
        return False
    
    def remove_building(self):
        """Remove building from this hexagon"""
        self.building = None
        
    def draw(self, screen, colors, fonts, selected=False, neighbor_elevations=None):
        """Draw the hexagon on the screen"""
        # Determine accessible sides
        if neighbor_elevations is None:
            accessible = [True] * 6
        else:
            accessible = self.get_accessible_sides(neighbor_elevations)

        # Draw hexagon with texture or fallback color
        if self.texture_surfaces.get(self.surface_type):
            # Create a mask for the hexagon shape
            mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.polygon(mask, (255, 255, 255, 255), [
                (v[0] - self.rect.x, v[1] - self.rect.y) for v in self.vertices
            ])
            
            # Create textured surface
            textured_hex = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
            # Tile the texture across the hexagon
            texture = self.texture_surfaces[self.surface_type]
            texture_rect = texture.get_rect()
            
            # Calculate tiling
            for x in range(0, self.rect.width, texture_rect.width):
                for y in range(0, self.rect.height, texture_rect.height):
                    textured_hex.blit(texture, (x, y))
            
            # Apply the hexagon mask
            textured_hex.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw the textured hexagon
            screen.blit(textured_hex, self.rect.topleft)
        else:
            # Fallback to solid color if texture not available
            base_color = self.surface_colors[self.surface_type]
            pygame.draw.polygon(screen, base_color, self.vertices)

        # Draw cliff visualization for elevated hexagons
        if self.elevation > 0:
            self.draw_vertical_cliff_lines(screen, colors)

        # Draw elevation indicator (darker lines on lower edges)
        if self.elevation > 0:
            for i in range(6):
                start_i = (i-1) % 6
                next_i = (start_i + 1) % 6
                if not accessible[i]:  # Draw inaccessible sides with a different color
                    pygame.draw.line(screen, (100, 0, 0),  # Red for inaccessible
                                    self.vertices[start_i], self.vertices[next_i], 4)
                else:
                    # Different line color based on elevation
                    line_color = (60, 60, 60) if self.elevation == 1 else (40, 40, 40)
                    pygame.draw.line(screen, line_color, 
                                    self.vertices[start_i], self.vertices[next_i], 3)
        
        # Draw elevation indicator in the center
        if self.elevation > 0:
            elevation_color = (100, 100, 100) if self.elevation == 1 else (70, 70, 70)
            pygame.draw.circle(screen, elevation_color, (self.x+20, self.y+5), 5)
            
            # Draw elevation number
            elev_text = fonts['small'].render(str(self.elevation), True, colors['text'])
            elev_rect = elev_text.get_rect(center=(self.x+20, self.y+5))
            screen.blit(elev_text, elev_rect)
        
        # Draw hex border
        border_color = colors['hex_selected'] if selected else colors['hex_border']
        pygame.draw.polygon(screen, border_color, self.vertices, 2)
        
        # Draw building info if present
        if self.building:
            # Draw building name
            name_text = fonts['small'].render(self.building.name, True, colors['text'])
            name_rect = name_text.get_rect(center=(self.x, self.y - 15))
            screen.blit(name_text, name_rect)
            
            # Draw worker count
            if hasattr(self.building, 'capacity'):
                capacity_text = fonts['small'].render(f"{len(self.building.residents)}/{self.building.capacity}", True, colors['text'])
                capacity_rect = capacity_text.get_rect(center=(self.x, self.y + 15))
                screen.blit(capacity_text, capacity_rect)
            elif hasattr(self.building, 'assigned_workers') and hasattr(self.building, 'max_workers'):
                workers_text = fonts['small'].render(f"{self.building.assigned_workers}/{self.building.max_workers}", True, colors['text'])
                workers_rect = workers_text.get_rect(center=(self.x, self.y + 15))
                screen.blit(workers_text, workers_rect)
            
            # Draw small indicator for building type
            if hasattr(self.building, 'production_rate'):
                indicator_color = colors['success']
            else:
                indicator_color = colors['warning']
            pygame.draw.circle(screen, indicator_color, (self.x, self.y), 5)

    def draw_area_of_effect_highlight(self, screen, color, alpha):
        """Draw an area of effect highlight on this hexagon"""
        highlight_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw the highlight polygon
        vertices_local = [
            (v[0] - self.rect.x, v[1] - self.rect.y) 
            for v in self.vertices
        ]
        pygame.draw.polygon(highlight_surface, (*color, alpha), vertices_local)
        
        # Apply to screen
        screen.blit(highlight_surface, self.rect.topleft)
        
        # Draw border
        border_color = (*color, min(255, alpha + 100))
        pygame.draw.polygon(screen, border_color, self.vertices, 2)

    def draw_vertical_cliff_lines(self, screen, colors):
        # Draw vertical lines to represent cliffs in the bottom area
        cliff_color = colors['highlight']
        num_cliff_lines = 8  # Increased number of lines for better visualization
        
        # Calculate the horizontal range for the bottom part of the hexagon
        left_x = min(v[0] for v in self.vertices)
        right_x = max(v[0] for v in self.vertices)
        width = right_x - left_x
        
        # Draw vertical lines in the bottom area
        for i in range(num_cliff_lines+1):
            # Distribute lines evenly across the bottom width
            line_x = left_x + i * (width / (num_cliff_lines))
            
            # Find the bottom edge y-coordinate at this x position
            current_bottom_y = None
            
            # Check which bottom edge segment this x falls on
            # Bottom edge is between vertices 1-2 and 2-3 in a flat-top hexagon
            for j in range(1, 4):  # Check segments 1-2, 2-3
                v1 = self.vertices[j]
                v2 = self.vertices[(j + 1) % 6]
                
                # Check if line_x is between these vertices horizontally
                if min(v1[0], v2[0]) <= line_x <= max(v1[0], v2[0]):
                    # Calculate y at line_x using linear interpolation
                    if v2[0] - v1[0] != 0:  # Avoid division by zero
                        t = (line_x - v1[0]) / (v2[0] - v1[0])
                        current_bottom_y = v1[1] + t * (v2[1] - v1[1])
                        break
            
            # If we found a bottom edge point, draw the cliff line
            if current_bottom_y is not None:
                # Calculate the zero elevation y at the same x position
                # For a zero elevation hexagon, the center y would be self.y (no elevation offset)
                zero_center_y = self.y  # No elevation offset
                
                # Calculate bottom vertices for zero elevation
                zero_vertices = []
                for k in range(6):
                    angle_deg = 60 * k - 30
                    angle_rad = math.pi / 180 * angle_deg
                    vertex_x = self.x + self.size * math.cos(angle_rad)
                    vertex_y = zero_center_y + self.size * math.sin(angle_rad)  # No elevation offset
                    zero_vertices.append((vertex_x, vertex_y))
                
                # Find the zero elevation bottom y at the same x position
                zero_bottom_y = None
                for j in range(1, 4):  # Check bottom segments 1-2, 2-3
                    v1 = zero_vertices[j]
                    v2 = zero_vertices[(j + 1) % 6]
                    
                    if min(v1[0], v2[0]) <= line_x <= max(v1[0], v2[0]):
                        if v2[0] - v1[0] != 0:
                            t = (line_x - v1[0]) / (v2[0] - v1[0])
                            zero_bottom_y = v1[1] + t * (v2[1] - v1[1])
                            break
                
                # Draw the vertical cliff line from elevated bottom to zero elevation bottom
                if zero_bottom_y is not None and current_bottom_y < zero_bottom_y:
                    # Start slightly inside the elevated hexagon
                    start_y = current_bottom_y 
                    end_y = zero_bottom_y
                    
                    # Draw the vertical cliff line
                    pygame.draw.line(screen, cliff_color, (line_x, start_y), (line_x, end_y), 1)
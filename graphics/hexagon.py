import pygame
import math

class Hexagon:
    def __init__(self, x, y, size, map_x, map_y):
        self.x = x  # Screen x position (center of hexagon)
        self.y = y  # Screen y position (center of hexagon)
        self.size = size  # Size (radius from center to vertex)
        self.map_x = map_x  # Grid x coordinate
        self.map_y = map_y  # Grid y coordinate
        self.building = None  # Building placed on this hex
        self.vertices = self.calculate_vertices()
        self.rect = self.calculate_bounding_rect()
        
    def calculate_vertices(self):
        """Calculate the six vertices of the hexagon"""
        vertices = []
        for i in range(6):
            angle_deg = 60 * i - 30  # Start at -30 degrees for flat-top hex
            angle_rad = math.pi / 180 * angle_deg
            vertex_x = self.x + self.size * math.cos(angle_rad)
            vertex_y = self.y + self.size * math.sin(angle_rad)
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
    
    def draw(self, screen, colors, fonts, selected=False):
        """Draw the hexagon on the screen"""
        # Draw hexagon background
        color = colors['hex_selected'] if selected else colors['hex_default']
        pygame.draw.polygon(screen, color, self.vertices)
        pygame.draw.polygon(screen, colors['hex_border'], self.vertices, 2)
        
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
    
    def place_building(self, building):
        """Place a building on this hexagon"""
        self.building = building
    
    def remove_building(self):
        """Remove building from this hexagon"""
        self.building = None
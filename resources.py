import pygame

class ResourceManager:
    def __init__(self):
        self.oxygen = 100
        self.food = 100
        self.regolith = 50  # Changed from minerals to regolith
        self.energy = 75
        self.credits = 1000
        self.hydrogen = 0  # New resource
        self.fuel = 25     # New resource
        
        self.images = {}
        self.fonts = {}

    def apply_production(self, production_dict, consumption_dict):
        # Apply production
        for resource, amount in production_dict.items():
            if hasattr(self, resource):
                current = getattr(self, resource)
                setattr(self, resource, current + amount)
        
        # Apply consumption
        for resource, amount in consumption_dict.items():
            if hasattr(self, resource):
                current = getattr(self, resource)
                setattr(self, resource, max(0, current - amount))

    def update(self, population, buildings):
        # Calculate total production and consumption from all buildings
        total_production = {
            'oxygen': 0, 'food': 0, 'regolith': 0, 'energy': 0, 
            'credits': 0, 'hydrogen': 0, 'fuel': 0
        }
        total_consumption = {
            'oxygen': 0, 'food': 0, 'regolith': 0, 'energy': 0, 
            'credits': 0, 'hydrogen': 0, 'fuel': 0
        }
        
        # Base consumption by population - now based on individual colonists
        total_consumption['oxygen'] += population.count * 0.1
        total_consumption['food'] += population.count * 0.2
        total_consumption['energy'] += population.count * 0.05
        
        # Calculate building production and consumption
        for building in buildings:
            production = building.calculate_effective_production(self)  # Use the new method
            consumption = building.calculate_consumption()
            
            for resource, amount in production.items():
                total_production[resource] += amount
                    
            for resource, amount in consumption.items():
                total_consumption[resource] += amount
        
        # Calculate rent income from all colonists
        rent_income = 0
        for colonist in population.colonists:
            if colonist.housing and colonist.can_afford_rent():
                rent_income += colonist.rent_cost
        
        # Add rent income to credits
        total_production['credits'] += rent_income
        
        # Apply the net effect
        self.apply_production(total_production, total_consumption)

    def get_resource(self, resource_name):
        return getattr(self, resource_name, 0)
        
    def set_resource(self, resource_name, value):
        if hasattr(self, resource_name):
            setattr(self, resource_name, value)

    def load_image(self, key, path, scale=None):
        """Load and optionally scale an image"""
        try:
            image = pygame.image.load(path)
            if image.get_alpha():
                image = image.convert_alpha()
            else:
                image = image.convert()
                
            if scale:
                image = pygame.transform.scale(image, scale)
                
            self.images[key] = image
            return image
        except pygame.error:
            print(f"Error loading image: {path}")
            return self.create_placeholder(scale or (32, 32))
    
    def create_placeholder(self, size):
        """Create a placeholder image for missing assets"""
        placeholder = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (255, 0, 255), (0, 0, size[0], size[1]), 2)
        font = pygame.font.SysFont('Arial', min(size)//4)
        text = font.render("X", True, (255, 255, 255))
        text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
        placeholder.blit(text, text_rect)
        return placeholder
    
    def get_image(self, key):
        """Retrieve a loaded image"""
        return self.images.get(key, self.create_placeholder((32, 32)))
    
    def load_font(self, key, path, size):
        """Load a font"""
        try:
            font = pygame.font.Font(path, size)
            self.fonts[key] = font
            return font
        except pygame.error:
            print(f"Error loading font: {path}")
            return pygame.font.SysFont('Arial', size)
    
    def get_font(self, key):
        """Retrieve a loaded font"""
        return self.fonts.get(key, pygame.font.SysFont('Arial', 16))
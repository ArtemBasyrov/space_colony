import pygame

class PopulationPanel:
    def __init__(self, screen):
        self.screen = screen
        self.rect = pygame.Rect(840, 100, 164, 150)
    
    # population_panel.py - update to show individual stats
    def draw(self, population):
        """Draw the population panel"""
        avg_happiness = population.calculate_average_happiness()
        avg_health = population.calculate_average_health()
        if avg_happiness < 20 or avg_health < 20:
            warning = True
        else:
            warning = False

        self.screen.draw_panel(self.rect.x, self.rect.y, self.rect.width, self.rect.height, "Population", warning)
        
        text = self.screen.graphics.small_font.render(f"Colonists: {population.count}/1000", True, self.screen.graphics.colors['text'])
        self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 40))
        
        text = self.screen.graphics.small_font.render(f"Avg Happiness: {avg_happiness:.1f}", True, self.screen.graphics.colors['text'])
        self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 60))
        
        text = self.screen.graphics.small_font.render(f"Avg Health: {avg_health:.1f}", True, self.screen.graphics.colors['text'])
        self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 80))
        
        # Housing stats
        housed = population.get_housed_count()
        housing_text = self.screen.graphics.small_font.render(f"Housed: {housed}/{population.count}", True, self.screen.graphics.colors['text'])
        self.screen.graphics.screen.blit(housing_text, (self.rect.x + 10, self.rect.y + 100))
        
        # Housing capacity if available
        if hasattr(population, 'get_available_housing'):
            available = population.get_available_housing(self.screen.graphics.game.buildings)
            capacity = population.get_total_housing_capacity(self.screen.graphics.game.buildings)
            capacity_text = self.screen.graphics.small_font.render(f"Housing: {capacity - available}/{capacity}", True, self.screen.graphics.colors['text'])
            self.screen.graphics.screen.blit(capacity_text,(self.rect.x + 10, self.rect.y + 120))
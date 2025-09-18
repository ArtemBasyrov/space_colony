import pygame

class EconomyPanel:
    def __init__(self, screen):
        self.screen = screen
        self.rect = pygame.Rect(840, 260, 164, 150)
 
    def draw(self, population):
        """Draw the economy panel"""
        self.screen.draw_panel(self.rect.x, self.rect.y, self.rect.width, self.rect.height, "Economy")
        
        text = self.screen.graphics.small_font.render(f"Avg wage: {self.screen.format_number(population.calculate_average_wage())} credits", True, self.screen.graphics.colors['text'])
        self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 40))
        
        daily_cost = self.screen.format_number(population.calculate_total_wages())
        text = self.screen.graphics.small_font.render(f"Daily cost: {daily_cost}", True, self.screen.graphics.colors['text'])
        self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 60))
        
        text = self.screen.graphics.small_font.render(f"Employed: {population.employed_workers}/{population.count}", True, self.screen.graphics.colors['text'])
        self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 80))
        
        # Add construction info if in construction mode
        if self.screen.game.construction_mode and self.screen.game.selected_building_type:
            from buildings import get_building_name
            building_type = self.screen.game.selected_building_type
            text = self.screen.graphics.small_font.render(f"Placing: {get_building_name(building_type)}", True, (100, 255, 100))
            self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 100))
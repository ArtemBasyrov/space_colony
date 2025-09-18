import pygame
from .screen import Screen

class WagesScreen(Screen):
    def __init__(self, graphics):
        super().__init__(graphics)
    
    def on_button_click(self, action):
        """Handle button clicks in wages screen"""
        if action == "back":
            self.graphics.set_screen('main')
            
        elif action.startswith("wage_"):
            wage = int(action.split("_")[1])
            pop = self.game.population
            old_wage = pop.calculate_average_wage()
            pop.set_wage_for_all(wage)
            self.graphics.show_message(f"Wage changed from {old_wage} to {wage} credits")
    
    def draw(self):
        # Background
        self.graphics.screen.fill(self.graphics.colors['background'])
        
        # Title
        title_text = self.graphics.title_font.render("Wage Management", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (20, 20))
        
        # Wage info
        self.draw_panel(20, 70, 984, 200, "Current Wage Situation")
        pop = self.game.population
        
        text = self.graphics.normal_font.render(f"Current wage: {self.format_number(pop.calculate_average_wage())} credits/worker/day", True, self.graphics.colors['text'])
        self.graphics.screen.blit(text, (30, 110))
        
        text = self.graphics.normal_font.render(f"Employed colonists: {pop.employed_workers}", True, self.graphics.colors['text'])
        self.graphics.screen.blit(text, (30, 140))
        
        text = self.graphics.normal_font.render(f"Unemployed colonists: {pop.available_workers}", True, self.graphics.colors['text'])
        self.graphics.screen.blit(text, (30, 170))
        
        text = self.graphics.normal_font.render(f"Daily wage cost: {self.format_number(pop.calculate_total_wages())} credits", True, self.graphics.colors['text'])
        self.graphics.screen.blit(text, (30, 200))
        
        # Wage effects
        current_wage = pop.calculate_average_wage()
        effect_text = ""
        if current_wage >= 10:
            effect_text = "VERY HIGH wages: +5 morale/day (Extremely happy workers)"
        elif current_wage >= 8:
            effect_text = "High wages: +3 morale/day (Happy workers)"
        elif current_wage >= 7:
            effect_text = "Above average: +1 morale/day (Satisfied workers)"
        elif current_wage == 6:
            effect_text = "Average wages: no morale effect (Content workers)"
        elif current_wage == 5:
            effect_text = "Below average: -1 morale/day (Concerned workers)"
        elif current_wage == 4:
            effect_text = "Low wages: -3 morale/day (Dissatisfied workers)"
        elif current_wage <= 3:
            effect_text = "VERY LOW wages: -5 morale/day (Angry workers)"
        
        text = self.graphics.normal_font.render(effect_text, True, self.graphics.colors['text'])
        self.graphics.screen.blit(text, (30, 230))
        
        # Wage adjustment buttons
        self.draw_panel(20, 290, 984, 200, "Adjust Wages")
        
        for i, wage in enumerate([3, 4, 5, 6, 7, 8, 10]):
            x = 30 + (i % 4) * 240
            y = 330 + (i // 4) * 60
            
            button_text = f"{wage} credits"
            self.draw_button(x, y, 220, 40, button_text, f"wage_{wage}")
        
        # Back button
        self.draw_button(40, 510, 150, 40, "Back", "back")
# wages_screen.py - FIXED VERSION
import pygame
import os
import sys

# Fix import path for professions
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from professions import PROFESSIONS, get_all_professions
from .screen import Screen

class WagesScreen(Screen):
    def __init__(self, graphics):
        super().__init__(graphics)
        self.professions = {}
        self.dragging_slider = None
        self.slider_width = 300
        self.slider_height = 20
        self.slider_knob_size = 24  # Increased for better usability
        
        # Initialize professions from centralized config
        for profession_key in get_all_professions():
            prof_data = PROFESSIONS[profession_key]
            self.professions[profession_key] = {
                'name': prof_data['name'],
                'min_wage': prof_data['min_wage'],
                'max_wage': prof_data['max_wage'],
                'current_wage': prof_data['default_wage'],
                'color': prof_data['color']
            }
        
    def get_profession_stats(self):
        """Get statistics for each profession"""
        stats = {}
        pop = self.game.population
        
        # Count colonists in each profession
        for profession_key in self.professions.keys():
            stats[profession_key] = len([
                c for c in pop.colonists 
                if c.employed and c.profession == profession_key
            ])
        
        stats['unemployed'] = len(pop.unemployed_colonists)
        
        # Calculate total wage costs
        total_cost = 0
        for profession_key, data in self.professions.items():
            stats[f'{profession_key}_cost'] = stats[profession_key] * data['current_wage']
            total_cost += stats[f'{profession_key}_cost']
        
        stats['total_cost'] = total_cost
        
        return stats
    
    def calculate_expected_happiness_change(self, profession_key, new_wage):
        """Calculate expected happiness change for a profession based on wage"""
        pop = self.game.population
        count = 0
        wage_satisfaction = []
        for colonist in pop.employed_colonists:
            if colonist.profession == profession_key:
                wage_satisfaction.append(colonist.calculate_wage_satisfaction())
                count += 1

        if count == 0:
            return 0
        else:
            avg_current_satisfaction = sum(wage_satisfaction) / count
            return avg_current_satisfaction
    
    def update_wages_for_profession(self, profession_key, new_wage):
        """Update wages for all colonists in a specific profession"""
        pop = self.game.population
        changed_count = 0
        
        for colonist in pop.colonists:
            if colonist.employed and colonist.profession == profession_key:
                if colonist.set_wage(new_wage):
                    changed_count += 1
        
        self.professions[profession_key]['current_wage'] = new_wage
        return changed_count
    
    def handle_event(self, event):
        """Handle mouse events for slider dragging"""
        # Handle slider dragging first
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            # Check if clicking on any slider knob or slider track
            for profession_key, data in self.professions.items():
                slider_rect = self.get_slider_rect(profession_key)
                knob_rect = self.get_knob_rect(profession_key, slider_rect)
                
                # Check if clicking on knob OR on the slider track
                if knob_rect.collidepoint(mouse_pos) or slider_rect.collidepoint(mouse_pos):
                    self.dragging_slider = profession_key
                    
                    # If clicked on track (not knob), jump to that position
                    if not knob_rect.collidepoint(mouse_pos):
                        self.handle_track_click(profession_key, slider_rect, mouse_pos)
                    break
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_slider = None
        
        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            mouse_x = event.pos[0]
            profession_key = self.dragging_slider
            slider_rect = self.get_slider_rect(profession_key)
            
            # Calculate new wage based on mouse position
            relative_x = max(0, min(self.slider_width, mouse_x - slider_rect.x))
            new_wage = int((relative_x / self.slider_width) * 
                          (self.professions[profession_key]['max_wage'] - self.professions[profession_key]['min_wage']) + 
                          self.professions[profession_key]['min_wage'])
            
            # Update wage if changed
            if new_wage != self.professions[profession_key]['current_wage']:
                self.update_wages_for_profession(profession_key, new_wage)
        
        # Only call parent class for non-slider events
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 
            self.dragging_slider is None):
            super().handle_event(event)
    
    def handle_track_click(self, profession_key, slider_rect, mouse_pos):
        """Handle clicking directly on the slider track"""
        mouse_x = mouse_pos[0]
        relative_x = max(0, min(self.slider_width, mouse_x - slider_rect.x))
        new_wage = int((relative_x / self.slider_width) * 
                      (self.professions[profession_key]['max_wage'] - self.professions[profession_key]['min_wage']) + 
                      self.professions[profession_key]['min_wage'])
        
        self.update_wages_for_profession(profession_key, new_wage)
    
    def get_slider_rect(self, profession_key):
        """Get the rectangle for a profession's slider"""
        profession_index = list(self.professions.keys()).index(profession_key)
        return pygame.Rect(50, 260 + profession_index * 120, self.slider_width, self.slider_height)
    
    def get_knob_rect(self, profession_key, slider_rect=None):
        """Get the rectangle for the slider knob"""
        if slider_rect is None:
            slider_rect = self.get_slider_rect(profession_key)
            
        knob_pos = self.wage_to_slider_pos(profession_key, self.professions[profession_key]['current_wage'])
        
        # Center the knob vertically on the slider
        knob_y = slider_rect.y + (self.slider_height - self.slider_knob_size) // 2
        
        return pygame.Rect(
            slider_rect.x + knob_pos - self.slider_knob_size // 2,
            knob_y,
            self.slider_knob_size,
            self.slider_knob_size
        )
    
    def wage_to_slider_pos(self, profession_key, wage):
        """Convert wage value to slider position"""
        data = self.professions[profession_key]
        return ((wage - data['min_wage']) / (data['max_wage'] - data['min_wage'])) * self.slider_width
    
    def on_button_click(self, action):
        """Handle button clicks"""
        if action == "back":
            self.graphics.set_screen('main')
    
    def draw_slider(self, profession_key, x, y):
        """Draw a wage slider for a profession"""
        data = self.professions[profession_key]
        stats = self.get_profession_stats()
        
        # Draw profession label
        profession_text = f"{data['name']} ({stats[profession_key]} colonists)"
        text_surf = self.graphics.normal_font.render(profession_text, True, self.graphics.colors['text'])
        self.graphics.screen.blit(text_surf, (x, y - 25))
        
        # Draw current wage
        wage_text = f"Current: {data['current_wage']} credits"
        wage_surf = self.graphics.small_font.render(wage_text, True, self.graphics.colors['text'])
        self.graphics.screen.blit(wage_surf, (x + self.slider_width + 10, y))
        
        # Draw slider background (track)
        slider_rect = pygame.Rect(x, y, self.slider_width, self.slider_height)
        pygame.draw.rect(self.graphics.screen, (50, 50, 50), slider_rect, border_radius=3)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], slider_rect, 1, border_radius=3)
        
        # Draw slider fill (progress)
        fill_width = (data['current_wage'] - data['min_wage']) / (data['max_wage'] - data['min_wage']) * self.slider_width
        fill_rect = pygame.Rect(x, y, fill_width, self.slider_height)
        pygame.draw.rect(self.graphics.screen, data['color'], fill_rect, border_radius=3)
        
        # Draw slider knob
        knob_rect = self.get_knob_rect(profession_key, slider_rect)
        
        # Draw knob with a slight shadow effect
        pygame.draw.rect(self.graphics.screen, (200, 200, 200), knob_rect, border_radius=4)
        pygame.draw.rect(self.graphics.screen, (100, 100, 100), knob_rect, 2, border_radius=4)
        
        # Add a subtle highlight to the knob
        highlight_rect = pygame.Rect(knob_rect.x + 2, knob_rect.y + 2, knob_rect.width - 4, 4)
        pygame.draw.rect(self.graphics.screen, (255, 255, 255, 100), highlight_rect, border_radius=2)
        
        # Draw min/max labels
        min_text = self.graphics.small_font.render(str(data['min_wage']), True, self.graphics.colors['text'])
        max_text = self.graphics.small_font.render(str(data['max_wage']), True, self.graphics.colors['text'])
        self.graphics.screen.blit(min_text, (x - 15, y + self.slider_height + 5))
        self.graphics.screen.blit(max_text, (x + self.slider_width - 10, y + self.slider_height + 5))
        
        return slider_rect
    
    def draw_happiness_info(self, profession_key, x, y):
        """Draw happiness change information for a profession"""
        data = self.professions[profession_key]
        expected_change = self.calculate_expected_happiness_change(profession_key, data['current_wage'])
        
        # Draw happiness change indicator
        change_text = f"Expected Happiness: {expected_change:+.0f}"
        change_color = self.graphics.colors['success'] if expected_change >= 0 else self.graphics.colors['warning']
        
        change_surf = self.graphics.normal_font.render(change_text, True, change_color)
        self.graphics.screen.blit(change_surf, (x, y))
        
        # Draw happiness effect description
        if expected_change >= 10:
            effect_text = "Workers are very happy with their wages"
        elif expected_change >= 0:
            effect_text = "Workers are satisfied with their wages"
        elif expected_change >= -10:
            effect_text = "Workers are concerned about low wages"
        else:
            effect_text = "Workers are very unhappy with low wages"
            
        effect_surf = self.graphics.small_font.render(effect_text, True, self.graphics.colors['text'])
        self.graphics.screen.blit(effect_surf, (x, y + 25))
    
    def draw(self):
        # Clear buttons at the start of each draw
        self.buttons = {}
        
        # Background
        self.draw_animated_background()
        
        # Title
        title_text = self.graphics.title_font.render("Wage Management", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (20, 20))
        
        # Statistics panel
        self.draw_panel(20, 70, 984, 100, "Employment Statistics")
        stats = self.get_profession_stats()
        
        # Draw statistics
        stats_texts = [
            f"Total Colonists: {self.game.population.count}",
            f"Unemployed: {stats['unemployed']}",
            f"Total Daily Wage Cost: {stats['total_cost']} credits"
        ]
        
        # Add profession-specific stats
        for i, profession_key in enumerate(self.professions.keys()):
            stats_texts.append(f"{self.professions[profession_key]['name']}s: {stats[profession_key]} - Cost: {stats[f'{profession_key}_cost']} credits/day")
        
        for i, text in enumerate(stats_texts):
            text_surf = self.graphics.normal_font.render(text, True, self.graphics.colors['text'])
            x_pos = 30 + (i % 3) * 320
            y_pos = 110 + (i // 3) * 25
            self.graphics.screen.blit(text_surf, (x_pos, y_pos))
        
        # Wage adjustment panel
        self.draw_panel(20, 190, 984, 400, "Adjust Wages by Profession")
        
        # Draw sliders and happiness info for each profession
        for i, (profession_key, data) in enumerate(self.professions.items()):
            y_pos = 260 + i * 120
            
            # Draw slider on left
            slider_rect = self.draw_slider(profession_key, 50, y_pos)
            
            # Draw happiness info on right
            self.draw_happiness_info(profession_key, 500, y_pos)
            
            # Draw daily cost for this profession
            cost_text = f"Daily Cost: {stats[f'{profession_key}_cost']} credits"
            cost_surf = self.graphics.normal_font.render(cost_text, True, self.graphics.colors['text'])
            self.graphics.screen.blit(cost_surf, (500, y_pos + 50))
        
        # Back button
        self.draw_button(40, 610, 150, 40, "Back", "back")
        
        # Instructions
        instructions = "Click and drag sliders or click on track to set wages. Wages affect colonist happiness."
        instr_surf = self.graphics.small_font.render(instructions, True, self.graphics.colors['text'])
        self.graphics.screen.blit(instr_surf, (50, 670))
# [file name]: quest_screen.py
# [file content begin]
import pygame
from .screen import Screen
from buildings import get_building_name

class QuestScreen(Screen):
    def __init__(self, graphics):
        super().__init__(graphics)
        self.selected_quest = None
        self.scroll_offset = 0
        self.max_scroll = 0
        self.active_tab = "active"  # "active" or "completed"
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_click(event.pos)
            elif event.button == 4:  # Mouse wheel up
                self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.button == 5:  # Mouse wheel down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
    
    def handle_click(self, mouse_pos):
        """Handle mouse clicks using action-based detection"""
        # Check all buttons for clicks
        for action, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                self.on_button_click(action)
                return
        
        # Check if click is in quest list area
        list_width = int(self.graphics.width * 0.4)
        list_x = 20
        list_y = 130  # Adjusted for tabs
        list_height = self.graphics.height - 210  # Adjusted for tabs and back button
        
        quest_list_rect = pygame.Rect(list_x, list_y, list_width, list_height)
        
        if quest_list_rect.collidepoint(mouse_pos):
            self.handle_quest_list_click(mouse_pos, list_x, list_y, list_width, list_height)
    
    def on_button_click(self, action):
        """Handle button actions"""
        if action == "back":
            self.graphics.set_screen('main')
        elif action == "tab_active":
            self.active_tab = "active"
            self.scroll_offset = 0
        elif action == "tab_completed":
            self.active_tab = "completed" 
            self.scroll_offset = 0
    
    def handle_quest_list_click(self, mouse_pos, list_x, list_y, list_width, list_height):
        """Handle clicks on the quest list items"""
        quest_manager = self.game.quest_manager
        
        # Get quests based on active tab
        if self.active_tab == "active":
            quests = quest_manager.get_active_quests() + quest_manager.get_available_quests()
        else:
            quests = quest_manager.completed_quests
        
        item_height = 60
        visible_items = list_height // item_height

        for i, quest in enumerate(quests):
            if i * item_height - self.scroll_offset < list_height and (i + 1) * item_height - self.scroll_offset > 0:
                item_y = list_y + (i * item_height) - self.scroll_offset
                item_rect = pygame.Rect(list_x, item_y, list_width, item_height)
                
                if item_rect.collidepoint(mouse_pos):
                    self.selected_quest = quest
                    break
    
    def draw(self):
        """Draw the quest screen"""
        # Draw animated background
        self.draw_animated_background()
        
        # Draw title
        title_text = self.graphics.title_font.render("Quest Log", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (20, 20))
        
        # Draw quest list panel
        list_width = int(self.graphics.width * 0.4)
        list_x = 20
        list_y = 80
        list_height = self.graphics.height - 160
        
        self.draw_panel(list_x, list_y, list_width, list_height, "Quests")
        
        # Draw tabs
        self.draw_tabs(list_x, list_y, list_width)
        
        # Draw quest details panel (right side)
        details_x = list_x + list_width + 20
        details_width = self.graphics.width - details_x - 20
        details_height = self.graphics.height - 160
        
        self.draw_panel(details_x, list_y, details_width, details_height, "Quest Details")
        
        # Draw quest list (below tabs)
        quest_list_y = list_y + 50  # Below tabs
        quest_list_height = list_height - 50  # Reduced height for tabs
        self.draw_quest_list(list_x, quest_list_y, list_width, quest_list_height)
        
        # Draw selected quest details
        if self.selected_quest:
            self.draw_quest_details(details_x, list_y+30, details_width, details_height)
        
        # Draw back button
        button_y = list_y + list_height + 20
        self.draw_button(40, button_y, 150, 40, "Back", "back")
    
    def draw_tabs(self, x, y, width):
        """Draw the active/completed tabs"""
        tab_height = 40
        tab_width = width // 2
        
        # Active tab
        active_color = self.graphics.colors['button_hover'] if self.active_tab == "active" else self.graphics.colors['button']
        pygame.draw.rect(self.graphics.screen, active_color, (x, y, tab_width, tab_height), border_radius=3)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (x, y, tab_width, tab_height), 1, border_radius=3)
        
        active_text = self.graphics.normal_font.render("Active Quests", True, self.graphics.colors['button_text'])
        active_rect = active_text.get_rect(center=(x + tab_width // 2, y + tab_height // 2))
        self.graphics.screen.blit(active_text, active_rect)
        
        # Store tab button for click detection
        self.buttons["tab_active"] = pygame.Rect(x, y, tab_width, tab_height)
        
        # Completed tab
        completed_color = self.graphics.colors['button_hover'] if self.active_tab == "completed" else self.graphics.colors['button']
        pygame.draw.rect(self.graphics.screen, completed_color, (x + tab_width, y, tab_width, tab_height), border_radius=3)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (x + tab_width, y, tab_width, tab_height), 1, border_radius=3)
        
        completed_text = self.graphics.normal_font.render("Completed Quests", True, self.graphics.colors['button_text'])
        completed_rect = completed_text.get_rect(center=(x + tab_width + tab_width // 2, y + tab_height // 2))
        self.graphics.screen.blit(completed_text, completed_rect)
        
        # Store tab button for click detection
        self.buttons["tab_completed"] = pygame.Rect(x + tab_width, y, tab_width, tab_height)
    
    def draw_quest_list(self, x, y, width, height):
        """Draw the scrollable quest list"""
        quest_manager = self.game.quest_manager
        
        # Get quests based on active tab
        if self.active_tab == "active":
            quests = quest_manager.get_active_quests() + quest_manager.get_available_quests()
            if not quests:
                no_quests_text = self.graphics.normal_font.render("No active quests available", True, self.graphics.colors['text'])
                text_rect = no_quests_text.get_rect(center=(x + width // 2, y + height // 2))
                self.graphics.screen.blit(no_quests_text, text_rect)
                return
        else:
            quests = quest_manager.completed_quests
            if not quests:
                no_quests_text = self.graphics.normal_font.render("No completed quests yet", True, self.graphics.colors['text'])
                text_rect = no_quests_text.get_rect(center=(x + width // 2, y + height // 2))
                self.graphics.screen.blit(no_quests_text, text_rect)
                return
        
        item_height = 60
        visible_items = height // item_height
        
        # Calculate maximum scroll
        total_height = len(quests) * item_height
        self.max_scroll = max(0, total_height - height)
        
        # Draw scrollable area
        scroll_area = pygame.Rect(x + 5, y + 5, width - 10, height - 10)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['panel'], scroll_area)
        
        for i, quest in enumerate(quests):
            item_y = y + 5 + (i * item_height) - self.scroll_offset
            
            # Only draw if visible in scroll area
            if item_y + item_height >= y + 5 and item_y < y + height - 5:
                # Highlight selected quest
                if quest == self.selected_quest:
                    pygame.draw.rect(self.graphics.screen, self.graphics.colors['button_hover'], 
                                    (x + 5, item_y, width - 20, item_height - 5), border_radius=3)
                
                # Draw quest state indicator
                state_color = self.get_quest_state_color(quest.state)
                pygame.draw.rect(self.graphics.screen, state_color, (x + 15, item_y + 10, 10, 10))
                
                # Draw quest title
                title_text = self.graphics.normal_font.render(quest.title, True, self.graphics.colors['text'])
                self.graphics.screen.blit(title_text, (x + 35, item_y + 10))
                
                # Draw quest description
                desc_text = self.graphics.small_font.render(quest.description, True, self.graphics.colors['text'])
                self.graphics.screen.blit(desc_text, (x + 35, item_y + 35))
        
        # Draw scroll bar if needed
        if self.max_scroll > 0:
            self.draw_scrollbar(x + width - 15, y + 5, 10, height - 10)
    
    def draw_scrollbar(self, x, y, width, height):
        """Draw a scrollbar for the quest list"""
        # Draw scrollbar background
        pygame.draw.rect(self.graphics.screen, (50, 60, 80), (x, y, width, height), border_radius=5)
        
        # Calculate scrollbar thumb size and position
        if self.max_scroll > 0:
            thumb_height = max(30, height * height / (self.get_quest_count() * 60))
            thumb_position = y + (self.scroll_offset / self.max_scroll) * (height - thumb_height)
            
            # Draw scrollbar thumb
            pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], 
                           (x, thumb_position, width, thumb_height), border_radius=5)
    
    def get_quest_count(self):
        """Get the number of quests in the active tab"""
        quest_manager = self.game.quest_manager
        if self.active_tab == "active":
            return len(quest_manager.get_active_quests() + quest_manager.get_available_quests())
        else:
            return len(quest_manager.completed_quests)
    
    def draw_quest_details(self, x, y, width, height):
        """Draw detailed information about the selected quest"""
        quest = self.selected_quest
        
        # Draw quest title
        title_text = self.graphics.header_font.render(quest.title, True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (x + 20, y + 20))
        
        # Draw quest state
        state_text = self.graphics.normal_font.render(f"Status: {quest.state.value}", True, self.get_quest_state_color(quest.state))
        self.graphics.screen.blit(state_text, (x + width - 150, y + 25))

        # Draw faction origin
        faction_name = "The Board"
        faction_color = self.graphics.colors['text']
        state_text = self.graphics.normal_font.render(f"Faction: {faction_name}", True, faction_color)
        self.graphics.screen.blit(state_text, (x + width - 150, y + 50))
        
        # Draw description
        desc_y = y + 60
        desc_text = self.graphics.normal_font.render(quest.description, True, self.graphics.colors['text'])
        self.graphics.screen.blit(desc_text, (x + 20, desc_y))
        
        # Draw detailed text with proper formatting
        text_y = desc_y + 40
        self.draw_formatted_text(quest.detailed_text, x + 20, text_y, width - 40, self.graphics.normal_font)
        
        # Draw objectives
        obj_y = text_y + self.get_formatted_text_height(quest.detailed_text, width - 40, self.graphics.normal_font) + 30
        obj_title = self.graphics.header_font.render("Objectives:", True, self.graphics.colors['text'])
        self.graphics.screen.blit(obj_title, (x + 20, obj_y))
        
        obj_y += 40
        for objective in quest.objectives:
            status = "✓" if objective.get('completed', False) else "○"
            color = self.graphics.colors['success'] if objective.get('completed', False) else self.graphics.colors['text']
            
            obj_text = f"{status} {self.format_objective_text(objective)}"
            obj_surf = self.graphics.normal_font.render(obj_text, True, color)
            self.graphics.screen.blit(obj_surf, (x + 30, obj_y))
            obj_y += 30
        
        # Draw rewards
        if quest.rewards:
            rew_y = obj_y + 20
            rew_title = self.graphics.header_font.render("Rewards:", True, self.graphics.colors['text'])
            self.graphics.screen.blit(rew_title, (x + 20, rew_y))
            
            rew_y += 40
            for reward in quest.rewards:
                # Use the description from the reward dictionary
                rew_text = "○ "+reward.get("description", "Unknown reward")
                rew_surf = self.graphics.normal_font.render(rew_text, True, self.graphics.colors['success'])
                self.graphics.screen.blit(rew_surf, (x + 30, rew_y))
                rew_y += 30
    
    def draw_formatted_text(self, text, x, y, max_width, font):
        """Draw text with proper formatting - handles newlines and ignores extra whitespace"""
        # Clean the text - remove extra whitespace but preserve intentional line breaks
        lines = self.clean_and_split_text(text)
        line_height = font.get_linesize()
        
        for line in lines:
            # If line is empty, just add vertical space
            if not line.strip():
                y += line_height // 2  # Half line height for paragraph breaks
                continue
                
            # Draw each pre-formatted line with word wrapping
            words = line.split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_width, _ = font.size(test_line)
                
                if test_width > max_width and current_line:
                    # Draw the current line and start a new one
                    text_surf = font.render(' '.join(current_line), True, self.graphics.colors['text'])
                    self.graphics.screen.blit(text_surf, (x, y))
                    y += line_height
                    current_line = [word]
                else:
                    current_line.append(word)
            
            # Draw the remaining line
            if current_line:
                text_surf = font.render(' '.join(current_line), True, self.graphics.colors['text'])
                self.graphics.screen.blit(text_surf, (x, y))
                y += line_height
    
    def clean_and_split_text(self, text):
        """Clean text by removing extra whitespace and splitting into lines"""
        if not text:
            return []
            
        # Split by newlines first
        raw_lines = text.split('\n')
        cleaned_lines = []
        
        for line in raw_lines:
            # Remove leading/trailing whitespace from each line
            cleaned_line = line.strip()
            # Only add non-empty lines
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
            else:
                # Add empty string to represent paragraph breaks
                cleaned_lines.append("")
        
        return cleaned_lines
    
    def get_formatted_text_height(self, text, max_width, font):
        """Calculate the height needed for formatted text"""
        lines = self.clean_and_split_text(text)
        line_height = font.get_linesize()
        total_height = 0
        
        for line in lines:
            if not line.strip():
                total_height += line_height // 2  # Half line for paragraph breaks
                continue
                
            words = line.split()
            current_line = []
            lines_count = 1  # Start with 1 line for the current paragraph
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_width, _ = font.size(test_line)
                
                if test_width > max_width and current_line:
                    lines_count += 1
                    current_line = [word]
                else:
                    current_line.append(word)
            
            total_height += lines_count * line_height
        
        return total_height
    
    def format_objective_text(self, objective):
        """Format objective data into readable text"""
        obj_type = objective['type']
        
        if obj_type == 'building_count':
            building_type = objective['building_type']
            required = objective['required']
            building_instance = building_type()
            current = sum(1 for b in self.game.buildings if isinstance(b, building_type))
            return f"Build {required} {building_instance.name} ({current}/{required})"
        
        elif obj_type == 'resource_amount':
            resource = objective['resource_type']
            required = objective['required']
            current = getattr(self.game.resources, resource, 0)
            return f"Accumulate {required} {resource} ({current}/{required})"
        
        elif obj_type == 'population_count':
            required = objective['required']
            current = self.game.population.count
            return f"Reach {required} colonists ({current}/{required})"
        
        elif obj_type == 'consecutive_days_positive':
            required = objective['required']
            return f"Maintain positive balance for {required} consecutive days"
        
        else:
            return f"Unknown objective: {obj_type}"
    
    def get_quest_state_color(self, state):
        """Get color for quest state indicator"""
        state_colors = {
            'available': (100, 100, 255),    # Blue
            'active': (255, 200, 0),         # Yellow
            'completed': (0, 255, 0),        # Green
            'failed': (255, 0, 0)            # Red
        }
        return state_colors.get(state.value, (200, 200, 200))
# [file content end]
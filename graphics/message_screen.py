# [file name]: message_screen.py
# [file content begin]
import pygame
import os
from .screen import Screen
import random

class MessageScreen(Screen):
    def __init__(self, graphics):
        super().__init__(graphics)
        self.current_message = None
        self.portrait_cache = {}  # Cache for loaded portraits
        self.typewriter_index = 0
        self.typewriter_speed = 30  # characters per second
        self.last_update_time = 0
        self.typewriter_complete = False

        # Calculate window dimensions (80% of screen size)
        self.window_width = int(self.graphics.width * 0.7)
        self.window_height = int(self.graphics.height * 0.6)
        
    def set_message(self, message):
        """Set the current message to display"""
        self.current_message = message
        self.typewriter_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.typewriter_complete = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # If typewriter is still running, complete it immediately
                if not self.typewriter_complete:
                    self.typewriter_complete = True
                    self.typewriter_index = len(self.current_message.text) if self.current_message else 0
                else:
                    self.close_message()
    
    def handle_click(self, mouse_pos):
        """Handle mouse clicks"""
        # Check if next button was clicked
        for action, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                # If typewriter is still running, complete it immediately
                if not self.typewriter_complete:
                    self.typewriter_complete = True
                    self.typewriter_index = len(self.current_message.text) if self.current_message else 0
                else:
                    self.on_button_click(action)
                return
        
        # If clicking elsewhere and typewriter is still running, complete it immediately
        if not self.typewriter_complete:
            self.typewriter_complete = True
            self.typewriter_index = len(self.current_message.text) if self.current_message else 0
    
    def on_button_click(self, action):
        """Handle button actions"""
        if action == "next":
            self.close_message()
    
    def close_message(self):
        """Close the message and return to main screen"""
        if self.current_message:
            self.game.message_manager.complete_current_message()
        self.current_message = None
        
        # If there are more pending messages, show the next one
        if self.game.message_manager.has_pending_messages():
            next_message = self.game.message_manager.get_next_pending_message()
            if next_message:
                self.set_message(next_message)
            else:
                self.graphics.set_screen('main')
        else:
            self.graphics.set_screen('main')
    
    def draw(self):
        """Draw the message screen overlay"""
        # Update typewriter effect
        self.update_typewriter()
        
        # Draw the main screen first (dimmed)
        self.graphics.screens['main'].draw()
        
        # Draw semi-transparent overlay
        self.draw_dimmed_background()
        
        # Draw message window
        self.draw_message_window()
        
        # Draw next button (only when typewriter is complete)
        if self.typewriter_complete:
            self.draw_next_button()
    
    def update_typewriter(self):
        """Update the typewriter effect based on time"""
        if self.current_message and not self.typewriter_complete:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.last_update_time
            
            # Calculate how many characters to add based on elapsed time
            chars_to_add = int(elapsed * self.typewriter_speed / 1000)
            
            if chars_to_add > 0:
                self.typewriter_index = min(self.typewriter_index + chars_to_add, len(self.current_message.text))
                self.last_update_time = current_time
                
                # Check if we've reached the end
                if self.typewriter_index >= len(self.current_message.text):
                    self.typewriter_complete = True
    
    def draw_dimmed_background(self):
        """Draw a semi-transparent overlay"""
        overlay = pygame.Surface((self.graphics.width, self.graphics.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.graphics.screen.blit(overlay, (0, 0))
    
    def draw_message_window(self):
        """Draw the message window"""
        if not self.current_message:
            return
            
        window_x = (self.graphics.width - self.window_width) // 2
        window_y = (self.graphics.height - self.window_height) // 2
        
        # Draw window background and border
        pygame.draw.rect(self.graphics.screen, (30, 40, 60), 
                        (window_x, window_y, self.window_width, self.window_height), 
                        border_radius=10)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], 
                        (window_x, window_y, self.window_width, self.window_height), 
                        2, border_radius=10)
        
        # Draw title bar (inside the window)
        title_height = 50
        title_y = window_y + 5  # Leave some space from top border
        pygame.draw.rect(self.graphics.screen, (40, 50, 80), 
                        (window_x + 5, title_y, self.window_width - 10, title_height), 
                        border_radius=8)
        
        # Draw title
        title_text = self.graphics.header_font.render(self.current_message.title, True, self.graphics.colors['text'])
        title_rect = title_text.get_rect(center=(window_x + self.window_width // 2, title_y + title_height // 2))
        self.graphics.screen.blit(title_text, title_rect)
        
        # Draw content area (below title bar)
        content_x = window_x + 20
        content_y = title_y + title_height + 15
        content_width = self.window_width - 40
        content_height = self.window_height - (title_height + 15) - 80  # Space for button at bottom
        
        # Define portrait area boundaries (invisible box for layout calculations)
        portrait_size = 150
        portrait_x = content_x
        portrait_y = content_y
        portrait_area_width = portrait_size + 10  # Extra space for margins
        
        # Draw portrait (no container box)
        portrait_rect = pygame.Rect(portrait_x, portrait_y, portrait_size, portrait_size)
        self.draw_portrait(self.current_message.portrait, portrait_rect)
        
        # Draw sender name below portrait
        sender_y = portrait_y + portrait_size + 10
        sender_text = self.graphics.normal_font.render(self.current_message.sender, True, self.graphics.colors['text'])
        
        # Ensure sender name fits within portrait area
        max_sender_width = portrait_area_width - 10
        if sender_text.get_width() > max_sender_width:
            # Scale down font if name is too long
            sender_text = self.graphics.small_font.render(self.current_message.sender, True, self.graphics.colors['text'])
        
        sender_rect = sender_text.get_rect(center=(portrait_x + portrait_size // 2, sender_y))
        self.graphics.screen.blit(sender_text, sender_rect)
        
        # Calculate text area (starts to the right of portrait, can extend below it)
        text_x = portrait_x + portrait_size + 20
        text_y = content_y
        text_width = content_width - portrait_size - 20
        
        # Calculate the bottom of the portrait area (for text flow)
        portrait_bottom = portrait_y + portrait_size + 30  # Include space for sender name
        
        # Draw message text - it can flow below the portrait if needed
        self.draw_message_text(self.current_message.text, text_x, text_y, text_width, portrait_bottom)

    def draw_portrait(self, portrait_name, rect):
        """Draw a portrait, either from file or as a placeholder, with incoming transmission effect"""
        # Check if we're in the first 5 seconds of message display
        current_time = pygame.time.get_ticks()
        message_start_time = getattr(self, 'message_start_time', None)
        
        # If this is a new message, record the start time
        if self.current_message and not hasattr(self, 'current_message_id') or \
        (hasattr(self, 'current_message_id') and self.current_message_id != id(self.current_message)):
            self.message_start_time = current_time
            self.current_message_id = id(self.current_message)
        
        # Show noisy screen for first 5 seconds
        if self.message_start_time and current_time - self.message_start_time < 5000:
            self.draw_gaussian_noise_transmission(rect)
            return
        
        # After 5 seconds, show the actual portrait
        portrait_surface = self.load_portrait(portrait_name, rect.width, rect.height)
        
        if portrait_surface:
            # Center the portrait in the rectangle
            x_offset = (rect.width - portrait_surface.get_width()) // 2
            y_offset = (rect.height - portrait_surface.get_height()) // 2
            portrait_display_rect = pygame.Rect(
                rect.x + x_offset, 
                rect.y + y_offset, 
                portrait_surface.get_width(), 
                portrait_surface.get_height()
            )
            
            # Draw the portrait
            self.graphics.screen.blit(portrait_surface, portrait_display_rect)
            
            # Draw highlight border around the portrait
            pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], 
                           portrait_display_rect, 2)
            
            # Add random white noise dots on the portrait
            self.add_portrait_noise(portrait_display_rect)
        else:
            # Draw gray placeholder
            pygame.draw.rect(self.graphics.screen, (100, 100, 100), rect)
            pygame.draw.rect(self.graphics.screen, (150, 150, 150), rect, 1)
            
            # Draw placeholder text
            placeholder_text = self.graphics.small_font.render("Portrait", True, self.graphics.colors['text'])
            text_rect = placeholder_text.get_rect(center=rect.center)
            self.graphics.screen.blit(placeholder_text, text_rect)

    def draw_gaussian_noise_transmission(self, rect):
        """Draw a Gaussian noise transmission effect with incoming transmission text"""
        # Create a temporary surface for the noise
        noise_surface = pygame.Surface((rect.width, rect.height))
        
        # Generate Gaussian noise with brighter effect
        for x in range(0, rect.width, 2):
            for y in range(0, rect.height, 2):
                # Generate Gaussian-like noise using multiple random calls
                # This creates a more natural, less intense noise pattern
                base_noise = random.randint(50, 100)  # Brighter base noise
                
                # Add some time-based variation for animation
                time_factor = (pygame.time.get_ticks() // 50) % 100
                animated_noise = (x + y + time_factor) % 50  # Increased range for more variation
                
                # Combine for final noise value (keeping it in brighter tones)
                noise_value = min(180, base_noise + animated_noise)
                
                # Occasionally add brighter spots for more natural look
                if random.random() < 0.03:  # 3% chance of bright spot
                    noise_value = min(255, noise_value + random.randint(50, 100))
                
                color = (noise_value, noise_value, noise_value)
                pygame.draw.rect(noise_surface, color, (x, y, 2, 2))
        
        # Draw the noise to the screen
        self.graphics.screen.blit(noise_surface, rect)
        
        # Draw "incoming transmission" text on a black band
        text = "incoming transmission"
        text_surface = self.graphics.small_font.render(text, True, self.graphics.colors['text'])
        
        # Create a black band behind the text
        band_height = text_surface.get_height() + 10
        band_rect = pygame.Rect(
            rect.x,
            rect.y + (rect.height - band_height) // 2,
            rect.width,
            band_height
        )
        
        # Draw semi-transparent black band
        band_surface = pygame.Surface((band_rect.width, band_rect.height), pygame.SRCALPHA)
        band_surface.fill((0, 0, 0, 200))  # Semi-transparent black
        self.graphics.screen.blit(band_surface, band_rect)
        
        # Draw the text centered on the band
        text_rect = text_surface.get_rect(center=band_rect.center)
        self.graphics.screen.blit(text_surface, text_rect)
        
        # Optional: Add a subtle border to the noise area
        pygame.draw.rect(self.graphics.screen, (50, 50, 50), rect, 1)

    def add_portrait_noise(self, portrait_rect):
        """Add random white noise dots to the portrait"""
        # Add a few random white dots to simulate transmission noise
        for _ in range(5):  # Number of dots to add per frame
            # Random position within the portrait
            x = random.randint(portrait_rect.left, portrait_rect.right - 1)
            y = random.randint(portrait_rect.top, portrait_rect.bottom - 1)
            
            # Random size (1-2 pixels)
            size = random.randint(1, 2)
            
            # Draw the white dot
            pygame.draw.rect(self.graphics.screen, (255, 255, 255), (x, y, size, size))
        
    def load_portrait(self, portrait_name, max_width, max_height):
        """Load and scale a portrait image, or return None if not found"""
        if not portrait_name:
            return None
            
        # Check cache first
        cache_key = f"{portrait_name}_{max_width}_{max_height}"
        if cache_key in self.portrait_cache:
            return self.portrait_cache[cache_key]
        
        try:
            # Try to load portrait from assets/portraits directory
            portrait_path = f"assets/portraits/{portrait_name}.png"
            
            if not os.path.exists(portrait_path):
                # Try with different extensions
                for ext in ['.jpg', '.jpeg', '.bmp']:
                    alt_path = f"assets/portraits/{portrait_name}{ext}"
                    if os.path.exists(alt_path):
                        portrait_path = alt_path
                        break
                else:
                    # Portrait file not found
                    return None
            
            # Load the image
            portrait = pygame.image.load(portrait_path)
            
            # Convert for better performance
            if portrait.get_alpha():
                portrait = portrait.convert_alpha()
            else:
                portrait = portrait.convert()
            
            # Scale the portrait to fit within the maximum dimensions while maintaining aspect ratio
            original_width, original_height = portrait.get_size()
            
            # Calculate scaling factor
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            scale_ratio = min(width_ratio, height_ratio)
            
            # Scale the image
            new_width = int(original_width * scale_ratio)
            new_height = int(original_height * scale_ratio)
            scaled_portrait = pygame.transform.smoothscale(portrait, (new_width, new_height))
            
            # Cache the result
            self.portrait_cache[cache_key] = scaled_portrait
            return scaled_portrait
            
        except (pygame.error, Exception) as e:
            print(f"Error loading portrait {portrait_name}: {e}")
            return None
    
    def draw_message_text(self, text, x, y, max_width, portrait_bottom):
        """Draw the message text with proper formatting that can flow below the portrait"""
        # Get the current text to display based on typewriter progress
        display_text = text[:self.typewriter_index] if self.current_message else ""
        
        lines = self.clean_and_split_text(display_text)
        line_height = self.graphics.normal_font.get_linesize()
        
        # Track the position of the last character for cursor placement
        last_char_x = x
        last_char_y = y
        
        for line in lines:
            # If line is empty, just add vertical space
            if not line.strip():
                y += line_height // 2
                last_char_y = y
                continue
                
            # Draw each pre-formatted line with word wrapping
            words = line.split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_width, _ = self.graphics.normal_font.size(test_line)
                
                if test_width > max_width and current_line:
                    # Draw the current line and start a new one
                    text_surf = self.graphics.normal_font.render(' '.join(current_line), True, self.graphics.colors['text'])
                    self.graphics.screen.blit(text_surf, (x, y))
                    
                    # Update last character position to end of this line
                    last_char_x = x + text_surf.get_width()
                    last_char_y = y
                    
                    y += line_height
                    current_line = [word]
                else:
                    current_line.append(word)
            
            # Draw the remaining line
            if current_line:
                text_surf = self.graphics.normal_font.render(' '.join(current_line), True, self.graphics.colors['text'])
                self.graphics.screen.blit(text_surf, (x, y))
                
                # Update last character position to end of this line
                last_char_x = x + text_surf.get_width()
                last_char_y = y
                
                y += line_height
            
            # If we've passed the portrait bottom, we can use full width
            if y > portrait_bottom:
                # Reset x position to left edge for text below portrait
                window_x = (self.graphics.width - self.window_width) // 2
                x = window_x + 20  # Left margin of content area
                max_width = self.window_width - 40  # Full content width
                
                # Update portrait_bottom to a very high value so this only happens once
                portrait_bottom = float('inf')
        
        # Draw a blinking cursor if typewriter is still active
        if not self.typewriter_complete and pygame.time.get_ticks() % 1000 < 500:
            # Use the position of the last character we drew
            cursor_x = last_char_x
            cursor_y = last_char_y
            
            # Draw cursor at the end of the text
            pygame.draw.rect(self.graphics.screen, self.graphics.colors['text'], 
                        (cursor_x, cursor_y, 2, line_height - 2))
    
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
    
    def draw_next_button(self):
        """Draw the next button at the bottom of the message window"""
        window_x = (self.graphics.width - self.window_width) // 2
        window_y = (self.graphics.height - self.window_height) // 2
        
        button_width = 120
        button_height = 40
        button_x = window_x + self.window_width - button_width - 20
        button_y = window_y + self.window_height - button_height - 20
        
        self.draw_button(button_x, button_y, button_width, button_height, "Next", "next")
# [file content end]
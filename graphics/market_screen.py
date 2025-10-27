import pygame
from .screen import Screen
from .stock_market_screen import StockMarketScreen  # Add this import

class MarketScreen(Screen):
    def __init__(self, graphics):
        super().__init__(graphics)
        self.selected_resource = None
        self.custom_amount = ""
        self.input_active = False
        self.price_chart_visible = False
        self.input_rect = pygame.Rect(30, 230, 200, 40)
        self.show_market_info = False
        self.width = graphics.width-40
        self.n_rows = 1
    
    def on_button_click(self, action):
        """Handle button clicks in market screen"""
        if action == "back":
            self.graphics.set_screen('main')
            
        elif action == "stock_market":  # NEW: Handle stock market button
            self.graphics.set_screen('stock_market')
            
        elif action.startswith("select_"):
            resource = action.split("_")[1]
            self.selected_resource = resource
            self.custom_amount = ""
            self.input_active = False
            
        elif action.startswith("buy_") and self.selected_resource:
            resource = self.selected_resource
            if action == "buy_10":
                self.buy_resource(resource, 10)
            elif action == "buy_custom" and self.custom_amount:
                try:
                    amount = int(self.custom_amount)
                    if amount > 0:
                        self.buy_resource(resource, amount)
                except ValueError:
                    self.graphics.show_message("Please enter a valid number!")
                
        elif action.startswith("sell_") and self.selected_resource:
            resource = self.selected_resource
            if action == "sell_10":
                self.sell_resource(resource, 10)
            elif action == "sell_custom" and self.custom_amount:
                try:
                    amount = int(self.custom_amount)
                    if amount > 0:
                        self.sell_resource(resource, amount)
                except ValueError:
                    self.graphics.show_message("Please enter a valid number!")
                
        elif action == "toggle_chart" and self.selected_resource:
            self.price_chart_visible = not self.price_chart_visible
            
        elif action == "toggle_market_info" and self.selected_resource:
            self.show_market_info = not self.show_market_info
            
        elif action == "clear_input":
            self.custom_amount = ""
    
    def handle_event(self, event):
        """Handle keyboard and mouse events"""
        super().handle_event(event)
        
        # Handle mouse clicks for input field
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if click is on input field
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False
        
        # Handle keyboard input
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.custom_amount = self.custom_amount[:-1]
            elif event.key == pygame.K_RETURN:
                self.input_active = False
            elif event.key == pygame.K_ESCAPE:
                self.input_active = False
                self.custom_amount = ""
            elif event.unicode.isdigit():
                if len(self.custom_amount) < 6:
                    self.custom_amount += event.unicode
    
    # market_screen.py - update the draw method
    def draw(self):
        """Draw the market screen"""
        # Background
        #self.graphics.screen.fill(self.graphics.colors['background'])
        self.draw_animated_background()
        
        # Title
        title_text = self.graphics.title_font.render("Interstellar Market", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (20, 20))
        
        # Market prices panel
        tradable = self.game.market.get_tradable_resources()
        self.n_rows = (len(tradable) + 1) // 2
        self.draw_panel(20, 70, self.width, 360 + self.n_rows*45, "Market Trading")
        
        
        # Draw resource selection buttons WITH ICONS
        for i, resource in enumerate(tradable):
            x = 30 + (i % 2) * 480
            y = 110 + (i // 2) * 45
            
            # Resource selection button
            button_color = self.graphics.colors['button_hover'] if resource == self.selected_resource else self.graphics.colors['button']
            pygame.draw.rect(self.graphics.screen, button_color, (x, y, 470, 40), border_radius=3)
            pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (x, y, 470, 40), 1, border_radius=3)
            
            # Draw resource icon
            if resource in self.graphics.icons:
                self.graphics.screen.blit(self.graphics.icons[resource], (x + 10, y + 8))
            
            # Resource name
            resource_text = self.graphics.normal_font.render(f"{resource.capitalize()}", True, self.graphics.colors['button_text'])
            self.graphics.screen.blit(resource_text, (x + 40, y + 10))  # Offset text to right of icon
            
            # Draw price info for each resource
            price = self.game.market.prices[resource]
            buy_price = price * self.game.market.buy_markup
            sell_price = price * self.game.market.sell_fee
            available = getattr(self.game.resources, resource)
            
            price_text = self.graphics.small_font.render(f"Buy: {buy_price:.2f} / Sell: {sell_price:.2f}", True, self.graphics.colors['text'])
            self.graphics.screen.blit(price_text, (x + 150, y + 5))
            
            available_text = self.graphics.small_font.render(f"You have: {available:.1f}", True, self.graphics.colors['text'])
            self.graphics.screen.blit(available_text, (x + 150, y + 20))
            
            # Select button
            self.draw_button(x + 400, y + 5, 60, 30, "Select", f"select_{resource}")
        
        # Selected resource trading panel
        if self.selected_resource:
            self.draw_selected_resource_panel()
        
        # Back button
        bottom_buttons_y = 440 + self.n_rows*45
        self.draw_button(40, bottom_buttons_y, 150, 40, "Back", "back")
        self.draw_button(self.graphics.width - 190, bottom_buttons_y, 150, 40, "Stock Market", "stock_market")

    def draw_selected_resource_panel(self):
        """Draw trading panel for selected resource"""
        resource = self.selected_resource
        price = self.game.market.prices[resource]
        buy_price = price * self.game.market.buy_markup
        sell_price = price * self.game.market.sell_fee
        available = getattr(self.game.resources, resource)
        
        # Selected resource info
        self.draw_panel(20, 130+self.n_rows*40, self.width, 200, f"Trading: {resource.capitalize()}")
        panel_y = 200 + self.n_rows*40
        self.input_rect = pygame.Rect(30, panel_y, 200, 40)

        # Price info
        info_text = self.graphics.normal_font.render(f"Buy Price: {buy_price:.2f} | Sell Price: {sell_price:.2f} | You have: {available:.1f}", True, self.graphics.colors['text'])
        self.graphics.screen.blit(info_text, (30, panel_y-30))
        
        # Input field
        pygame.draw.rect(self.graphics.screen, (50, 60, 80), self.input_rect, border_radius=3)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], self.input_rect, 1, border_radius=3)
        
        # Draw input text or placeholder
        if self.custom_amount or self.input_active:
            amount_text = self.graphics.normal_font.render(self.custom_amount, True, self.graphics.colors['text'])
            self.graphics.screen.blit(amount_text, (self.input_rect.x + 10, self.input_rect.y + 10))
        else:
            placeholder_text = self.graphics.normal_font.render("Click to enter amount...", True, (100, 100, 100))
            self.graphics.screen.blit(placeholder_text, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        # Draw input field border when active
        if self.input_active:
            pygame.draw.rect(self.graphics.screen, self.graphics.colors['success'], self.input_rect, 2, border_radius=3)
        
        # Clear input button
        self.draw_button(240, panel_y, 80, 40, "Clear", "clear_input")
        
        # Buy/Sell buttons
        self.draw_button(350, panel_y, 100, 40, "Buy 10", "buy_10")
        self.draw_button(460, panel_y, 100, 40, "Sell 10", "sell_10")
        
        if self.custom_amount:
            try:
                amount = int(self.custom_amount)
                if amount > 0:
                    self.draw_button(350, panel_y+50, 100, 40, f"Buy {amount}", "buy_custom")
                    self.draw_button(460, panel_y+50, 100, 40, f"Sell {amount}", "sell_custom")
            except ValueError:
                pass
        
        # Chart and info toggle buttons (moved to the right side)
        chart_button_text = "Hide Price Chart" if self.price_chart_visible else "Show Price Chart"
        self.draw_button(580, panel_y, 150, 40, chart_button_text, "toggle_chart")
        
        info_button_text = "Hide Market Info" if self.show_market_info else "Show Market Info"
        self.draw_button(740, panel_y, 150, 40, info_button_text, "toggle_market_info")
        
        # Draw price chart if enabled
        if self.price_chart_visible:
            self.draw_price_chart(resource, panel_y)
            
        # Draw market information if enabled
        if self.show_market_info:
            self.draw_market_info(resource, panel_y)
    
    def draw_market_info(self, resource, panel_y):
        """Draw market information and player influence"""
        info_panel_rect = pygame.Rect(30, panel_y+60, 924, 150)
        pygame.draw.rect(self.graphics.screen, (40, 50, 70), info_panel_rect, border_radius=5)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], info_panel_rect, 1, border_radius=5)
        
        # Get market information
        market_info = self.game.market.get_market_info(resource)
        if not market_info:
            return
        
        # Title
        title_text = self.graphics.normal_font.render(f"Market Information: {resource.capitalize()}", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (info_panel_rect.x + 10, info_panel_rect.y + 10))
        
        # Market data - focused on useful information
        y_offset = info_panel_rect.y + 40
        info_lines = [
            f"Base Price: {market_info['base_price']:.2f} | Current: {market_info['current_price']:.2f}",
            f"Price Ratio: {market_info['price_ratio']:.2f}x base price",
            f"Player Influence: {market_info['player_influence'] * 100:.1f}% of market",
            f"Transaction Fees: {((market_info['buy_markup'] - 1) * 100):.0f}% buy markup, {((1 - market_info['sell_fee']) * 100):.0f}% sell fee",
            f"Market Depth: {market_info['market_depth']:.0f} units (other traders)"
        ]
        
        for line in info_lines:
            text = self.graphics.small_font.render(line, True, self.graphics.colors['text'])
            self.graphics.screen.blit(text, (info_panel_rect.x + 20, y_offset))
            y_offset += 20
            
        # Extreme capitalism warning/opportunity
        if market_info['player_influence'] > 0.1:
            if market_info['player_influence'] > 0.5:
                influence_text = "EXTREME: You dominate this market! Prices will swing wildly."
                color = self.graphics.colors['warning']
            else:
                influence_text = "Noticeable: Your trading affects market prices significantly."
                color = self.graphics.colors['success']
                
            text = self.graphics.small_font.render(influence_text, True, color)
            self.graphics.screen.blit(text, (info_panel_rect.x + 20, y_offset + 10))
    
    def draw_price_chart(self, resource, panel_y):
        """Draw price history chart for selected resource"""
        chart_panel_rect = pygame.Rect(30, panel_y+60, 924, 150)
        pygame.draw.rect(self.graphics.screen, (40, 50, 70), chart_panel_rect, border_radius=5)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], chart_panel_rect, 1, border_radius=5)
        
        # Chart title (above the chart)
        chart_title = self.graphics.normal_font.render(f"{resource.capitalize()} Price History (Last 30 Days)", True, self.graphics.colors['text'])
        self.graphics.screen.blit(chart_title, (chart_panel_rect.x + 10, chart_panel_rect.y + 10))
        
        # Get price history
        price_history = self.game.market.get_price_history(resource, 30)
        if not price_history:
            no_data_text = self.graphics.small_font.render("No price history available", True, self.graphics.colors['text'])
            self.graphics.screen.blit(no_data_text, (chart_panel_rect.x + 20, chart_panel_rect.y + 60))
            return
        
        # Chart area (inside the panel, below the title)
        chart_rect = pygame.Rect(
            chart_panel_rect.x + 50,  # Extra padding for y-axis labels
            chart_panel_rect.y + 40,
            chart_panel_rect.width - 60,
            chart_panel_rect.height - 50
        )
        
        # Draw chart background
        pygame.draw.rect(self.graphics.screen, (30, 40, 60), chart_rect)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], chart_rect, 1)
        
        # Find min and max prices for scaling
        min_price = min(price_history)
        max_price = max(price_history)
        price_range = max(max_price - min_price, 1)  # Avoid division by zero
        
        # Draw grid lines
        grid_color = (60, 70, 90)
        
        # Horizontal grid lines (price levels)
        num_horizontal_lines = 5
        for i in range(num_horizontal_lines):
            price_value = min_price + (i / (num_horizontal_lines - 1)) * price_range
            y = chart_rect.y + chart_rect.height - ((price_value - min_price) / price_range) * chart_rect.height
            pygame.draw.line(self.graphics.screen, grid_color, (chart_rect.x, y), (chart_rect.x + chart_rect.width, y), 1)
            
            # Price labels on y-axis
            price_text = self.graphics.small_font.render(f"{price_value:.1f}", True, self.graphics.colors['text'])
            self.graphics.screen.blit(price_text, (chart_rect.x - 45, y - 8))
        
        # Vertical grid lines (time intervals)
        num_vertical_lines = min(6, len(price_history))
        for i in range(0, len(price_history), max(1, len(price_history) // num_vertical_lines)):
            x = chart_rect.x + (i / (len(price_history) - 1)) * chart_rect.width if len(price_history) > 1 else chart_rect.x
            pygame.draw.line(self.graphics.screen, grid_color, (x, chart_rect.y), (x, chart_rect.y + chart_rect.height), 1)
            
            # Day labels on x-axis
            day_text = self.graphics.small_font.render(f"Day {i+1}", True, self.graphics.colors['text'])
            self.graphics.screen.blit(day_text, (x - 15, chart_rect.y + chart_rect.height + 5))
        
        # Draw price points and lines
        points = []
        for i, price in enumerate(price_history):
            x = chart_rect.x + (i / (len(price_history) - 1)) * chart_rect.width if len(price_history) > 1 else chart_rect.x
            y = chart_rect.y + chart_rect.height - ((price - min_price) / price_range) * chart_rect.height
            points.append((x, y))
            
            # Draw price point
            pygame.draw.circle(self.graphics.screen, (255, 200, 50), (int(x), int(y)), 3)
            pygame.draw.circle(self.graphics.screen, (255, 255, 255), (int(x), int(y)), 1)
        
        # Draw connecting lines
        if len(points) > 1:
            pygame.draw.lines(self.graphics.screen, (100, 200, 255), False, points, 2)
    
    def buy_resource(self, resource, amount):
        """Buy resources from market"""
        price = self.game.market.prices[resource] * 1.1
        available = self.game.resources.credits
        
        buyable_amount, cost = self.game.market.buy_resource(resource, amount, available)
        
        if buyable_amount > 0:
            setattr(self.game.resources, resource, getattr(self.game.resources, resource) + buyable_amount)
            self.game.resources.credits -= cost
            self.graphics.show_message(f"Bought {buyable_amount} {resource} for {cost:.2f} credits")
            self.custom_amount = ""  # Reset input after transaction
            self.input_active = False
        else:
            self.graphics.show_message("Not enough credits to buy!")
    
    def sell_resource(self, resource, amount):
        """Sell resources to market"""
        available = getattr(self.game.resources, resource)
        
        if available <= 0:
            self.graphics.show_message(f"You don't have any {resource} to sell!")
            return
        
        sellable_amount, revenue = self.game.market.sell_resource(resource, amount, available)
        
        if sellable_amount > 0:
            setattr(self.game.resources, resource, getattr(self.game.resources, resource) - sellable_amount)
            self.game.resources.credits += revenue
            self.graphics.show_message(f"Sold {self.graphics.format_number(sellable_amount)} {resource} for {revenue:.2f} credits")
            self.custom_amount = ""  # Reset input after transaction
            self.input_active = False
        else:
            self.graphics.show_message("Not enough resources to sell!")
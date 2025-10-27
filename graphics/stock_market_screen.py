import pygame
from .screen import Screen

class StockMarketScreen(Screen):
    def __init__(self, graphics):
        super().__init__(graphics)
        self.selected_stock = None
        self.custom_amount = ""
        self.input_active = False
        self.price_chart_visible = False
        self.input_rect = pygame.Rect(30, 230, 200, 40)
        self.show_market_info = False
        self.width = graphics.width - 40
        self.n_rows = 1
    
    def on_button_click(self, action):
        """Handle button clicks in stock market screen"""
        if action == "back":
            self.graphics.set_screen('market')
            
        elif action.startswith("select_"):
            stock = action.split("_")[1]
            self.selected_stock = stock
            self.custom_amount = ""
            self.input_active = False
            
        elif action.startswith("buy_") and self.selected_stock:
            stock = self.selected_stock
            if action == "buy_10":
                self.buy_stock(stock, 10)
            elif action == "buy_custom" and self.custom_amount:
                try:
                    amount = int(self.custom_amount)
                    if amount > 0:
                        self.buy_stock(stock, amount)
                except ValueError:
                    self.graphics.show_message("Please enter a valid number!")
                
        elif action.startswith("sell_") and self.selected_stock:
            stock = self.selected_stock
            if action == "sell_10":
                self.sell_stock(stock, 10)
            elif action == "sell_custom" and self.custom_amount:
                try:
                    amount = int(self.custom_amount)
                    if amount > 0:
                        self.sell_stock(stock, amount)
                except ValueError:
                    self.graphics.show_message("Please enter a valid number!")
                
        elif action == "toggle_chart" and self.selected_stock:
            self.price_chart_visible = not self.price_chart_visible
            
        elif action == "toggle_market_info" and self.selected_stock:
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
    
    def draw(self):
        """Draw the stock market screen"""
        # Background
        #self.graphics.screen.fill(self.graphics.colors['background'])
        self.draw_animated_background()
        
        # Title
        title_text = self.graphics.title_font.render("Galactic Stock Exchange", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (20, 20))
        
        # Market overview panel
        market_data = self.game.stock_market.get_all_indices()
        self.n_rows = (len(market_data) + 1) // 2
        self.draw_panel(20, 70, self.width, 360 + self.n_rows*45, "Stock Trading")
        
        # Draw stock selection buttons
        for i, (resource, stock_data) in enumerate(market_data.items()):
            x = 30 + (i % 2) * 480
            y = 110 + (i // 2) * 45
            
            # Stock selection button
            button_color = self.graphics.colors['button_hover'] if resource == self.selected_stock else self.graphics.colors['button']
            pygame.draw.rect(self.graphics.screen, button_color, (x, y, 470, 40), border_radius=3)
            pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], (x, y, 470, 40), 1, border_radius=3)
            
            # Draw resource icon if available
            if resource in self.graphics.icons:
                self.graphics.screen.blit(self.graphics.icons[resource], (x + 10, y + 8))
            
            # Stock ticker and name
            ticker_text = self.graphics.normal_font.render(f"{stock_data['ticker']}", True, self.graphics.colors['button_text'])
            self.graphics.screen.blit(ticker_text, (x + 40, y + 10))
            
            # Price and change info
            price_text = self.graphics.small_font.render(f"Price: {stock_data['current_price']:.2f}", True, self.graphics.colors['text'])
            self.graphics.screen.blit(price_text, (x + 150, y + 5))
            
            change_color = self.graphics.colors['success'] if stock_data['change'] >= 0 else self.graphics.colors['warning']
            change_text = self.graphics.small_font.render(f"Change: {stock_data['change']:+.2f} ({stock_data['percent_change']:+.1f}%)", True, change_color)
            self.graphics.screen.blit(change_text, (x + 150, y + 20))
            
            # Shares owned
            shares_owned = self.game.stock_market.player_portfolio[resource]
            shares_text = self.graphics.small_font.render(f"Owned: {shares_owned}", True, self.graphics.colors['text'])
            self.graphics.screen.blit(shares_text, (x + 320, y + 12))
            
            # Select button
            self.draw_button(x + 400, y + 5, 60, 30, "Select", f"select_{resource}")
        
        # Selected stock trading panel
        if self.selected_stock:
            self.draw_selected_stock_panel()
        
        # Back button
        self.draw_button(40, 440 + self.n_rows*45, 150, 40, "Back", "back")

    def draw_selected_stock_panel(self):
        """Draw trading panel for selected stock"""
        stock = self.selected_stock
        stock_data = self.game.stock_market.get_market_data(stock)
        if not stock_data:
            return
            
        portfolio = self.game.stock_market.player_portfolio
        shares_owned = portfolio[stock]
        current_price = stock_data['current_price']
        
        # Selected stock info
        self.draw_panel(20, 130+self.n_rows*40, self.width, 200, f"Trading: {stock_data['ticker']} - {stock_data['resource']} shares")
        panel_y = 200 + self.n_rows*40
        self.input_rect = pygame.Rect(30, panel_y, 200, 40)

        # Stock info
        info_text = self.graphics.normal_font.render(
            f"Price: {current_price:.2f} | Change: {stock_data['change']:+.2f} ({stock_data['percent_change']:+.1f}%) | Owned: {shares_owned}", 
            True, self.graphics.colors['text']
        )
        self.graphics.screen.blit(info_text, (30, panel_y-30))
        
        # Input field
        pygame.draw.rect(self.graphics.screen, (50, 60, 80), self.input_rect, border_radius=3)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], self.input_rect, 1, border_radius=3)
        
        # Draw input text or placeholder
        if self.custom_amount or self.input_active:
            amount_text = self.graphics.normal_font.render(self.custom_amount, True, self.graphics.colors['text'])
            self.graphics.screen.blit(amount_text, (self.input_rect.x + 10, self.input_rect.y + 10))
        else:
            placeholder_text = self.graphics.normal_font.render("Click to enter shares...", True, (100, 100, 100))
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
        
        # Chart and info toggle buttons
        chart_button_text = "Hide Price Chart" if self.price_chart_visible else "Show Price Chart"
        self.draw_button(580, panel_y, 150, 40, chart_button_text, "toggle_chart")
        
        info_button_text = "Hide Stock Info" if self.show_market_info else "Show Stock Info"
        self.draw_button(740, panel_y, 150, 40, info_button_text, "toggle_market_info")
        
        # Draw price chart if enabled
        if self.price_chart_visible:
            self.draw_price_chart(stock_data, panel_y)
            
        # Draw stock information if enabled
        if self.show_market_info:
            self.draw_stock_info(stock_data, panel_y)
    
    def draw_stock_info(self, stock_data, panel_y):
        """Draw detailed stock information"""
        info_panel_rect = pygame.Rect(30, panel_y+60, 924, 150)
        pygame.draw.rect(self.graphics.screen, (40, 50, 70), info_panel_rect, border_radius=5)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], info_panel_rect, 1, border_radius=5)
        
        # Title
        title_text = self.graphics.normal_font.render(f"Stock Information: {stock_data['ticker']}", True, self.graphics.colors['text'])
        self.graphics.screen.blit(title_text, (info_panel_rect.x + 10, info_panel_rect.y + 10))
        
        # Stock data
        y_offset = info_panel_rect.y + 40
        info_lines = [
            f"Volume: {stock_data['volume']:,} | Market Cap: {stock_data['market_cap']:,.0f}",
            f"Volatility: {stock_data['volatility']:.1%} | Beta: {stock_data['beta']:.2f}",
            f"Sentiment Momentum: {stock_data['sentiment']}",
            f"VIX (Volatility Index): {self.game.stock_market.global_volatility:.2f}"
        ]
        
        for line in info_lines:
            text = self.graphics.small_font.render(line, True, self.graphics.colors['text'])
            self.graphics.screen.blit(text, (info_panel_rect.x + 20, y_offset))
            y_offset += 20
            
        # Portfolio value
        portfolio_value = self.game.stock_market.get_portfolio_value()
        portfolio_text = self.graphics.small_font.render(
            f"Portfolio: Cash: {portfolio_value['cash']:.0f} | Stocks: {portfolio_value['stock_value']:.0f} | Total: {portfolio_value['total_value']:.0f} | Daily Change: {portfolio_value['daily_change']:+.0f}",
            True, self.graphics.colors['success'] if portfolio_value['daily_change'] >= 0 else self.graphics.colors['warning']
        )
        self.graphics.screen.blit(portfolio_text, (info_panel_rect.x + 20, y_offset + 10))
    
    def draw_price_chart(self, stock_data, panel_y):
        """Draw price history chart for selected stock"""
        chart_panel_rect = pygame.Rect(30, panel_y+60, 924, 150)
        pygame.draw.rect(self.graphics.screen, (40, 50, 70), chart_panel_rect, border_radius=5)
        pygame.draw.rect(self.graphics.screen, self.graphics.colors['highlight'], chart_panel_rect, 1, border_radius=5)
        
        # Chart title
        chart_title = self.graphics.normal_font.render(f"{stock_data['ticker']} Price History (Last 30 Days)", True, self.graphics.colors['text'])
        self.graphics.screen.blit(chart_title, (chart_panel_rect.x + 10, chart_panel_rect.y + 10))
        
        # Get price history
        price_history = stock_data['price_history']
        if not price_history:
            no_data_text = self.graphics.small_font.render("No price history available", True, self.graphics.colors['text'])
            self.graphics.screen.blit(no_data_text, (chart_panel_rect.x + 20, chart_panel_rect.y + 60))
            return
        
        # Chart area
        chart_rect = pygame.Rect(
            chart_panel_rect.x + 50,
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
        price_range = max(max_price - min_price, 1)
        
        # Draw grid lines
        grid_color = (60, 70, 90)
        
        # Horizontal grid lines
        num_horizontal_lines = 5
        for i in range(num_horizontal_lines):
            price_value = min_price + (i / (num_horizontal_lines - 1)) * price_range
            y = chart_rect.y + chart_rect.height - ((price_value - min_price) / price_range) * chart_rect.height
            pygame.draw.line(self.graphics.screen, grid_color, (chart_rect.x, y), (chart_rect.x + chart_rect.width, y), 1)
            
            # Price labels
            price_text = self.graphics.small_font.render(f"{price_value:.1f}", True, self.graphics.colors['text'])
            self.graphics.screen.blit(price_text, (chart_rect.x - 45, y - 8))
        
        # Vertical grid lines
        num_vertical_lines = min(6, len(price_history))
        for i in range(0, len(price_history), max(1, len(price_history) // num_vertical_lines)):
            x = chart_rect.x + (i / (len(price_history) - 1)) * chart_rect.width if len(price_history) > 1 else chart_rect.x
            pygame.draw.line(self.graphics.screen, grid_color, (x, chart_rect.y), (x, chart_rect.y + chart_rect.height), 1)
            
            # Day labels
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
    
    def buy_stock(self, stock, shares):
        """Buy shares of a stock"""
        success, message = self.game.stock_market.buy_shares(stock, shares)
        self.graphics.show_message(message)
        if success:
            self.custom_amount = ""
            self.input_active = False
    
    def sell_stock(self, stock, shares):
        """Sell shares of a stock"""
        success, message = self.game.stock_market.sell_shares(stock, shares)
        self.graphics.show_message(message)
        if success:
            self.custom_amount = ""
            self.input_active = False
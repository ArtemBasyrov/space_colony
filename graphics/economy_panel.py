import pygame

class EconomyPanel:
    def __init__(self, screen, x, y, width, height):
        self.screen = screen
        self.rect = pygame.Rect(840, 260, 164, 150)
        self.rect = pygame.Rect(x, y, width, height)
 
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
        
        # Add portfolio value if stock market exists
        if hasattr(self.screen.game, 'stock_market'):
            portfolio_data = self.screen.game.stock_market.get_portfolio_value()
            stock_value = portfolio_data['stock_value']
            
            # Calculate percent change (if we have any stocks)
            percent_change = 0
            if stock_value > 0:
                total_cost = sum(trade['total'] for trade in self.screen.game.stock_market.trade_history if trade['action'] == 'buy')
                total_sales = sum(trade['total'] for trade in self.screen.game.stock_market.trade_history if trade['action'] == 'sell')
                net_investment = total_cost - total_sales
                if net_investment > 0:
                    percent_change = ((stock_value - net_investment) / net_investment) * 100
            
            # Render portfolio value in white
            portfolio_text = f"Portfolio: {self.screen.format_number(stock_value)}"
            text_surface = self.screen.graphics.small_font.render(portfolio_text, True, self.screen.graphics.colors['text'])
            self.screen.graphics.screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 100))
            
            # Render percent change in color
            percent_text = f" ({percent_change:+.1f}%)"
            change_color = self.screen.graphics.colors['success'] if percent_change >= 0 else self.screen.graphics.colors['warning']
            percent_surface = self.screen.graphics.small_font.render(percent_text, True, change_color)
            
            # Position percent text right after the portfolio text
            percent_x = self.rect.x + 10 + text_surface.get_width()
            self.screen.graphics.screen.blit(percent_surface, (percent_x, self.rect.y + 100))
        
        # Add construction info if in construction mode (moved down to make room for portfolio)
        if self.screen.game.construction_system.construction_mode and self.screen.game.construction_system.selected_building_type:
            from buildings import get_building_name
            building_type = self.screen.game.construction_system.selected_building_type
            text = self.screen.graphics.small_font.render(f"Placing: {get_building_name(building_type)}", True, self.screen.graphics.colors['success'])
            self.screen.graphics.screen.blit(text, (self.rect.x + 10, self.rect.y + 120))
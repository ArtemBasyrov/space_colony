import random

class Market:
    def __init__(self):
        # Base prices for resources
        self.base_prices = {
            'regolith': 5,
            'food': 8,
            'oxygen': 4,
            'hydrogen': 3,
            'fuel': 10,
        }
        
        # Current market prices
        self.prices = self.base_prices.copy()
        
        # Market volatility (how much prices can change naturally)
        self.volatility = 0.15
        
        # Price history for charts
        self.price_history = {resource: [] for resource in self.base_prices.keys()}
        
        # Market depth - simulates other traders in the market
        self.market_depth = {
            'regolith': 10000,  # Total minerals available in the market
            'food': 5000,        # Total food available in the market
            'oxygen': 8000,
            'hydrogen': 10000,
            'fuel': 3000
        }
        
        # Player influence tracking
        self.player_transactions = {
            'regolith': {'bought': 0, 'sold': 0},
            'food': {'bought': 0, 'sold': 0},
            'oxygen': {'bought': 0, 'sold': 0},
            'hydrogen': {'bought': 0, 'sold': 0},
            'fuel': {'bought': 0, 'sold': 0}
        }
        
        # Market elasticity - how quickly prices respond to player actions
        self.elasticity = {
            'regolith': 0.0002,  # Price change per unit traded
            'food': 0.0003,       # Food is more elastic (prices change faster)
            'oxygen': 0.00025,
            'hydrogen': 0.0002,
            'fuel': 0.00035
        }
        
        # Market recovery rate - how quickly prices return to equilibrium
        self.recovery_rate = 0.1  # 10% recovery per day
        
        # Transaction fees (10% markup for buying, 10% fee for selling)
        self.buy_markup = 1.1  # 10% markup
        self.sell_fee = 0.9    # 10% fee
        
    def update_market(self):
        """Update market prices and record history"""
        # Apply market recovery (prices tend toward equilibrium)
        for resource in self.prices:
            # Calculate price difference from base
            price_diff = self.base_prices[resource] - self.prices[resource]
            # Apply recovery (prices move toward base price)
            self.prices[resource] += price_diff * self.recovery_rate
            
            # Add natural market fluctuations
            natural_change = random.uniform(1 - self.volatility, 1 + self.volatility)
            self.prices[resource] = max(0.01, self.prices[resource] * natural_change)  # Minimum 1% of base price
            
        # Record current prices in history
        for resource in self.prices:
            self.price_history[resource].append(self.prices[resource])
            
        # Keep only the last 30 days of history for performance
        for resource in self.price_history:
            if len(self.price_history[resource]) > 30:
                self.price_history[resource] = self.price_history[resource][-30:]
        
        # Gradually reduce player influence (market forgets past transactions)
        for resource in self.player_transactions:
            self.player_transactions[resource]['bought'] *= 0.9  # Decay by 10% daily
            self.player_transactions[resource]['sold'] *= 0.9
            
    def apply_player_influence(self, resource, amount, is_buying):
        """Apply price changes based on player transactions - EXTREME capitalism edition"""
        if resource not in self.prices:
            return
        
        # Update transaction tracking
        if is_buying:
            self.player_transactions[resource]['bought'] += amount
            # Buying increases demand, which increases prices
            price_impact = amount * self.elasticity[resource]
            self.prices[resource] = self.prices[resource] * (1 + price_impact)
            # No upper limit - prices can go to infinity!
        else:
            self.player_transactions[resource]['sold'] += amount
            # Selling increases supply, which decreases prices
            price_impact = amount * self.elasticity[resource]
            self.prices[resource] = max(self.prices[resource] * (1 - price_impact), 
                                       self.base_prices[resource] * 0.01)  # Floor at 1% of base price
    
    def get_player_influence_factor(self, resource):
        """Calculate how much influence the player has on the market"""
        if resource not in self.player_transactions:
            return 0
        
        total_transactions = (self.player_transactions[resource]['bought'] + 
                             self.player_transactions[resource]['sold'])
        market_size = self.market_depth[resource]
        
        # Influence factor ranges from 0 (no influence) to 1 (complete dominance)
        influence = min(total_transactions / market_size, 1.0)
        return influence
            
    def buy_resource(self, resource, amount, credits):
        if resource not in self.prices:
            return 0, 0
            
        # Calculate cost with 10% markup
        cost = amount * self.prices[resource] * self.buy_markup
        cost = round(cost, 2)
        
        if credits >= cost:
            # Apply player influence to market prices
            self.apply_player_influence(resource, amount, True)
            return amount, cost
        else:
            # Can only buy what you can afford
            affordable_amount = int(credits / (self.prices[resource] * self.buy_markup))
            cost = affordable_amount * self.prices[resource] * self.buy_markup
            cost = round(cost, 2)
            
            if affordable_amount > 0:
                # Apply player influence for the actual purchase
                self.apply_player_influence(resource, affordable_amount, True)
            return affordable_amount, cost
            
    def sell_resource(self, resource, amount, available):
        if resource not in self.prices:
            return 0, 0
            
        # Can't sell more than available
        sellable_amount = min(amount, available)
        revenue = sellable_amount * self.prices[resource] * self.sell_fee  # 10% fee
        revenue = round(revenue, 2)
        
        if sellable_amount > 0:
            # Apply player influence to market prices
            self.apply_player_influence(resource, sellable_amount, False)
        
        return sellable_amount, revenue
        
    def get_tradable_resources(self):
        return list(self.prices.keys())
    
    def get_price_history(self, resource, days=30):
        """Get price history for a resource (last n days)"""
        if resource not in self.price_history:
            return []
        return self.price_history[resource][-days:]
    
    def get_market_info(self, resource):
        """Get information about market state for a resource"""
        if resource not in self.prices:
            return None
            
        influence = self.get_player_influence_factor(resource)
        price_vs_base = self.prices[resource] / self.base_prices[resource]
        
        return {
            'current_price': self.prices[resource],
            'base_price': self.base_prices[resource],
            'price_ratio': price_vs_base,
            'player_influence': influence,
            'market_depth': self.market_depth[resource],
            'buy_markup': self.buy_markup,
            'sell_fee': self.sell_fee
        }
import random
from enum import Enum

class MarketSentiment(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class ResourceIndex:
    def __init__(self, resource_type, base_price):
        self.resource_type = resource_type
        self.ticker = self._generate_ticker(resource_type)
        
        # Price metrics
        self.base_price = base_price
        self.current_price = base_price
        self.previous_close = base_price
        
        # Market metrics
        self.volume = 0
        self.price_history = [base_price]  # Start with base price
        self.volatility = random.uniform(0.08, 0.25)  # 8-25% volatility
        
        # Individual index sentiment and factors
        self.sentiment = MarketSentiment.NEUTRAL
        self.sentiment_momentum = 0
        self.beta = random.uniform(0.7, 1.3)
        self.market_cap = base_price * random.randint(50000, 200000)
        
    def _generate_ticker(self, resource_type):
        """Generate a ticker symbol for the resource index"""
        tickers = {
            'regolith': 'RGLT',
            'food': 'FOOD',
            'oxygen': 'OXYG', 
            'hydrogen': 'HYDR',
            'fuel': 'FUEL'
        }
        return tickers.get(resource_type, resource_type.upper()[:4])
    
    def calculate_commodity_influence(self, commodity_ratio):
        """Calculate how commodity prices influence this index"""
        # Commodity ratio above 1.0 is bullish, below 1.0 is bearish for the resource
        return (commodity_ratio - 1.0) * 0.3  # 30% influence from commodities


class StockMarket:
    def __init__(self, commodity_market, resources):
        self.commodity_market = commodity_market
        self.resources = resources
        self.indices = {}
        self.day = 0
        self.last_update_day = 0
        
        # Player portfolio
        self.player_portfolio = {resource: 0 for resource in ['regolith', 'food', 'oxygen', 'hydrogen', 'fuel']}
        self.trade_history = []
        
        # Global market conditions (affect all indices but to varying degrees)
        self.global_volatility = 0.1
        self.global_trend = 0  # Slight overall market trend
        
        self.pending_news_events = []
        
        self._initialize_indices()
    
    def _initialize_indices(self):
        """Initialize index funds for each resource type"""
        base_prices = {
            'regolith': 45,
            'food': 75, 
            'oxygen': 35,
            'hydrogen': 25,
            'fuel': 90
        }
        
        for resource, base_price in base_prices.items():
            self.indices[resource] = ResourceIndex(resource, base_price)
    
    def update_market(self, game_day):
        """Update stock market for the new day"""
        if game_day == self.last_update_day:
            return
            
        self.day = game_day
        self.last_update_day = game_day
        
        # Update global market conditions
        self._update_global_conditions()
        
        # Update each resource index price with individual sentiment
        for resource, index in self.indices.items():
            self._update_index_sentiment(index)
            self._update_index_price(index)
            
        # Apply any pending news events
        self._apply_pending_news()
        
        # Generate random market events (25% chance per day)
        if random.random() < 0.25:
            self._generate_market_event()
    
    def _update_global_conditions(self):
        """Update overall market conditions that affect all indices"""
        # Global volatility slowly changes
        volatility_change = random.uniform(-0.02, 0.02)
        self.global_volatility = max(0.05, min(0.4, self.global_volatility + volatility_change))
        
        # Global trend has momentum but mean-reverts to zero
        trend_change = random.uniform(-0.01, 0.01)
        self.global_trend = self.global_trend * 0.9 + trend_change * 0.1
    
    def _update_index_sentiment(self, index):
        """Update individual index sentiment based on its specific conditions"""
        sentiment_factors = []
        
        # Factor 1: Commodity price influence (most important)
        commodity_price = self.commodity_market.prices[index.resource_type]
        commodity_base = self.commodity_market.base_prices[index.resource_type]
        commodity_ratio = commodity_price / commodity_base
        commodity_influence = index.calculate_commodity_influence(commodity_ratio)
        sentiment_factors.append(commodity_influence)
        
        # Factor 2: Price momentum (recent performance)
        momentum = self._calculate_price_momentum(index)
        sentiment_factors.append(momentum * 0.4)  # 40% weight to momentum
        
        # Factor 3: Global market influence
        sentiment_factors.append(self.global_trend * index.beta)
        
        # Factor 4: Random noise (affected by volatility)
        noise = random.gauss(0, index.volatility * 0.1)
        sentiment_factors.append(noise)
        
        # Calculate net sentiment
        net_sentiment = sum(sentiment_factors)
        
        # Update sentiment momentum (slower changes)
        index.sentiment_momentum = index.sentiment_momentum * 0.8 + net_sentiment * 0.2
        
        # Determine sentiment
        if index.sentiment_momentum > 0.03:
            index.sentiment = MarketSentiment.BULLISH
        elif index.sentiment_momentum < -0.03:
            index.sentiment = MarketSentiment.BEARISH
        else:
            index.sentiment = MarketSentiment.NEUTRAL
    
    def _calculate_price_momentum(self, index):
        """Calculate price momentum from recent history"""
        if len(index.price_history) < 5:
            return 0
        
        # Use last 5 days for short-term momentum
        recent_prices = index.price_history[-5:]
        price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        # Normalize and cap momentum
        return max(-0.1, min(0.1, price_change * 2))
    
    def _update_index_price(self, index):
        """Update individual resource index price using realistic price movement"""
        # Store previous close
        index.previous_close = index.current_price
        
        # Calculate base price movement from sentiment
        base_movement = 0
        
        if index.sentiment == MarketSentiment.BULLISH:
            base_movement = random.uniform(0.005, 0.03)  # 0.5% to 3% up
        elif index.sentiment == MarketSentiment.BEARISH:
            base_movement = random.uniform(-0.03, -0.005)  # 0.5% to 3% down
        else:  # NEUTRAL
            base_movement = random.uniform(-0.01, 0.01)  # Small random movement
        
        # Apply beta to global conditions
        global_effect = self.global_trend * index.beta
        
        # Volume effect (high volume can amplify moves)
        volume_effect = 0
        if index.volume > 1000:
            volume_effect = (index.volume / 10000) * 0.01  # Small amplification
        
        # Random volatility effect
        volatility_effect = random.gauss(0, index.volatility * self.global_volatility)
        
        # Combine all factors
        total_movement = base_movement + global_effect + volume_effect + volatility_effect
        
        # Apply intelligent mean reversion based on both base price and 30-day average
        if len(index.price_history) >= 10:
            # Calculate 30-day moving average (use available history if less than 30 days)
            days_to_use = min(30, len(index.price_history))
            moving_avg_30 = sum(index.price_history[-days_to_use:]) / days_to_use
            recent_avg_10 = sum(index.price_history[-10:]) / 10
            
            # Calculate deviations from different benchmarks
            deviation_from_base = (index.current_price - index.base_price) / index.base_price
            deviation_from_30day = (index.current_price - moving_avg_30) / moving_avg_30
            deviation_from_10day = (index.current_price - recent_avg_10) / recent_avg_10
            
            # Weight the deviations (30-day average is most important, then base price, then recent)
            total_deviation = (
                deviation_from_30day * 0.5 +      # 50% weight to 30-day average (medium-term)
                deviation_from_base * 0.3 +       # 30% weight to base price (long-term anchor)  
                deviation_from_10day * 0.2        # 20% weight to 10-day average (short-term)
            )
            
            # Apply reversion only for significant deviations (>15% combined deviation)
            if abs(total_deviation) > 0.15:
                # Use a gentle reversion coefficient that scales with deviation size
                reversion_strength = 0.08  # 8% reversion strength at maximum deviation
                
                # Scale reversion based on how far we are from equilibrium
                # More aggressive reversion for larger deviations, gentler for smaller ones
                reversion_factor = reversion_strength * (abs(total_deviation) - 0.15) / 0.85
                
                # Apply reversion in the opposite direction of the deviation
                reversion = -total_deviation * reversion_factor
                
                # Cap maximum daily reversion at 5% to avoid violent corrections
                #reversion = max(-0.05, min(0.05, reversion))
                
                total_movement += reversion
                
                # Additional: If price is extremely overvalued (>50% above base), apply stronger base reversion
                if deviation_from_base > 0.5:
                    base_reversion = -deviation_from_base * 0.02  # Additional 2% pull toward base
                    total_movement += base_reversion
        
        # Ensure reasonable daily movement (-15% to +15% max)
        #total_movement = max(-0.15, min(0.15, total_movement))
        
        # Apply price change
        new_price = index.current_price * (1 + total_movement)
        
        # Ensure absolute minimum price (1% of base)
        new_price = max(new_price, index.base_price * 0.01)
        
        index.current_price = new_price
        
        # Add to price history
        index.price_history.append(new_price)
        if len(index.price_history) > 50:  # Keep more history for better averaging
            index.price_history.pop(0)
        
        # Reset daily volume
        index.volume = 0
    
    def _generate_market_event(self):
        """Generate random market events"""
        event_types = [
            ("supply_news", "Supply chain developments affect {resource} market", 0.08),
            ("demand_news", "Demand shifts in {resource} sector", 0.10),
            ("tech_news", "Technological breakthrough impacts {resource}", 0.06),
            ("regulation", "New regulations affect {resource} industry", 0.07),
        ]
        
        event_type, message_template, base_impact = random.choice(event_types)
        
        # 80% chance affects specific resource, 20% affects all
        if random.random() < 0.8:
            affected_resource = random.choice(list(self.indices.keys()))
            impact = base_impact * random.choice([-1, 1])
            message = message_template.format(resource=affected_resource.capitalize())
        else:
            affected_resource = "all"
            impact = base_impact * 0.3 * random.choice([-1, 1])  # Smaller broad impact
            message = "Market-wide " + message_template.format(resource="prices")
        
        # Adjust impact based on volatility
        impact *= (1 + self.global_volatility)
        
        self.pending_news_events.append({
            'type': event_type,
            'message': message,
            'impact': impact,
            'affected_resource': affected_resource,
            'day': self.day + 1
        })
    
    def _apply_pending_news(self):
        """Apply news events scheduled for today"""
        events_to_apply = [event for event in self.pending_news_events if event['day'] == self.day]
        
        for event in events_to_apply:
            if event['affected_resource'] == 'all':
                for index in self.indices.values():
                    # Apply with some variation
                    variation = random.uniform(0.8, 1.2)
                    index.current_price *= (1 + event['impact'] * variation)
            else:
                if event['affected_resource'] in self.indices:
                    index = self.indices[event['affected_resource']]
                    index.current_price *= (1 + event['impact'])
            
            self.pending_news_events.remove(event)
    
    def buy_shares(self, resource, shares):
        """Buy shares of a resource index"""
        if resource not in self.indices:
            return False, "Invalid resource"
        
        index = self.indices[resource]
        total_cost = shares * index.current_price
        
        if total_cost > self.resources.credits:
            return False, "Insufficient credits"
        
        if shares <= 0:
            return False, "Invalid share amount"
        
        # Execute trade
        self.resources.credits -= total_cost
        self.player_portfolio[resource] += shares
        index.volume += shares  # Add to today's volume
        
        self.trade_history.append({
            'day': self.day,
            'action': 'buy',
            'resource': resource,
            'shares': shares,
            'price': index.current_price,
            'total': total_cost
        })
        
        return True, f"Bought {shares} shares of {index.ticker} at {index.current_price:.2f} credits"
    
    def sell_shares(self, resource, shares):
        """Sell shares of a resource index"""
        if resource not in self.indices:
            return False, "Invalid resource"
        
        if self.player_portfolio[resource] < shares:
            return False, "Insufficient shares"
        
        index = self.indices[resource]
        
        if shares <= 0:
            return False, "Invalid share amount"
        
        total_value = shares * index.current_price
        self.resources.credits += total_value
        self.player_portfolio[resource] -= shares
        index.volume += shares
        
        self.trade_history.append({
            'day': self.day,
            'action': 'sell',
            'resource': resource,
            'shares': shares,
            'price': index.current_price,
            'total': total_value
        })
        
        return True, f"Sold {shares} shares of {index.ticker} at {index.current_price:.2f} credits"
    
    def get_portfolio_value(self):
        """Calculate total portfolio value"""
        stock_value = 0
        for resource, shares in self.player_portfolio.items():
            if shares > 0 and resource in self.indices:
                stock_value += shares * self.indices[resource].current_price
        
        portfolio_value = self.resources.credits + stock_value
        
        return {
            'cash': self.resources.credits,
            'stock_value': stock_value,
            'total_value': portfolio_value,
            'daily_change': self._calculate_daily_portfolio_change()
        }
    
    def _calculate_daily_portfolio_change(self):
        """Calculate daily change in portfolio value from price movements only"""
        if not self.trade_history:
            return 0
        
        daily_change = 0
        for resource, shares in self.player_portfolio.items():
            if shares > 0 and resource in self.indices:
                index = self.indices[resource]
                price_change = index.current_price - index.previous_close
                daily_change += price_change * shares

        return daily_change
    
    def get_market_data(self, resource):
        """Get market data for a resource index"""
        if resource not in self.indices:
            return None
        
        index = self.indices[resource]
        price_change = index.current_price - index.previous_close
        percent_change = (price_change / index.previous_close) * 100 if index.previous_close > 0 else 0
        
        return {
            'ticker': index.ticker,
            'resource': resource.capitalize(),
            'current_price': index.current_price,
            'previous_close': index.previous_close,
            'change': price_change,
            'percent_change': percent_change,
            'volume': index.volume,
            'sentiment': index.sentiment.value,
            'volatility': index.volatility,
            'price_history': index.price_history[-30:],
            'market_cap': index.market_cap,
            'beta': index.beta
        }
    
    def get_all_indices(self):
        """Get data for all resource indices"""
        return {resource: self.get_market_data(resource) for resource in self.indices.keys()}
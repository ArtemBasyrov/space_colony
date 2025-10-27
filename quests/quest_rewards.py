# [file name]: quest_rewards.py
# [file content begin]
def grant_resources(resource_type: str, amount: int):
    """Reward that grants resources - returns dictionary"""
    return {
        "type": "grant_resources",
        "resource_type": resource_type,
        "amount": amount,
        "description": f"Receive {amount} {resource_type}"
    }

def unlock_building(building_class):
    """Reward that unlocks a new building type - returns dictionary"""
    building_instance = building_class()
    return {
        "type": "unlock_building", 
        "building_class": building_class,
        "building_name": building_instance.name,
        "description": f"Unlock {building_instance.name} building"
    }

def modify_market_price(resource_type: str, modifier: float):
    """Reward that modifies market prices - returns dictionary"""
    direction = "increase" if modifier > 1 else "decrease"
    change = abs(modifier - 1) * 100
    if resource_type == "all":
        description = f"{direction.capitalize()} all market prices by {change:.1f}%"
    else:
        description = f"{direction.capitalize()} {resource_type} market prices by {change:.1f}%"
    
    return {
        "type": "modify_market_price",
        "resource_type": resource_type,
        "modifier": modifier,
        "description": description
    }

def grant_population_bonus(bonus_count: int):
    """Reward that adds population - returns dictionary"""
    return {
        "type": "grant_population_bonus",
        "bonus_count": bonus_count,
        "description": f"Gain {bonus_count} new colonists"
    }

def reduce_market_fees(buy_reduction: float = 0.0, sell_improvement: float = 0.0):
    """Reward that reduces market transaction fees - returns dictionary"""
    parts = []
    if buy_reduction > 0:
        parts.append(f"buy fees -{buy_reduction*100:.1f}%")
    if sell_improvement > 0:
        parts.append(f"sell fees +{sell_improvement*100:.1f}%")
    
    description = f"Market: {', '.join(parts)}" if parts else "Market fee reduction"
    
    return {
        "type": "reduce_market_fees",
        "buy_reduction": buy_reduction,
        "sell_improvement": sell_improvement,
        "description": description
    }

def grant_shares(resource_type: str, shares: int):
    """Reward that grants stock market shares - returns dictionary"""
    return {
        "type": "grant_shares",
        "resource_type": resource_type,
        "shares": shares,
        "description": f"Receive {shares} shares of {resource_type.upper()}"
    }

def unlock_advanced_building():
    """Reward that unlocks advanced buildings - returns dictionary"""
    return {
        "type": "unlock_advanced_building",
        "description": "Unlock advanced buildings"
    }

def permanent_production_boost(building_type, multiplier: float):
    """Reward that permanently boosts production of a building type - returns dictionary"""
    building_instance = building_type()
    boost = (multiplier - 1) * 100
    return {
        "type": "permanent_production_boost",
        "building_type": building_type,
        "multiplier": multiplier,
        "description": f"{building_instance.name} production +{boost:.1f}%"
    }

# NEW: Function to execute rewards based on their dictionary definition
def execute_reward(reward_dict, game):
    """Execute a reward based on its dictionary definition"""
    reward_type = reward_dict["type"]
    
    if reward_type == "grant_resources":
        resource_type = reward_dict["resource_type"]
        amount = reward_dict["amount"]
        current = getattr(game.resources, resource_type, 0)
        setattr(game.resources, resource_type, current + amount)
        
        if hasattr(game, 'graphics'):
            game.graphics.show_message(f"Quest Reward: +{amount} {resource_type}")
    
    elif reward_type == "unlock_building":
        building_class = reward_dict["building_class"]
        building_name = building_class.__name__
        if game.construction_system.unlock_building(building_name):
            if hasattr(game, 'graphics'):
                building_instance = building_class()
                game.graphics.show_message(f"New Building Unlocked: {building_instance.name}")
            return True
        return False
    
    elif reward_type == "modify_market_price":
        resource_type = reward_dict["resource_type"]
        modifier = reward_dict["modifier"]
        
        if resource_type == "all":
            for resource in game.market.base_prices.keys():
                game.market.modify_base_price(resource, modifier)
            message = f"All market prices modified by {modifier:.1%}"
        else:
            game.market.modify_base_price(resource_type, modifier)
            message = f"{resource_type} market price modified by {modifier:.1%}"
        
        if hasattr(game, 'graphics'):
            game.graphics.show_message(f"Quest Reward: {message}")
    
    elif reward_type == "grant_population_bonus":
        bonus_count = reward_dict["bonus_count"]
        old_count = game.population.count
        for _ in range(bonus_count):
            if not game.population.add_colonist():
                break  # Stop if population cap reached
        
        new_count = game.population.count
        actual_bonus = new_count - old_count
        
        if hasattr(game, 'graphics') and actual_bonus > 0:
            game.graphics.show_message(f"Quest Reward: +{actual_bonus} new colonists arrived!")
    
    elif reward_type == "reduce_market_fees":
        buy_reduction = reward_dict["buy_reduction"]
        sell_improvement = reward_dict["sell_improvement"]
        
        new_buy_modifier = 1.0 - buy_reduction
        new_sell_modifier = 1.0 + sell_improvement
        
        game.market.modify_market_fees(
            buy_modifier=new_buy_modifier,
            sell_modifier=new_sell_modifier
        )
        
        message_parts = []
        if buy_reduction > 0:
            message_parts.append(f"buy fees reduced by {buy_reduction:.1%}")
        if sell_improvement > 0:
            message_parts.append(f"sell fees improved by {sell_improvement:.1%}")
            
        if message_parts and hasattr(game, 'graphics'):
            game.graphics.show_message(f"Quest Reward: Market {', '.join(message_parts)}")
    
    elif reward_type == "grant_shares":
        resource_type = reward_dict["resource_type"]
        shares = reward_dict["shares"]
        
        if hasattr(game, 'stock_market'):
            current_shares = game.stock_market.player_portfolio.get(resource_type, 0)
            game.stock_market.player_portfolio[resource_type] = current_shares + shares
            
            if resource_type in game.stock_market.indices:
                ticker = game.stock_market.indices[resource_type].ticker
            else:
                ticker = resource_type.upper()
                
            if hasattr(game, 'graphics'):
                game.graphics.show_message(f"Quest Reward: Received {shares} shares of {ticker}")
    
    elif reward_type == "unlock_advanced_building":
        # This would unlock buildings not in the initial catalog
        advanced_buildings = {
            "AdvancedMine": 2000,
            "ResearchLab": 1500,
        }
        
        for building_name, price in advanced_buildings.items():
            game.construction_system.unlock_building(building_name)
            
        if hasattr(game, 'graphics'):
            game.graphics.show_message("Quest Reward: Advanced buildings unlocked!")
    
    elif reward_type == "permanent_production_boost":
        building_type = reward_dict["building_type"]
        multiplier = reward_dict["multiplier"]
        
        for building in game.buildings:
            if isinstance(building, building_type):
                if hasattr(building, 'production_boost'):
                    building.production_boost *= multiplier
                else:
                    building.production_boost = multiplier
                    
        if hasattr(game, 'graphics'):
            building_instance = building_type()
            game.graphics.show_message(f"Quest Reward: {building_instance.name} production +{multiplier:.1%}")

# NEW: Function to get reward description from dictionary
def get_reward_description(reward_dict):
    """Get description from reward dictionary"""
    return reward_dict.get("description", "Unknown reward")
# [file content end]
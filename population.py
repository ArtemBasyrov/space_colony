# population.py
import random
from colonist import Colonist
from events import EventType, GameEvent

class Population:
    def __init__(self, game=None):
        self.game = game
        self.colonists = []  # Individual colonists
        self.max_population = 1000  # Population cap
        self.next_colonist_id = 1
        self.base_wage = 6  # Default base wage for new assignments
        
        # Initialize starting population
        for i in range(10):
            self.add_colonist()
            
    def add_colonist(self):
        """Add a new colonist if under population cap"""
        if len(self.colonists) >= self.max_population:
            return False
            
        colonist = Colonist(self.next_colonist_id)
        self.next_colonist_id += 1
        self.colonists.append(colonist)
        return True
        
    def remove_colonist(self, colonist):
        """Remove a colonist from the population"""
        if colonist in self.colonists:
            # Remove from workplace if employed
            if colonist.workplace and colonist in colonist.workplace.assigned_colonists:
                colonist.workplace.assigned_colonists.remove(colonist)
                colonist.workplace.assigned_workers -= 1
                
            self.colonists.remove(colonist)
            return True
        return False
        
    @property
    def count(self):
        return len(self.colonists)
        
    @property
    def employed_colonists(self):
        return [c for c in self.colonists if c.employed]
        
    @property
    def unemployed_colonists(self):
        return [c for c in self.colonists if not c.employed]
        
    @property
    def available_workers(self):
        return len(self.unemployed_colonists)
        
    @property
    def employed_workers(self):
        return len(self.employed_colonists)
        
    def calculate_average_happiness(self):
        if not self.colonists:
            return 50
        return sum(c.happiness for c in self.colonists) / len(self.colonists)
        
    def calculate_average_health(self):
        if not self.colonists:
            return 80
        return sum(c.health for c in self.colonists) / len(self.colonists)
        
    def calculate_total_wages(self):
        employed = self.employed_colonists
        if not employed:
            return 0
        return sum(c.wage for c in employed)
        
    def calculate_average_wage(self):
        """Calculate the average wage of employed colonists"""
        employed = self.employed_colonists
        if not employed:
            return 0
        return sum(c.wage for c in employed) / len(employed)
        
    def set_wage_for_all(self, new_wage):
        """Set the same wage for all employed colonists"""
        changed_count = 0
        for colonist in self.employed_colonists:
            if colonist.set_wage(new_wage):
                changed_count += 1
        return changed_count
        
    def set_wage_for_building(self, building, new_wage):
        """Set wage for all colonists in a specific building"""
        changed_count = 0
        for colonist in building.assigned_colonists:
            if colonist.set_wage(new_wage):
                changed_count += 1
        return changed_count
        
    def set_wage_for_colonist(self, colonist_id, new_wage):
        """Set wage for a specific colonist"""
        for colonist in self.colonists:
            if colonist.id == colonist_id and colonist.employed:
                return colonist.set_wage(new_wage)
        return False
        
    def update_employment(self, buildings):
        """Update employment status based on available buildings"""
        # First, unassign colonists from destroyed buildings
        for colonist in self.employed_colonists:
            if colonist.workplace and colonist.workplace not in buildings:
                colonist.unassign_from_workplace()
                
        # Count current assignments
        for building in buildings:
            building.assigned_colonists = [c for c in self.colonists if c.workplace == building]
            building.assigned_workers = len(building.assigned_colonists)
        
    def update_housing(self, buildings):
        """Update housing for all colonists"""
        # Get all habitat buildings
        habitats = [b for b in buildings if hasattr(b, 'residents')]
        
        # Update housing for each colonist
        for colonist in self.colonists:
            colonist.update_housing_situation(habitats)
            
    def get_homeless_count(self):
        """Get number of homeless colonists"""
        return sum(1 for c in self.colonists if not c.housing)
        
    def get_housed_count(self):
        """Get number of housed colonists"""
        return sum(1 for c in self.colonists if c.housing)
        
    def get_available_housing(self, buildings):
        """Get total available housing capacity"""
        habitats = [b for b in buildings if hasattr(b, 'residents')]
        return sum(h.get_vacancy_count() for h in habitats)
        
    def get_total_housing_capacity(self, buildings):
        """Get total housing capacity"""
        habitats = [b for b in buildings if hasattr(b, 'residents')]
        return sum(h.capacity for h in habitats)

    def update(self, resources, buildings):
        """Update all colonists and handle population changes"""
        # Update housing first
        self.update_housing(buildings)
        self.update_employment(buildings)
        self.update_health(buildings)
        
        # Check for critical resource shortages
        oxygen_shortage = resources.oxygen <= 0
        food_shortage = resources.food <= 0
        severe_shortage = oxygen_shortage or food_shortage
        
        # Update each colonist
        for colonist in self.colonists:
            colonist.update(self.game)
            
            # Apply resource shortage effects
            if severe_shortage:
                colonist.health -= 2  # Rapid health decline
                colonist.happiness -= 5  # Severe unhappiness
        
        # Calculate and pay wages
        total_wages = self.calculate_total_wages()
        if resources.credits >= total_wages:
            resources.credits -= total_wages
        else:
            # Can't pay full wages - severe happiness penalty
            unpaid_ratio = (total_wages - resources.credits) / total_wages
            for colonist in self.employed_colonists:
                colonist.happiness -= 20 * unpaid_ratio
                colonist.debt += colonist.wage * unpaid_ratio  # Add unpaid wages to debt
            resources.credits = 0
            
        # Population changes based on happiness, health, and resource availability
        avg_happiness = self.calculate_average_happiness()
        avg_health = self.calculate_average_health()
        
        birth_chance = 0
        death_chance = 0
        leave_chance = 0
        
        # Birth chance - only if conditions are good
        if (avg_happiness > 70 and 
            resources.food > self.count * 2 and 
            resources.oxygen > self.count * 0.5 and
            avg_health > 60):
            birth_chance = 0.3
        
        # Death chance - increased by resource shortages
        if severe_shortage:
            death_chance = 0.6  # Very high chance of death during shortages
        elif avg_health < 20:
            death_chance = 0.4
        elif avg_health < 40:
            death_chance = 0.2
            
        # Handle births
        if birth_chance > 0 and random.random() < birth_chance and self.count < self.max_population:
            if self.add_colonist():
                if self.game:
                    self.game.event_manager.publish(GameEvent(
                        EventType.POPULATION_INCREASE,
                        "Population increased! A new colonist has arrived.",
                        {"new_count": self.count}
                    ))
            
        # Handle deaths
        dead_colonists = []
        for colonist in self.colonists[:]:  # Copy list for safe iteration
            death_roll = random.random()
            if death_roll < death_chance:
                dead_colonists.append(colonist)
                
        # Remove dead colonists
        for colonist in dead_colonists:
            self.remove_colonist(colonist)
            if self.game:
                self.game.event_manager.publish(GameEvent(
                    EventType.POPULATION_DECREASE,
                    "A colonist has died due to poor conditions.",
                    {"new_count": self.count}
                ))
        
        # Handle colonists leaving
        leaving_colonists = []
        leave_chance = 0.3
        for colonist in self.colonists[:]:
            if (colonist.happiness < 20 and 
                colonist.debt > 50 and 
                random.random() < leave_chance):
                leaving_colonists.append(colonist)
                
        # Remove leaving colonists
        for colonist in leaving_colonists:
            self.remove_colonist(colonist)
            if self.game:
                self.game.event_manager.publish(GameEvent(
                    EventType.POPULATION_DECREASE,
                    "A colonist has left the colony due to unhappiness and debt.",
                    {"new_count": self.count}
                ))
        
        # Ensure values are within bounds
        for colonist in self.colonists:
            colonist.happiness = max(0, min(100, colonist.happiness))
            colonist.health = max(0, min(100, colonist.health))

    def update_health(self, buildings):
        """Apply health boosts from hospital"""
        for building in buildings:
            if hasattr(building, 'calculate_health_boost'):
                health_boost = building.calculate_health_boost()

                for c in self.colonists:
                    c.health = min(100, c.health + health_boost)
# colonist.py
import random

class Colonist:
    def __init__(self, id):
        self.id = id
        self.health = random.randint(70, 90)
        self.happiness = random.randint(40, 60)
        self.employed = False
        self.workplace = None
        self.wage = 0
        self.savings = 0
        self.debt = 0
        self.days_unemployed = 0
        self.days_homeless = 0  # Track homelessness duration
        self.living_cost = 1.0
        self.housing = None  # Reference to HabitatBlock if housed
        self.housing_quality = 0  # Quality of current housing
        self.rent_cost = 0  # Current rent payment
        
    def calculate_living_cost(self):
        """Calculate individual cost of living including rent"""
        base_cost = self.living_cost + (self.debt * 0.01)
        if self.housing:
            base_cost += self.rent_cost
        return base_cost
        
    def can_afford_rent(self):
        """Check if colonist can afford their current rent"""
        if not self.housing:
            return False
        return self.savings + self.wage >= self.rent_cost

    def calculate_housing_happiness(self):
        """Calculate happiness effect from housing"""
        if self.housing:
            # Check if living in slums
            is_slum = hasattr(self.housing, 'is_slum')
            
            if is_slum:
                # Significant penalty for living in slums
                slum_penalty = -10  # Base penalty for slum living                
                return slum_penalty
            else:
                # Regular housing calculation
                housing_happiness = self.housing_quality * 3  # 3 happiness per quality point
                
                # Rent burden penalty (only if rent is significant portion of wage)
                if self.wage > 0:
                    rent_ratio = self.rent_cost / self.wage
                    if rent_ratio > 0.3:  # Only penalize if rent is more than 30% of wage
                        rent_burden = (rent_ratio - 0.3) * 15  # Moderate penalty
                    else:
                        rent_burden = 0
                else:
                    rent_burden = 5  # Small penalty if unemployed with housing costs
                
                return housing_happiness - rent_burden
        else:
            # Homelessness penalty
            return -15 - (self.days_homeless * 0.5)

    def update_housing_situation(self, available_housing):
        """Update housing status - find new housing or check affordability"""
        # Check if currently housed but can't afford it
        if self.housing and not self.can_afford_rent():
            self.housing.remove_resident(self)
            self.housing = None
            self.housing_quality = 0
            self.rent_cost = 0
            return False
        
        # Separate slums from other housing
        slums = [h for h in available_housing if hasattr(h, 'is_slum') and h.is_slum]
        regular_housing = [h for h in available_housing if not hasattr(h, 'is_slum') or not h.is_slum]
        
        # If homeless, first try to find any affordable regular housing
        if not self.housing:
            best_habitat = None
            for habitat in regular_housing:
                if (habitat.get_vacancy_count() > 0 and 
                    self.can_afford_housing(habitat.rent) and 
                    habitat.quality > self.housing_quality):
                    
                    # Found a better option than current best
                    if not best_habitat or habitat.quality > best_habitat.quality:
                        best_habitat = habitat
            
            # If found affordable regular housing, move there
            if best_habitat:
                if best_habitat.add_resident(self):
                    self.housing = best_habitat
                    self.housing_quality = best_habitat.quality
                    self.rent_cost = best_habitat.rent
                    return True
            
            # If no affordable regular housing, try slums (no affordability check for slums)
            for slum in slums:
                if slum.get_vacancy_count() > 0 and slum.quality > self.housing_quality:
                    if slum.add_resident(self):
                        self.housing = slum
                        self.housing_quality = slum.quality
                        self.rent_cost = slum.rent
                        return True
        
        # If already housed, look for upgrades to better housing (regular only)
        else:
            best_habitat = None
            for habitat in regular_housing:
                if (habitat.get_vacancy_count() > 0 and 
                    self.can_afford_housing(habitat.rent) and 
                    habitat.quality > self.housing_quality):
                    
                    # Found a better option than current best
                    if not best_habitat or habitat.quality > best_habitat.quality:
                        best_habitat = habitat
            
            # If found better housing, move there
            if best_habitat:
                # Leave current housing
                self.housing.remove_resident(self)
                
                # Move to new housing
                if best_habitat.add_resident(self):
                    self.housing = best_habitat
                    self.housing_quality = best_habitat.quality
                    self.rent_cost = best_habitat.rent
                    return True
        
        return False

    def can_afford_housing(self, rent):
        """Simple check if colonist can afford housing rent"""
        if not self.employed:
            return False

        return self.wage >= (rent + self.living_cost)
        
    def calculate_wage_satisfaction(self):
        """Calculate how satisfied this colonist is with their wage"""
        living_cost = self.calculate_living_cost()
        if self.wage <= living_cost:
            return -20  # Can't afford basic living
        elif self.wage <= living_cost * 1.5:
            return 0  # Satisfactory
        elif self.wage <= living_cost * 2:
            return 10    # Comfortable
        else:
            return 20    # Well-off
            
    def update(self, game_state):
        """Update colonist status daily"""
        # Update homelessness counter
        if not self.housing:
            self.days_homeless += 1
        else:
            self.days_homeless = 0
            
        # Calculate happiness factors
        wage_satisfaction = self.calculate_wage_satisfaction()
        employment_factor = 0 if self.employed else -5
        housing_happiness = self.calculate_housing_happiness()
        
        # Unemployment penalty increases over time
        unemployment_penalty = min(20, self.days_unemployed * 0.5)
        
        # Debt causes stress
        debt_penalty = min(15, self.debt * 0.1)
        
        # Health affects happiness
        health_factor = (self.health - 50) / 10
        
        # Update happiness with housing effect
        self.happiness += (wage_satisfaction + employment_factor + housing_happiness - 
                          unemployment_penalty - debt_penalty + health_factor)
        self.happiness = max(0, min(100, self.happiness))
        
        # Update health (basic decay for now)
        self.health -= 0.1
        if self.health < 30:
            self.health -= 0.5  # Faster decay when very unhealthy
            
        # Track unemployment
        if not self.employed:
            self.days_unemployed += 1
        else:
            self.days_unemployed = 0
            
        # Pay living costs including rent
        living_cost = self.calculate_living_cost()
        if self.savings >= living_cost:
            self.savings -= living_cost
        else:
            self.debt += living_cost - self.savings
            self.savings = 0
            
        # Receive wage if employed
        if self.employed and self.wage > 0:
            self.savings += self.wage
            
    def assign_to_workplace(self, building, wage=None):
        """Assign this colonist to a workplace with optional custom wage"""
        self.workplace = building
        self.employed = True
        if wage is not None:
            self.wage = wage
        else:
            self.wage = building.base_wage  # Use building's base wage if not specified
            
    def unassign_from_workplace(self):
        """Remove this colonist from their workplace"""
        self.workplace = None
        self.employed = False
        self.wage = 0
        
    def set_wage(self, new_wage):
        """Set a new wage for this colonist"""
        if self.employed:
            self.wage = new_wage
            return True
        return False
from professions import PROFESSIONS, get_profession_for_building, get_profession_default_wage

# buildings.py - update the Building class
class Building:
    def __init__(self, name, description, max_workers, energy_consumption=0, mineral_consumption=0, 
                 required_surface=None, area_of_effect_radius=0, profession='worker'):  # Add profession parameter
        self.name = name
        self.description = description
        self.max_workers = max_workers
        self.assigned_workers = 0
        self.assigned_colonists = []  # Track individual colonists
        self.energy_consumption = energy_consumption
        self.mineral_consumption = mineral_consumption
        self.required_surface = required_surface  # None for any surface, or specific surface type
        self.active = True
        self.profession = profession  # Use parameter
        self.base_wage = get_profession_default_wage(self.profession)  # Base wage for all workers
        self.crime_level = 0  # 0-100 crime level
        self.crime_resistance = 1.0  # Resistance to crime (higher = less affected)
        self.is_crime_source = False
        self.area_of_effect_radius = area_of_effect_radius  # New: radius in hexes for area effects
        self.hex_position = None  # New: store which hex this building is placed on
        
    def can_be_placed_on(self, hexagon):
        """Check if building can be placed on this hexagon type"""
        if self.required_surface is None:
            return True
        return hexagon.surface_type == self.required_surface
    
    def set_hex_position(self, hex_x, hex_y):
        """Set the hex grid position for area of effect calculations"""
        self.hex_position = (hex_x, hex_y)
        
    def get_area_of_effect_hexes(self, hex_map):
        """Get all hexes within the area of effect radius using proper hex grid flood fill"""
        if not self.hex_position or self.area_of_effect_radius == 0:
            return []
            
        # Use hex_map's methods for distance and accessibility
        return hex_map.get_area_of_effect_hexes(self.hex_position, self.area_of_effect_radius)
        
    def assign_colonist(self, colonist, wage=None):
        """Assign a colonist to this building with optional custom wage"""
        if len(self.assigned_colonists) < self.max_workers:
            self.assigned_colonists.append(colonist)
            self.assigned_workers = len(self.assigned_colonists)

            if wage is None:
                wage = self.base_wage
            colonist.assign_to_workplace(self, wage)
            return True
        return False
        
    def remove_colonist(self, colonist):
        """Remove a colonist from this building"""
        if colonist in self.assigned_colonists:
            self.assigned_colonists.remove(colonist)
            self.assigned_workers = len(self.assigned_colonists)
            colonist.unassign_from_workplace()
            return True
        return False
        
    def calculate_production(self):
        """Calculate production based on assigned workers"""
        if not self.active:
            return {}
            
        return {}
        
    def calculate_consumption(self):
        """Calculate consumption based on assigned workers"""
        consumption = {
            'energy': self.energy_consumption * (self.assigned_workers / max(1, self.max_workers)),
            'regolith': self.mineral_consumption * (self.assigned_workers / max(1, self.max_workers))
        }
        return consumption
    
    # buildings.py - add this method to the Building class
    def can_operate(self, resource_manager):
        """Check if this building has enough resources to operate"""
        consumption = self.calculate_consumption()
        for resource, amount in consumption.items():
            if amount > 0 and getattr(resource_manager, resource, 0) < amount:
                return False
        return True
    
    def update_crime(self, game):
        """Update crime level based on unhappy colonists"""
        # Base crime decay
        self.crime_level = max(0, self.crime_level - 2)
        
        # Generate crime from unhappy workers
        if hasattr(self, 'assigned_colonists') and self.assigned_colonists:
            unhappy_workers = [c for c in self.assigned_colonists if c.happiness < 40]
            if unhappy_workers:
                # More unhappy workers = more crime
                crime_generated = len(unhappy_workers) * 2
                self.crime_level = min(100, self.crime_level + crime_generated)
                self.is_crime_source = True
        
        # Generate crime from unhappy residents
        if hasattr(self, 'residents') and self.residents:
            unhappy_residents = [c for c in self.residents if c.happiness < 40]
            if unhappy_residents:
                crime_generated = len(unhappy_residents) * 3  # Residents generate more crime
                self.crime_level = min(100, self.crime_level + crime_generated)
                self.is_crime_source = True
                
        # Slums always generate crime
        if hasattr(self, 'is_slum') and self.is_slum:
            crime_generated = 8  # Constant crime from slums
            self.crime_level = min(100, self.crime_level + crime_generated)
            self.is_crime_source = True
            
    def get_crime_penalty(self):
        """Get the productivity/quality penalty from crime"""
        return max(0, self.crime_level * 0.01)  # 1% penalty per crime point
    
    def calculate_effective_production(self, resource_manager):
        """Apply crime penalty to production"""
        if not self.can_operate(resource_manager):
            return {}
        else:
            base_production = self.calculate_production()
        
        if not base_production:
            return {}
            
        # Apply crime penalty (up to 100% reduction at 100 crime)
        crime_penalty = 1.0 - self.get_crime_penalty()
        
        penalized_production = {}
        for resource, amount in base_production.items():
            penalized_production[resource] = amount * crime_penalty
            
        return penalized_production


class Mine(Building):
    def __init__(self):
        super().__init__(
            name="Regolith Mine",
            description="Extracts raw regolith from earth. Requires energy.",
            max_workers=20,
            energy_consumption=5,
            required_surface="regolith",
            profession=get_profession_for_building('Mine'),
        )
        self.production_rate = 2.0  # Raw regolith per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'regolith': self.assigned_workers * self.production_rate
        }

class EnergyGenerator(Building):
    def __init__(self):
        super().__init__(
            name="Fusion Reactor",
            description="Generates energy. Requires fuel.",
            max_workers=10,
            mineral_consumption=0,  # Now uses fuel instead of minerals
            energy_consumption=0,
            profession=get_profession_for_building('EnergyGenerator')
        )
        self.fuel_consumption = 3  # New fuel consumption
        self.production_rate = 4.0  # Energy per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'energy': self.assigned_workers * self.production_rate
        }
        
    def calculate_consumption(self):
        """Override consumption to include fuel"""
        consumption = super().calculate_consumption()
        consumption['fuel'] = self.fuel_consumption * (self.assigned_workers / max(1, self.max_workers))
        return consumption

class OxygenGenerator(Building):
    def __init__(self):
        super().__init__(
            name="Oxygen Synthesizer",
            description="Produces breathable oxygen. Requires energy.",
            max_workers=8,
            energy_consumption=4,
            profession=get_profession_for_building('OxygenGenerator')
        )
        self.production_rate = 3.0  # Oxygen per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'oxygen': self.assigned_workers * self.production_rate
        }

class HydroponicFarm(Building):
    def __init__(self):
        super().__init__(
            name="Hydroponic Farm",
            description="Grows food. Requires significant energy.",
            max_workers=15,
            energy_consumption=8,
            profession=get_profession_for_building('HydroponicFarm')
        )
        self.production_rate = 2.5  # Food per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'food': self.assigned_workers * self.production_rate
        }

class IceExtractor(Building):
    def __init__(self):
        super().__init__(
            name="Ice Extractor",
            description="Extracts oxygen and hydrogen from ice deposits. Requires energy.",
            max_workers=12,
            energy_consumption=6,
            required_surface="ice",
            profession=get_profession_for_building('IceExtractor')
        )
        self.oxygen_production_rate = 2.0  # Oxygen per worker
        self.hydrogen_production_rate = 1.5  # Hydrogen per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'oxygen': self.assigned_workers * self.oxygen_production_rate,
            'hydrogen': self.assigned_workers * self.hydrogen_production_rate
        }

class ChemicalProcessingPlant(Building):
    def __init__(self):
        super().__init__(
            name="Chemical Processing Plant",
            description="Converts hydrogen into fuel. Requires energy.",
            max_workers=8,
            energy_consumption=4,
            profession=get_profession_for_building('ChemicalProcessingPlant')
        )
        self.hydrogen_consumption = 2  # Hydrogen consumed per worker
        self.production_rate = 1.0  # Fuel produced per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'fuel': self.assigned_workers * self.production_rate
        }
        
    def calculate_consumption(self):
        """Override consumption to include hydrogen"""
        consumption = super().calculate_consumption()
        consumption['hydrogen'] = self.hydrogen_consumption * (self.assigned_workers / max(1, self.max_workers))
        return consumption

class SolarPanelArray(Building):
    def __init__(self):
        super().__init__(
            name="Solar Panel Array",
            description="Generates energy from sunlight. No workers required.",
            max_workers=0,  # No workers needed
            energy_consumption=0
        )
        self.production_rate = 10.0  # Energy production (not based on workers)
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'energy': self.production_rate  # Constant production, no workers
        }
        
    def calculate_consumption(self):
        """No consumption for solar panels"""
        return {}

# buildings.py - update the Hospital class
class Hospital(Building):
    def __init__(self):
        super().__init__(
            name="Hospital",
            description="Improves population health. Requires energy and raw regolith.",
            max_workers=6,
            energy_consumption=6,
            mineral_consumption=2,
            profession=get_profession_for_building('Hospital')
        )
        self.production_rate = 3.0  # Health points per worker
        self.max_capacity = 30  # Maximum colonists one hospital can effectively serve when fully staffed
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        # Hospital doesn't produce resources, but improves health
        return {}
        
    def calculate_health_boost(self, total_population):
        """Calculate health boost based on assigned workers and population served"""
        if not self.active:
            return 0
            
        # Base health production from workers
        base_health_production = self.assigned_workers * self.production_rate
        
        # Calculate the effective capacity based on staffing level
        # Fully staffed (6 workers) = 100% capacity, half staffed = 50% capacity, etc.
        staffing_ratio = self.assigned_workers / max(1, self.max_workers)
        effective_capacity = self.max_capacity * staffing_ratio
        
        # Calculate how many colonists this hospital is effectively serving
        # This distributes the hospital's effect proportionally across the population
        if total_population <= effective_capacity:
            # Hospital can serve the entire population effectively
            health_boost_per_colonist = base_health_production / max(1, total_population)
        else:
            # Hospital is overloaded - effect is diluted
            overload_ratio = effective_capacity / total_population
            effective_health_production = base_health_production * overload_ratio
            health_boost_per_colonist = effective_health_production / max(1, total_population)
            
        return health_boost_per_colonist
    
class PolicePrecinct(Building):
    def __init__(self):
        super().__init__(
            name="Police Precinct",
            description="Reduces crime in surrounding buildings. Requires energy and fuel.",
            max_workers=8,
            energy_consumption=4,
            mineral_consumption=0,
            required_surface=None,
            area_of_effect_radius=2,  # Affects buildings within 2 hexes
            profession=get_profession_for_building('PolicePrecinct')
        )
        self.fuel_consumption = 2
        self.crime_reduction_per_worker = 3  # Crime reduction points per worker
        
    def calculate_production(self):
        """Police precinct doesn't produce resources"""
        return {}
        
    def calculate_consumption(self):
        """Override consumption to include fuel"""
        consumption = super().calculate_consumption()
        consumption['fuel'] = self.fuel_consumption * (self.assigned_workers / max(1, self.max_workers))
        return consumption
        
    def calculate_crime_reduction(self):
        """Calculate total crime reduction based on assigned workers"""
        if not self.active or self.assigned_workers == 0:
            return 0
            
        return self.assigned_workers * self.crime_reduction_per_worker
        
    def apply_area_effect(self, game):
        """Apply crime reduction to buildings in area of effect"""
        if not self.active or self.assigned_workers == 0:
            return
            
        crime_reduction = self.calculate_crime_reduction()
        hex_map = game.graphics.screens['main'].hex_map
        
        # Get all hexes in area of effect
        affected_hexes = self.get_area_of_effect_hexes(hex_map)
        
        for hexagon in affected_hexes:
            if hexagon.building and hasattr(hexagon.building, 'crime_level'):
                # Apply crime reduction (but not below 0)
                hexagon.building.crime_level = max(0, hexagon.building.crime_level - crime_reduction)

class ResidentialBuilding(Building):
    """Parent class for all residential buildings"""
    def __init__(self, name, description, quality, rent, capacity, energy_consumption=0, mineral_consumption=0):
        super().__init__(
            name=name,
            description=description,
            max_workers=0,  # Residential buildings don't have workers
            energy_consumption=energy_consumption,
            mineral_consumption=mineral_consumption,
            required_surface=None
        )
        self.quality = quality
        self.base_quality = quality  # Store original quality
        self.rent = rent
        self.capacity = capacity
        self.residents = []
        self.crime_resistance = 0.7  # Residential buildings are more susceptible to crime
        
    def update_quality_from_crime(self):
        """Update quality based on crime level - minimum quality of 1"""
        quality_penalty = self.get_crime_penalty() * 2  # Crime has stronger effect on quality
        self.quality = max(1.0, self.base_quality - quality_penalty)
        
    def calculate_production(self):
        """Residential buildings don't produce resources"""
        return {}
        
    def add_resident(self, colonist):
        """Add a colonist as resident if there's space"""
        if len(self.residents) < self.capacity:
            self.residents.append(colonist)
            colonist.housing = self
            colonist.housing_quality = self.quality
            colonist.rent_cost = self.rent
            return True
        return False
        
    def remove_resident(self, colonist):
        """Remove a colonist from residence"""
        if colonist in self.residents:
            self.residents.remove(colonist)
            colonist.housing = None
            colonist.housing_quality = 0
            colonist.rent_cost = 0
            return True
        return False
        
    def get_vacancy_count(self):
        """Get number of available spots"""
        return self.capacity - len(self.residents)
        
    def update_rent(self, new_rent):
        """Update the rent amount"""
        self.rent = new_rent
        # Update rent for all current residents
        for colonist in self.residents:
            colonist.rent_cost = new_rent
        
    def update_quality(self, new_quality):
        """Update the quality level"""
        self.quality = new_quality
        self.base_quality = new_quality
        # Update quality for all current residents
        for colonist in self.residents:
            colonist.housing_quality = new_quality

class HabitatBlock(ResidentialBuilding):
    def __init__(self):
        super().__init__(
            name="Habitat Block",
            description="Provides housing for colonists. Quality affects happiness.",
            quality=3.0,
            rent=2.0,
            capacity=10,
            energy_consumption=0,
            mineral_consumption=0
        )
        # All common functionality is inherited from ResidentialBuilding

class Slums(ResidentialBuilding):
    def __init__(self):
        super().__init__(
            name="Slums",
            description="Makeshift housing that appears when colonists are desperate. Zero rent but very poor quality. Generates crime.",
            quality=1.0,
            rent=0.0,
            capacity=10,
            energy_consumption=0,
            mineral_consumption=0
        )
        self.is_slum = True
        self.crime_resistance = 0.3  # Slums have very low crime resistance

def get_building_metadata(building_class):
    """Extract name and description from a building class by creating a temporary instance"""
    temp_instance = building_class()
    return {
        "name": temp_instance.name,
        "description": temp_instance.description,
        "required_surface": temp_instance.required_surface
    }

# Building prices and definitions - now synchronized with classes
BUILDING_CATALOG = {
    "Mine": {
        "class": Mine,
        "price": 500,
        "metadata": get_building_metadata(Mine)
    },
    "EnergyGenerator": {
        "class": EnergyGenerator, 
        "price": 800,
        "metadata": get_building_metadata(EnergyGenerator)
    },
    "OxygenGenerator": {
        "class": OxygenGenerator,
        "price": 450,
        "metadata": get_building_metadata(OxygenGenerator)
    },
    "HydroponicFarm": {
        "class": HydroponicFarm,
        "price": 550,
        "metadata": get_building_metadata(HydroponicFarm)
    },
    "IceExtractor": {
        "class": IceExtractor,
        "price": 650,
        "metadata": get_building_metadata(IceExtractor)
    },
    "ChemicalProcessingPlant": {
        "class": ChemicalProcessingPlant,
        "price": 700,
        "metadata": get_building_metadata(ChemicalProcessingPlant)
    },
    "SolarPanelArray": {
        "class": SolarPanelArray,
        "price": 500,
        "metadata": get_building_metadata(SolarPanelArray)
    },
    "Hospital": {
        "class": Hospital,
        "price": 800,
        "metadata": get_building_metadata(Hospital)
    },
    "PolicePrecinct": {
        "class": PolicePrecinct,
        "price": 800,
        "metadata": get_building_metadata(PolicePrecinct)
    },
    "HabitatBlock": {
        "class": HabitatBlock,
        "price": 700,
        "metadata": get_building_metadata(HabitatBlock)
    }
}

def get_building_price(building_name):
    """Get the price of a building from the catalog"""
    return BUILDING_CATALOG.get(building_name, {}).get("price", 1000)

def get_building_name(building_name):
    """Get the display name of a building from the catalog"""
    return BUILDING_CATALOG.get(building_name, {}).get("metadata", {}).get("name", building_name)

def get_building_description(building_name):
    """Get the description of a building from the catalog"""
    return BUILDING_CATALOG.get(building_name, {}).get("metadata", {}).get("description", "No description available.")

def get_building_required_surface(building_name):
    """Get the required surface type for a building from the catalog"""
    return BUILDING_CATALOG.get(building_name, {}).get("metadata", {}).get("required_surface", None)

def create_building_from_name(building_name):
    """Create a building instance from its name"""
    building_info = BUILDING_CATALOG.get(building_name)
    if building_info:
        return building_info["class"]()
    return None
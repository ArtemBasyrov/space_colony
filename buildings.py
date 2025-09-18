# buildings.py - update the Building class
class Building:
    def __init__(self, name, description, max_workers, energy_consumption=0, mineral_consumption=0):
        self.name = name
        self.description = description
        self.max_workers = max_workers
        self.assigned_workers = 0
        self.assigned_colonists = []  # Track individual colonists
        self.energy_consumption = energy_consumption
        self.mineral_consumption = mineral_consumption
        self.active = True
        self.base_wage = 6  # Base wage for all workers
        
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
            
        # Simple production based on number of workers
        if isinstance(self, Mine):
            return {'minerals': self.assigned_workers * self.production_rate}
        elif isinstance(self, EnergyGenerator):
            return {'energy': self.assigned_workers * self.production_rate}
        elif isinstance(self, OxygenGenerator):
            return {'oxygen': self.assigned_workers * self.production_rate}
        elif isinstance(self, HydroponicFarm):
            return {'food': self.assigned_workers * self.production_rate}
        elif isinstance(self, Hospital):
            return {}  # Hospitals don't produce resources
        return {}
        
    def calculate_consumption(self):
        """Calculate consumption based on assigned workers"""
        consumption = {
            'energy': self.energy_consumption * (self.assigned_workers / max(1, self.max_workers)),
            'minerals': self.mineral_consumption * (self.assigned_workers / max(1, self.max_workers))
        }
        return consumption

class Mine(Building):
    def __init__(self):
        super().__init__(
            name="Crystal Mine",
            description="Extracts minerals from earth. Requires energy.",
            max_workers=20,
            energy_consumption=5
        )
        self.production_rate = 2.0  # Minerals per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'minerals': self.assigned_workers * self.production_rate
        }

class EnergyGenerator(Building):
    def __init__(self):
        super().__init__(
            name="Fusion Reactor",
            description="Generates energy. Requires minerals for fuel.",
            max_workers=10,
            mineral_consumption=3
        )
        self.production_rate = 4.0  # Energy per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'energy': self.assigned_workers * self.production_rate
        }

class OxygenGenerator(Building):
    def __init__(self):
        super().__init__(
            name="Oxygen Synthesizer",
            description="Produces breathable oxygen. Requires energy.",
            max_workers=8,
            energy_consumption=4
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
            energy_consumption=8
        )
        self.production_rate = 2.5  # Food per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        return {
            'food': self.assigned_workers * self.production_rate
        }
    
class Hospital(Building):
    def __init__(self):
        super().__init__(
            name="Hospital",
            description="Improves population health. Requires energy and minerals.",
            max_workers=6,
            energy_consumption=6,
            mineral_consumption=2
        )
        self.production_rate = 3.0  # Health points per worker
        
    def calculate_production(self):
        if not self.active:
            return {}
            
        # Hospital doesn't produce resources, but improves health
        return {}
        
    def calculate_health_boost(self):
        if not self.active:
            return 0
            
        return self.assigned_workers * self.production_rate
    
class HabitatBlock(Building):
    def __init__(self):
        super().__init__(
            name="Habitat Block",
            description="Provides housing for colonists. Quality affects happiness.",
            max_workers=0,  # No workers needed for housing
            energy_consumption=2,
            mineral_consumption=1
        )
        self.quality = 3.0  # Base quality level (affects happiness)
        self.rent = 2.0     # Base rent cost per colonist
        self.capacity = 10  # Maximum colonists that can live here
        self.residents = []  # Colonists living in this habitat
        
    def calculate_production(self):
        """Habitats don't produce resources"""
        return {}
        
    def add_resident(self, colonist):
        """Add a colonist as resident if there's space"""
        if len(self.residents) < self.capacity:
            self.residents.append(colonist)
            colonist.housing = self
            return True
        return False
        
    def remove_resident(self, colonist):
        """Remove a colonist from residence"""
        if colonist in self.residents:
            self.residents.remove(colonist)
            colonist.housing = None
            return True
        return False
        
    def get_vacancy_count(self):
        """Get number of available spots"""
        return self.capacity - len(self.residents)
        
    def update_rent(self, new_rent):
        """Update the rent amount"""
        self.rent = new_rent
        
    def update_quality(self, new_quality):
        """Update the quality level"""
        self.quality = new_quality

def get_building_metadata(building_class):
    """Extract name and description from a building class by creating a temporary instance"""
    temp_instance = building_class()
    return {
        "name": temp_instance.name,
        "description": temp_instance.description
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
        "price": 600,
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
    "Hospital": {
        "class": Hospital,
        "price": 800,
        "metadata": get_building_metadata(Hospital)
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

def create_building_from_name(building_name):
    """Create a building instance from its name"""
    building_info = BUILDING_CATALOG.get(building_name)
    if building_info:
        return building_info["class"]()
    return None
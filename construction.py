# [file name]: construction.py
from buildings import BUILDING_CATALOG, create_building_from_name

class ConstructionSystem:
    def __init__(self, game):
        self.game = game
        self.unlocked_buildings = set(BUILDING_CATALOG.keys())  # Start with all buildings unlocked
        self.construction_mode = False
        self.selected_building_type = None
        self.pending_construction = None
        
    def unlock_building(self, building_name):
        """Unlock a building type for construction"""
        if building_name in BUILDING_CATALOG:
            self.unlocked_buildings.add(building_name)
            return True
        return False
        
    def is_building_unlocked(self, building_name):
        """Check if a building type is available for construction"""
        return building_name in self.unlocked_buildings
        
    def get_available_buildings(self):
        """Get all buildings that can be constructed"""
        return {name: data for name, data in BUILDING_CATALOG.items() 
                if name in self.unlocked_buildings}
        
    def start_construction(self, building_name, hex_position):
        """Start construction of a building"""
        if not self.is_building_unlocked(building_name):
            return False, "Building not unlocked"
            
        building_info = BUILDING_CATALOG[building_name]
        cost = building_info["price"]
        
        if self.game.resources.credits < cost:
            return False, "Insufficient credits"
            
        # Deduct cost
        self.game.resources.credits -= cost
        
        # Create building instance
        building = building_info["class"]()
        building.set_hex_position(*hex_position)
        
        # Add to game buildings
        self.game.buildings.append(building)
        
        return True, f"{building.name} constructed successfully"
# professions.py
PROFESSIONS = {
    'worker': {
        'name': 'Worker',
        'description': 'General labor and production workers',
        'min_wage': 0,
        'max_wage': 20,
        'default_wage': 6,
        'color': (100, 150, 255),
        'buildings': ['Mine', 'EnergyGenerator', 'OxygenGenerator', 'HydroponicFarm', 
                     'IceExtractor', 'ChemicalProcessingPlant', 'SolarPanelArray']
    },
    'police': {
        'name': 'Police Officer', 
        'description': 'Law enforcement and crime prevention',
        'min_wage': 0,
        'max_wage': 20,
        'default_wage': 7,
        'color': (255, 150, 100),
        'buildings': ['PolicePrecinct']
    },
    'doctor': {
        'name': 'Doctor',
        'description': 'Medical care and health services',
        'min_wage': 0, 
        'max_wage': 20,
        'default_wage': 8,
        'color': (100, 255, 150),
        'buildings': ['Hospital']
    }
}

def get_profession_for_building(building_name):
    """Get the profession for a given building type"""
    for profession, data in PROFESSIONS.items():
        if building_name in data['buildings']:
            return profession
    return 'worker'  # Default to worker

def get_all_professions():
    """Get list of all profession keys"""
    return list(PROFESSIONS.keys())

def get_profession_display_name(profession_key):
    """Get display name for a profession key"""
    return PROFESSIONS.get(profession_key, {}).get('name', profession_key)

def get_profession_color(profession_key):
    """Get color for a profession key"""
    return PROFESSIONS.get(profession_key, {}).get('color', (150, 150, 150))

def get_profession_default_wage(profession_key):
    """Get default wage for a profession key"""
    return PROFESSIONS.get(profession_key, {}).get('default_wage', 0)
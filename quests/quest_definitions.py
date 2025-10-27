# [file name]: quest_definitions.py
# [file content begin]
from .quest import Quest
from .quest_triggers import *
from .quest_rewards import *
from buildings import Mine, EnergyGenerator, Hospital, HabitatBlock, OxygenGenerator, HydroponicFarm, ChemicalProcessingPlant

def get_initial_quests():
    """Return all starting quests for the game"""
    return [
        # Tutorial quest chain
        Quest(
            quest_id="tutorial_setup",
            title="Establish Basic Infrastructure",
            description="Build essential buildings for survival",
            detailed_text="""Welcome, Colony Director! Your first task is to establish the basic infrastructure needed for survival in this harsh environment.

Without these basic systems, your colony will not survive long. Prioritize power and oxygen above all else.""",
            triggers=[create_day_trigger(1)],
            objectives=[
                {"type": "building_count", "building_type": EnergyGenerator, "required": 1, "completed": False},
                {"type": "building_count", "building_type": OxygenGenerator, "required": 1, "completed": False},
                {"type": "building_count", "building_type": HydroponicFarm, "required": 1, "completed": False}
            ],
            rewards=[
                grant_resources("credits", 1000),
                unlock_building(Hospital)
            ],
            failure_conditions=[create_population_trigger(0)]
        ),
        
        Quest(
            quest_id="mining_operation",
            title="Establish Mining Operation", 
            description="Extract 100 units of minerals",
            detailed_text="""Now that basic survival is ensured, we need to establish a sustainable mining operation. The surrounding terrain is rich in minerals that we can use for construction and trade.

TIPS:
Assign workers to mines to increase production
Monitor your power consumption - mines require energy""",
            triggers=[create_quest_completion_trigger("tutorial_setup")],
            objectives=[
                {"type": "resource_amount", "resource_type": "minerals", "required": 100, "completed": False},
                {"type": "building_count", "building_type": Mine, "required": 1, "completed": False}
            ],
            rewards=[
                grant_resources("credits", 2000),
                modify_market_price("regolith", 0.8)
            ]
        ),
        
        Quest(
            quest_id="population_growth", 
            title="Expand Colony Population",
            description="Reach 50 colonists",
            detailed_text="""A thriving colony needs people! We must attract new settlers and ensure we have adequate housing and facilities to support them.

CHALLENGES:
Ensure you have enough food and oxygen production
Hospitals will help with population growth and health""",
            triggers=[create_quest_completion_trigger("mining_operation")],
            objectives=[
                {"type": "population_count", "required": 50, "completed": False},
                {"type": "building_count", "building_type": HabitatBlock, "required": 2, "completed": False}
            ],
            rewards=[
                grant_population_bonus(10),
                unlock_building(ChemicalProcessingPlant)
            ]
        )
    ]

def get_midgame_quests():
    """Quests that become available later"""
    return [
        Quest(
            quest_id="economic_independence",
            title="Achieve Economic Independence",
            description="Accumulate 10,000 money through trade",
            detailed_text="""Our colony cannot rely on external funding forever. We must establish a robust economy through smart trading and resource management.

STRATEGIES:
Trade surplus resources on the market
Invest in profitable building combinations
Monitor market prices for buying low and selling high""",
            triggers=[create_day_trigger(30), create_resource_trigger("money", 5000)],
            objectives=[
                {"type": "resource_amount", "resource_type": "money", "required": 10000, "completed": False},
                {"type": "consecutive_days_positive", "required": 10, "completed": False}
            ],
            rewards=[
                modify_market_price("all", 1.1)
            ]
        )
    ]
# [file content end]
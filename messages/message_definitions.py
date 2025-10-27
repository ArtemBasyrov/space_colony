# [file name]: message_definitions.py
# [file content begin]
from .message import Message

def get_initial_messages():
    """Return all initial messages for the game"""
    return [
        Message(
            message_id="welcome_message",
            title="Transmission Received",
            sender="Corporate Command",
            portrait="command_portrait",
            text="""Welcome to the Tau Ceti system, Colony Director.

Your mission is to establish a profitable mining operation on this desolate moon. The Board has high expectations for your performance.

Initial objectives:
- Establish basic life support systems
- Begin mineral extraction operations
- Expand colony population

Remember: Profit is priority. The Board is watching.""",
            day_trigger=1
        ),
        
        Message(
            message_id="first_production",
            title="Production Report",
            sender="Operations Manager Chen",
            portrait="chen_portrait",
            text="""Director, our initial production systems are coming online.

The mining drones have detected rich mineral deposits in the surrounding area. I recommend prioritizing expansion of our mining operations.

However, we're experiencing power fluctuations in sector 4. We may need to build additional energy generators soon.

Keep an eye on our resource stockpiles - we don't want to run out of oxygen.""",
            day_trigger=3
        ),
        
        Message(
            message_id="market_opportunity",
            title="Market Analysis",
            sender="Trade Representative Volkov",
            portrait="volkov_portrait", 
            text="""Director, I have promising market intelligence.

The galactic market prices for Regolith have increased by 15% this cycle. This presents an excellent opportunity for profit.

I recommend stockpiling our Regolith production and waiting for the price to peak before selling.

Also, consider investing in additional mining operations while prices are favorable.

Volkov out.""",
            day_trigger=5
        )
    ]

def get_midgame_messages():
    """Messages that become available later in the game"""
    return [
        Message(
            message_id="rival_company",
            title="Competitor Alert",
            sender="Corporate Intelligence",
            portrait="intel_portrait",
            text="""Director, we have troubling news.

A rival corporation, OmniCorp, has established a mining operation in the adjacent sector. They're competing for the same resources.

Our analysts suggest they may attempt hostile takeover maneuvers. Strengthen your economic position and consider defensive measures.

The Board expects you to maintain our market dominance in this system.""",
            day_trigger=15
        ),
        
        Message(
            message_id="breakthrough",
            title="Research Breakthrough",
            sender="Dr. Arisaka",
            portrait="arisaka_portrait",
            text="""Director, fantastic news from the research division!

We've developed a new extraction technique that could increase mining efficiency by 40%. The technology is ready for implementation.

This could give us a significant advantage over OmniCorp. I recommend retrofitting our existing mines as soon as possible.

The research team awaits your approval to begin manufacturing the new components.""",
            day_trigger=20
        )
    ]
# [file content end]
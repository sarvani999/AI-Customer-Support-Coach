from dataclasses import dataclass

@dataclass
class Session:
    interaction_mode: str
    product: str
    scenario: str
    customer_persona: str
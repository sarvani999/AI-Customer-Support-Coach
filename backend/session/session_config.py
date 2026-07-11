from pydantic import BaseModel


class SessionConfig(BaseModel):
    interaction_mode: str
    product: str
    scenario: str
    customer_persona: str
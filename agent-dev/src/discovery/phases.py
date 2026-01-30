from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DiscoveryPhase(Enum):
    INTRO = "INTRO"
    GOALS = "GOALS"
    USERS = "USERS"
    CONSTRAINTS = "CONSTRAINTS"
    NON_GOALS = "NON_GOALS"
    RISKS = "RISKS"
    CONFIRMATION = "CONFIRMATION"


class PhaseState(BaseModel):
    phase: str
    response: str
    timestamp: datetime
    validated: bool = False
    issues: Optional[list[str]] = None


class DiscoveryState(BaseModel):
    current_phase: DiscoveryPhase
    phase_states: dict[str, PhaseState] = {}
    responses: dict[str, dict] = {}
    is_complete: bool = False
    confirmed: bool = False
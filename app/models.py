from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

BoundingBox = Tuple[int, int, int, int]  # coords (xmin,ymim,xmax,ymax)


class Behavior(Enum):
    APPROACH = "approach"
    AVOID = "avoid"
    CONTINUE = "continue"

class OperatorChoice(Enum):
    CONTINUE_MISSION = "continue_mission"
    TAKE_MANUAL_CONTROL = "take_manual_control"
    RESUME_NEXT_WAYPOINT = "resume_next_waypoint"

@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    bounding_box: BoundingBox


@dataclass(frozen=True)
class Decision:
    behavior: Behavior
    reason: str
    object_label: Optional[str] = None


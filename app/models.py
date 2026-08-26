from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

BoundingBox = Tuple[int, int, int, int]  # coords (xmin,ymim,xmax,ymax)


class Behavior(Enum):
    APPROACH = "approach"
    AVOID = "avoid"
    CONTINUE = "continue"


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

from typing import List

from constants import (
    MINIMUM_OBSTACLE_CONFIDENCE,
    MINIMUM_TARGET_CONFIDENCE,
    OBSTACLE_LABELS,
    TARGET_LABELS,
)

from models import Behavior, Decision, Detection


def choose_behavior(detections: List[Detection]) -> Decision:
    obstacles = [
        detection
        for detection in detections
        if (
            detection.label
            in OBSTACLE_LABELS  # if something found to be labeled as an obstacle
            and detection.confidence
            >= MINIMUM_OBSTACLE_CONFIDENCE  # and it is above confidence threshhold, add to obstacle list
        )
    ]

    if (
        obstacles
    ):  # if list is not empty (obstacle meeting confidence threshold is present)
        obstacle = max(
            obstacles,
            key=lambda detection: detection.confidence,  # select object with highest confidence
        )

        return Decision(
            behavior=Behavior.AVOID, # avoid selected obstacle
            reason=f"Obstacle detected: {obstacle.label}",  
            object_label=obstacle.label,
        )

    targets = [
        detection
        for detection in detections
        if (
            detection.label
            in TARGET_LABELS  # if something found to be labeled as a target
            and detection.confidence
            >= MINIMUM_TARGET_CONFIDENCE  # and it is above confidence threshhold, add to target list
        )
    ]

    if targets: # if list is not empty (target meeting confidence threshold is present)
        target = max(
            targets,
            key=lambda detection: detection.confidence,
        )

        return Decision(
            behavior=Behavior.APPROACH, # approach selected target
            reason=f"Target detected: {target.label}",
            object_label=target.label,
        )

    return Decision( # if no obstacles or targets, continue as normal
        behavior=Behavior.CONTINUE,
        reason="No relevant objects detected",
    )

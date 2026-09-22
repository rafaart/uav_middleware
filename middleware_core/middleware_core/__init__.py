"""Núcleo de decisão do middleware — agnóstico a ROS2/MAVROS/OpenCV.

Ver README.md deste pacote para a justificativa arquitetural completa.
"""

from middleware_core.contracts import (
    AutopilotStatus,
    BoundingBox,
    Detection,
    FrameContext,
    NavigationCommand,
    TrackerState,
)
from middleware_core.controller import ControllerParams
from middleware_core.pipeline import TrackingPipeline

__all__ = [
    "AutopilotStatus",
    "BoundingBox",
    "Detection",
    "FrameContext",
    "NavigationCommand",
    "TrackerState",
    "ControllerParams",
    "TrackingPipeline",
]

__version__ = "0.1.0"

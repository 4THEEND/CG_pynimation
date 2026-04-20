from typing import Dict, Any
from .analytical_ik import AnalyticalIK

from pynimation.anim import Joint


def ikFactory(
    targetJoint: Joint,
    endJoint: Joint,
    settings: Dict[str, Any] = None,
):
    if targetJoint.parent.parent == endJoint:
        return AnalyticalIK(targetJoint, endJoint, settings)
    else:
        raise NotImplementedError("no IK algorithm for given parameters")

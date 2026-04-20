import abc
from typing import Dict, Any

import numpy

from pynimation.anim import Frame
from pynimation.anim import Joint


class IK(abc.ABC):
    """
    Base IK class
    """

    @abc.abstractmethod
    def __init__(
        self,
        targetJoint: Joint,
        endJoint: Joint,
        settings: Dict[str, Any] = None,
    ):
        pass

    @abc.abstractmethod
    def solve(self, targetPos: numpy.ndarray, frame: Frame) -> None:
        """
        Abstract ik solve method
        Overriding methods must solve IK for given parameters

        Parameters
        ----------
        targetPos:
            desired position for the target
        frame:
            frame of the animation the ik algorithm will be applied to
        """
        pass

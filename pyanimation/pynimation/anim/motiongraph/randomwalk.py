import random
from typing import TYPE_CHECKING

import numpy

from pynimation.common import Transform

if TYPE_CHECKING:
    from pynimation.anim.motiongraph.motiongraph import MotionGraph
    from pynimation.anim import Frame


class RandomWalk:
    """A basic random walk implementation for a Motion Graph

    Parameters
    ----------
    mograph: MotionGraph
        MotionGraph instance used to by the random walk

    Attributes
    ----------
    mograph: MotionGraph
        MotionGraph instance used to by the random walk

    currentNode: int
        current node in the motion graph walk

    cumulatedTime: float
        cumulated time since beginning of random walk

    remainingTime: float
        remaining time not taken into account in the last update

    cumulatedTransform: Transform
        cumulated transform since beginning of random walk
    """

    def __init__(self, mograph: "MotionGraph"):
        self.mograph = mograph
        self.cumulatedTime: float = 0
        self.remainingTime: float = 0
        self.currentNode: int = 0
        self.cumulatedTransform: Transform = Transform()

    def getCurrentFrame(self) -> "Frame":
        """
        Get the frame of the random walk animation for the current time

        Returns
        -------
        Frame:
            frame of the animation for the current time
        """
        fr = self.mograph.nodes[self.currentNode].frame.copy()
        self.cumulatedTransform = numpy.dot(
            self.cumulatedTransform, fr.localTransforms[fr.skeleton.root.id]
        )
        fr.localTransforms[fr.skeleton.root.id] = self.cumulatedTransform
        return fr

    def update(self, deltaTime: float) -> None:
        """
        Update the state of the random walk based on a :attr:`deltaTime`
        difference since last call

        Parameters
        ----------
        deltaTime:
            time since last call to this function
        """
        self.remainingTime += deltaTime
        self.cumulatedTime += deltaTime
        dt = 1.0 / self.mograph.framerate
        while self.remainingTime > dt:
            trans = list(self.mograph.nodes[self.currentNode].transitions)
            t = random.randint(0, len(trans) - 1)
            self.cumulatedTransform = numpy.dot(
                self.cumulatedTransform,
                self.mograph.nodes[self.currentNode].transitions[trans[t]],
            )
            self.currentNode = trans[t]
            self.remainingTime -= dt

import math
import numpy
from pynimation.anim.frame import Frame
from pynimation.common import Transform
from pynimation.anim.skeleton import Skeleton
from typing import List
from copy import deepcopy

from pynimation.anim.metrics import (
    LocalOrientationWithoutRootMetric as Metric,
)

class Animation:
    """
    Internal representation of an animation

    Parameters
    ----------
    framerate: int
        original framerate of the animation

    skeleton: Skeleton
        skeleton that is animated

    frameNumber: int
        total number of frames in the animation

    Attributes
    ----------
    framerate: int
        original framerate of the animation

    skeleton: Skeleton
        The skeleton that is animated. Each
        :class:`~pynimation.anim.joint.Joint` :code:`j` of the
        :class:`~pynimation.anim.skeleton.Skeleton` is transformed at each
        :class:`~pynimation.anim.frame.Frame` :code:`f` by
        :code:`f.localTransforms[j.id]`

    frames: List[Frame]
        List of Frames of the animation. Each frame is a list of
        :class:`~pynimation.common.transform.Transform`, one for each joint of
        :attr:`skeleton`. This list and its elements are the main interface to
        access and modify the animation.

    """

    def __init__(
        self,
        framerate: int,
        skeleton: Skeleton,
        frameNumber: int = 0,
    ) -> None:
        self.skeleton = skeleton
        self.framerate = framerate
        self.frames: List[Frame] = [
            Frame(self.skeleton) for _ in range(frameNumber)
        ]

    def addFrame(self, frame: Frame) -> None:
        """
        Add a frame to the animation

        Parameters
        ----------
        frame:
            frame to add

        Raises
        ------
        ValueError
            If the skeleton of :attr:`frame` has a different topology than :attr:`skeleton`

        """
        if not frame.skeleton.hasSameTopology(self.skeleton):
            raise ValueError(
                "frame's skeleton has different topology than"
                + " animation's skeleton"
            )

        self.frames.append(frame)

    def setFrame(self, frameID: int, frame: Frame) -> None:
        """

        Parameters
        ----------
        frameID:
            Index of the frame to set in :attr:`frames`

        frame:
            Value of the new frame

        Raises
        ------
        ValueError
            If the skeleton of :attr:`frame` has a different topology than :attr:`skeleton`
            If frameID is larger than last frame index in :attt:`frames`

        """
        if not frame.skeleton.hasSameTopology(self.skeleton):
            raise ValueError(
                "frame's skeleton has different topology than"
                + " animation's skeleton"
            )

        if frameID < len(self.frames):
            raise ValueError(
                "frameID "
                + str(frameID)
                + " exceeds last frame index "
                + str(len(self.frames))
            )

        else:
            self.frames[frameID] = frame

    def copy(self) -> "Animation":
        """
        Get a deep copy of this animation

        Returns
        -------
        Animation:
            A deep copy of this animation
        """
        return deepcopy(self)

    def getFrameFromTime(
        self, time: float, interpolate: bool = False
    ) -> Frame:
        """
        Computes which frame of the animation should be played at time
        :attr:`time` if the animation is repeated

        Parameters
        ----------
        time:
            time for which a frame is requested, if :attr:`time` exceeds the duration
            of the animation, a frame is returned for :code:`time % duration`

        interpolate:
            if :code:`True`, interpolates the frame just before :attr:`time`
            and the one right after according to their times and the difference
            with :attr:`time`

        Note
        ----
        Interpolation can be much more resource intensive and might not be
        suited for playing animations in real-time


        Returns
        -------
        Frame
            the frame that should be played at time :attr:`time` if the animation is repeated

        """
        duration = self.getDuration()
        if time < 0 or time > duration:
            time = time % duration

        fID = time * self.framerate
        if interpolate:
            fIDMin = (int)(fID // 1)
            fIDMax = fIDMin + 1
            f1 = self.frames[fIDMin]
            f2 = self.frames[fIDMax]
            w = (fIDMax - fID) / (fIDMax - fIDMin)
            return Frame.interpolate([f1, f2], [w, 1.0 - w])
        else:
            return self.frames[round(fID)]

    def getDuration(self) -> float:
        """
        Get the duration of the animation

        Returns
        -------
        float:
            duration of the animation in seconds
        """
        return (len(self.frames) - 1) / self.framerate

    def getFrameNumber(self) -> int:
        """
        Get the number of frames in the animation

        Returns
        -------
        int:
            number of frames in the animation
        """
        return len(self.frames)

    def getJointTrajectory(self, jointId: int) -> numpy.ndarray:
        """
        Get the trajectory of joint :attr:`jointId`, as an array of 3D positions

        Parameters
        ----------
        jointId:
            id of the joint


        Returns
        -------
        numpy.ndarray
            an array of the 3D positions of joint :attr:`jointId`, one position
            for each frame
        """
        return [
            self.frames[i].globalTransforms[jointId].getPosition()
            for i in range(self.getFrameNumber())
        ]

    def setFramerate(self, framerate: int) -> None:
        # TODO: explain behaviour difference between cyclic and non-cyclic
        """
        Set the framerate of the animation

        Parameters
        ----------
        framerate:
            new framerate

        """

        if self.framerate == framerate:
            return

        oldNbFrames = self.getFrameNumber()
        if self.isCyclic():
            # For cyclic motions we want to ensure that we keep the first and
            # last frame the same, and therefore timewarp the motion
            nbFrames = (int)(
                round((oldNbFrames - 1) * framerate / self.framerate)
            ) + 1
            # frameToTime = self.getDuration() / (nbFrames - 1)
            newFrames = [
                self.getFrameFromTime(fr / framerate)  # fr * frameToTime
                for fr in range(nbFrames)
            ]
        else:
            nbFrames = (int)(
                math.floor((oldNbFrames - 1) * framerate / self.framerate)
            ) + 1
            newFrames = [
                self.getFrameFromTime(fr / framerate) for fr in range(nbFrames)
            ]

        self.frames = newFrames
        self.framerate = framerate

    def setOriginRootXZPosition(
        self, position: List[float] = [0.0, 0.0]
    ) -> None:
        """
        Set the initial position of the root joint on the XZ plane to
        :attr:`position`. The entire animation is shifted so that the root
        joint is at :attr:`position` on the first frame

        Parameters
        ----------
        position:
            array of 2 elements, the x and z positions

        """
        originalPosition = self.frames[0].localTransforms[0].getPosition()
        originalPosition[0] -= position[0]
        originalPosition[2] -= position[1]

        rootID = self.skeleton.root.id
        for i in range(self.getFrameNumber()):
            fr = self.frames[i]
            pos = fr.getRootPosition()
            fr.setBonePosition(
                rootID,
                [
                    pos[0] - originalPosition[0],
                    pos[1],
                    pos[2] - originalPosition[2],
                ],
            )

    def getCycleOffset(self, time: float) -> Transform:
        """
        Compute the offset transform of the root joint from the first frame of
        the first cycle to the first frame of current cycle at :attr:`time`.
        Essentially, get the offset of the current cycle at :attr:`time`

        Parameters
        ----------
        time:
            time for which to compute the offset transformation


        Returns
        -------
        Transform:
            offset transform for time :attr:`time` taking cycles into account

        """

        duration = self.getDuration()
        cycle = math.floor(time / duration)

        originalTransform = self.frames[0].globalTransforms[
            self.skeleton.root.id
        ]
        finalTransform = self.frames[-1].globalTransforms[
            self.skeleton.root.id
        ]
        offsetTransform = finalTransform * originalTransform.inverse()

        offset = Transform()
        for i in range(cycle):
            offset = offset * offsetTransform

        return offset

    def getFrameXZOffset(self, time: float) -> Transform:
        """
        Compute offset transform of the root joint for XZ position and Y
        rotation from the initial frame of the current cycle to :attr:`time`.
        Essentially, get the offset of the frame at :attr:`time` inside its cycle

        Parameters
        ----------
        time:
            time for which the offset is computed

        Returns
        -------
        Transform:
            offset of the Frame at time :attr:`time` relative to the start of
            the cycle

        """
        t = time % self.getDuration()

        originalTransform = self.frames[0].globalTransforms[
            self.skeleton.root.id
        ]
        frame = self.getFrameFromTime(t)
        frameTransform = frame.globalTransforms[self.skeleton.root.id]

        return Transform.computeXZOffset(originalTransform, frameTransform)

    def getXZOffset(self, time: int) -> Transform:
        """
        Compute offset transform of the root joint for XZ position and Y
        rotation from the first frame of the first cycle to time :attr:`time`

        Parameters
        ----------
        time:
            time for which the offset is computed

        Returns
        -------
        Transform:
            offset of the animation at time :attr:`time`

        """
        duration = self.getDuration()
        cycle = math.floor(time / duration)
        offset = Transform()

        if cycle == 0:
            return offset

        offsetTransform = self.getFrameXZOffset(self.getDuration())
        for i in range(cycle):
            offset = offset * offsetTransform

        return offset
        
    def createRootProjectionProxy(self) -> None:
        """
        Create a proxy bone and set its animation the the XZ position and Y
        rotation of the current root
        """
        if self.skeleton.proxyBone:
            return

        originalRootId = self.skeleton.root.id
        self.skeleton.createProxyBone()

        for (frId, oldFrame) in enumerate(self.frames):
            proxyTrans = oldFrame.localTransforms[
                originalRootId
            ].extractXZTransform()
            rootTrans = (
                proxyTrans.inverse() * oldFrame.localTransforms[originalRootId]
            )

            newFrame = Frame(self.skeleton)
            for i in range(len(self.skeleton.nodes)):
                if i == self.skeleton.root.id:
                    newFrame.localTransforms[i] = proxyTrans
                elif i == (originalRootId + 1):
                    newFrame.localTransforms[i] = rootTrans
                else:
                    newFrame.localTransforms[i] = oldFrame.localTransforms[
                        i - 1
                    ].copy()
            self.frames[frId] = newFrame

    def setRelativeRootGlobalTransform(self) -> None:
        """
        Make the root joint global transforms for each frame relative the one
        of the previous frame
        """
        rootId = self.skeleton.root.id
        for fr in range(self.getFrameNumber() - 1, 0, -1):
            self.frames[fr].localTransforms[rootId] = numpy.dot(
                self.frames[fr - 1].localTransforms[rootId].inverse(),
                self.frames[fr].localTransforms[rootId],
            )

    def setAbsoluteRootGlobalTransform(self) -> None:
        """
        Make the root joint global transforms for each frame relative to the
        one of the the first frame
        """
        rootId = self.skeleton.root.id
        for fr in range(1, self.getFrameNumber()):
            self.frames[fr].localTransforms[rootId] = numpy.dot(
                self.frames[fr - 1].localTransforms[rootId],
                self.frames[fr].localTransforms[rootId],
            )

    def destroyProxyBone(self) -> None:
        """
        Remove the proxy bone if there is one and apply its animation to the root
        """
        if self.skeleton.proxyBone is None:
            return

        proxyId = self.skeleton.root.id
        rootId = (
            proxyId + 1
        )  # LUDO TOFIX: self.skeleton.root.children[0].id (PROBLEM WHILE ADDING ROOT - TWO JOINTS WITH ID 0)
        self.skeleton.destroyProxyBone()

        for (frId, oldFrame) in enumerate(self.frames):
            newRootTrans = oldFrame.globalTransforms[rootId]

            newFrame = Frame(self.skeleton)
            for i in range(len(self.skeleton.nodes)):
                if i == self.skeleton.root.id:
                    newFrame.localTransforms[i] = newRootTrans
                else:
                    newFrame.localTransforms[i] = oldFrame.localTransforms[
                        i + 1
                    ].copy()
            self.frames[frId] = newFrame

    def isCyclic(self) -> bool:
        """
        Determine if the animation is cyclic using
        :class:`~pynimation.similarity.similarity.Similarity` metrics between
        the first and the last frame

        Returns
        -------
        bool:
            wether the animation is cyclic

        """

        metric = Metric()
        sim = metric.evaluate(
            metric.prepareFrame(0, self),
            metric.prepareFrame(self.getFrameNumber() - 1, self),
        )
        return sim < 0.001
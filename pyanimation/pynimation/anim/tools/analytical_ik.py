from typing import Dict, Any
import math

import numpy as np

from pynimation.common import Transform
from pynimation.common import RotationTools
from pynimation.anim import Joint
from pynimation.anim import Frame
from .ik import IK


class AnalyticalIK(IK):
    """
    Implements IK with the analytical method
    Is only applicable to chains of 3 joints
    """

    defaultSettings = {"debug": False, "backupRotAxis": "X"}

    def __init__(
        self,
        targetJoint: Joint,
        endJoint: Joint,
        settings: Dict[str, Any] = None,
    ):
        self.targetJoint = targetJoint
        self.endJoint = endJoint
        if self.endJoint != self.targetJoint.parent.parent:
            raise ValueError("given joint chain must be 3 joint long")
        self.intermediateJoint = self.targetJoint.parent
        if settings is None:
            self.settings = AnalyticalIK.defaultSettings
        else:
            self.settings = {**AnalyticalIK.defaultSettings, **settings}

    def solve(self, targetPos: np.ndarray, frame: Frame) -> None:
        """
        Solves IK with the analytical method

        Parameters
        ----------
        targetPos:
            desired position for the target
        frame:
            frame of the animation the ik algorithm will be applied to
        """

        originalGlobalPositionTarget = frame.getBoneGlobalPosition(
            self.targetJoint.id
        )

        L1 = np.linalg.norm(self.intermediateJoint.transform.getPosition())
        L2 = np.linalg.norm(self.targetJoint.transform.getPosition())

        rootPos = frame.getBoneGlobalPosition(self.endJoint.id)

        d = np.linalg.norm(targetPos - rootPos)
        theta = math.pi - math.acos(
            np.clip((L1 ** 2 + L2 ** 2 - d ** 2) / (2 * L1 * L2), -1, 1)
        )

        axisRot = (
            frame.getBoneLocalTransform(self.intermediateJoint.id)
            .getQuaternion()
            .get_axis()
        )
        if np.linalg.norm(axisRot) == 0:
            axisRot = RotationTools.getAxis(self.settings["backupRotAxis"])
        Rot = Transform()
        Rot.setAxisAngle(axis=axisRot, angle=theta)
        frame.setBoneLocalRotation(
            self.intermediateJoint.id, Rot.getRotation()
        )

        currentTargetPos = frame.getBoneGlobalPosition(self.targetJoint.id)

        rot = Transform.rotationMatrixAlignVectors(
            currentTargetPos - rootPos, targetPos - rootPos
        )
        rot = np.dot(
            rot.getRotation(),
            frame.getBoneGlobalTransform(self.endJoint.id).getRotation(),
        )

        frame.setBoneLocalRotation(
            self.endJoint.id,
            np.dot(
                np.linalg.inv(
                    frame.getBoneGlobalTransform(
                        self.endJoint.parent.id
                    ).getRotation()
                ),
                rot,
            ),
        )
        newPosTarget = frame.getBoneGlobalPosition(self.targetJoint.id)

        if self.settings["debug"]:
            print("old: " + str(originalGlobalPositionTarget))
            print("new" + str(newPosTarget))
            print(
                "Error: "
                + str(
                    np.linalg.norm(originalGlobalPositionTarget - newPosTarget)
                )
            )

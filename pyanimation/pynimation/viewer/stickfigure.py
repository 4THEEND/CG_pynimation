from typing import List, Union
import numpy
from pynimation.common import Transform
from pynimation.anim import Frame
from pynimation.anim import Skeleton
from .objects.capsule import Capsule
from .scene_graph import SceneNode
from .animatable import Animatable


class StickFigure(SceneNode, Animatable):
    """
    Skeletal 3D figure used to display an animation.
    Parent of the :class:`~pynimation.viewer.objects.Capsule` 3D meshes, that
    are displayed as the skeleton limbs

    Parameters
    ----------
    skeleton: Skeleton:
        skeleton that is displayed
    color: numpy.ndarray:
        color of the figure
    boneRadius: float:
        radius of the joint meshes

    Attributes
    ----------
    skeleton: Skeleton:
        skeleton that is displayed
    color: numpy.ndarray:
        color of the figure
    boneRadius: float:
        radius of the joint meshes
    """

    def __init__(
        self,
        skeleton: Skeleton,
        color: List[Union[float, int]] = [0.9, 0.0, 0.0, 1],
        boneRadius: float = 0.005,
    ) -> None:
        super().__init__("")
        self.skeleton = skeleton
        self.boneRadius = boneRadius
        self._addCapsulesForJoint(0, color)

    def _addCapsulesForJoint(
        self, jointID: int, color: List[Union[float, int]]
    ) -> None:
        """

        Parameters
        ----------
        jointID: int :

        color: List[Union[float :

        int]] :


        Returns
        -------

        """
        if len(self.skeleton.joints[jointID].children) != 0:
            for i in self.skeleton.joints[jointID].children:
                # Only add capsule if not proxy joint
                if (
                    self.skeleton.proxyBone is None
                    or self.skeleton.proxyBone.id != jointID
                ):
                    p = i.transform.getPosition()
                    jointLength = numpy.linalg.norm(p)
                    defaultRotation = Transform.rotationMatrixAlignVectors(
                        [0, 1, 0], p
                    )
                    capsule = Capsule(
                        jointID,
                        defaultRotation,
                        jointLength,
                        self.boneRadius,
                        False,
                        color,
                    )
                    self.addChild(capsule)

                self._addCapsulesForJoint(i.id, color)
        # else:
        # capsule = Capsule(0.05, self.boneRadius, False)
        # self.capsules.append([jointID, capsule, None])

    def animate(
        self,
        frame: Frame,
    ) -> None:
        """
        Animate the figure with :attr:`frame`

        Parameters
        ----------
        frame:
            frame to animated the figure with
        """
        for capsule in self.children:
            # if capsule.jointID == 0:
            #     import ipdb

            #     ipdb.set_trace()
            frameTransform = frame.globalTransforms[capsule.jointID]
            capsule.transform = frameTransform * capsule.defaultRotation

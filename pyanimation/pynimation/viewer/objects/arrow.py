import numpy
import math
from pyquaternion import Quaternion

from .cylinder import Cylinder
from typing import List, Union
from numpy import ndarray
from pynimation.common import RotationTools
from ..scene_graph import SceneNode

AXIS = "y"


class Arrow(SceneNode):
    """
    A 3D arrow

    Parameters
    ----------
    radiusBaseProp : float, optional
        The length proportion of the radius of the base, by default 0.4
    radiusPointerProp : float, optional
        The length proportion of the radius of the pointer, by default 0.6
    lengthBaseProp : float, optional
        The length proportion of the length of the base , by default 0.85
    lengthPointerProp : float, optional
        The length proportion of the length of the pointer, by default 0.15
    color : List[Union[float, int]], optional
        The color of the arrow, by default [0.5, 0.9, 0.5, 1]
    phong : bool, optional
        Sheder selector if True Phong, if False Diffuse, by default False
    pointAt : ndarray, optional
        A position where to direct the arrow, by default numpy.array([0.0, 1.0, 0.0])
    length : float, optional
        The total length of the arrow, by default 1
    radius : float, optional
        The total radius of the arrow, by default 0.05

    Attributes
    ----------
    radiusBaseProp : float, optional
        The length proportion of the radius of the base, by default 0.4
    radiusPointerProp : float, optional
        The length proportion of the radius of the pointer, by default 0.6
    lengthBaseProp : float, optional
        The length proportion of the length of the base , by default 0.85
    lengthPointerProp : float, optional
        The length proportion of the length of the pointer, by default 0.15
    color : List[Union[float, int]], optional
        The color of the arrow, by default [0.5, 0.9, 0.5, 1]
    phong : bool, optional
        Sheder selector if True Phong, if False Diffuse, by default False
    pointAt : ndarray, optional
        A position where to direct the arrow, by default numpy.array([0.0, 1.0, 0.0])
    length : float, optional
        The total length of the arrow, by default 1
    radius : float, optional
        The total radius of the arrow, by default 0.05

    """

    # TODO find a way to dynamically modify length and radius
    def __init__(
        self,
        length: float = 1,
        radius: float = 0.05,
        pointAt: ndarray = numpy.array([0.0, 1.0, 0.0]),
        color: List[Union[float, int]] = [0.5, 0.9, 0.5, 1],
        phong: bool = False,
        radiusBaseProp: float = 0.4,
        radiusPointerProp: float = 0.6,
        lengthBaseProp: float = 0.85,
        lengthPointerProp: float = 0.15,
    ):
        """
        Initialize the 3D arrow

        Parameters
        ----------
        radiusBaseProp : float, optional
            The length proportion of the radius of the base, by default 0.4
        radiusPointerProp : float, optional
            The length proportion of the radius of the pointer, by default 0.6
        lengthBaseProp : float, optional
            The length proportion of the length of the base , by default 0.85
        lengthPointerProp : float, optional
            The length proportion of the length of the pointer, by default 0.15
        color : List[Union[float, int]], optional
            The color of the arrow, by default [0.5, 0.9, 0.5, 1]
        phong : bool, optional
            Sheder selector if True Phong, if False Diffuse, by default False
        pointAt : ndarray, optional
            A position where to direct the arrow, by default numpy.array([0.0, 1.0, 0.0])
        length : float, optional
            The total length of the arrow, by default 1
        radius : float, optional
            The total radius of the arrow, by default 0.05
        """
        super().__init__("")
        self.radiusProp: ndarray = numpy.array(
            [radiusBaseProp, radiusPointerProp]
        )
        self.lengthProp: ndarray = numpy.array(
            [lengthBaseProp, lengthPointerProp]
        )
        self.radiusProp = RotationTools.normalize(self.radiusProp)
        self.lengthProp = RotationTools.normalize(self.lengthProp)
        self.length: float = length
        self.radius: float = radius
        self.color = color
        self.phong = phong
        self._generateCylinders()
        self.pointAt(pointAt)
        self.addChild(self.cylinderBase)
        self.addChild(self.cylinderPointer)

    def _generateCylinders(self) -> None:
        self.cylinderBase: Cylinder = Cylinder(
            height=self.length * self.lengthProp[0],
            radiusBase=self.radius * self.radiusProp[0],
            radiusTop=self.radius * self.radiusProp[0],
            numberOfSectors=20,
            numberOfStacks=3,
            center=False,
            color=self.color,
            height_direction=AXIS,
            phong=self.phong,
        )
        self.cylinderPointer: Cylinder = Cylinder(
            height=self.length * self.lengthProp[1],
            radiusBase=self.radius * self.radiusProp[1],
            radiusTop=0.001,
            numberOfSectors=20,
            numberOfStacks=3,
            center=False,
            color=self.color,
            height_direction=AXIS,
            phong=self.phong,
        )
        yDirection = RotationTools.normalize(self.transform.getYVector())
        baseDirection = yDirection * self.length * self.lengthProp[0]
        self.cylinderPointer.transform.translate(baseDirection)

    def pointAt(self, target: ndarray) -> None:
        """
        Direct the arrow to point at target

        Parameters
        ----------
        target : ndarray
            The position to point at
        """
        position = self.transform.getPosition()
        yDirection = self.transform.getYVector()
        normalizedTarget = RotationTools.normalize(target - position)
        normalizedPosition = RotationTools.normalize(yDirection)
        dot = numpy.dot(normalizedTarget, normalizedPosition)
        angle = math.acos(dot)
        if angle != 0:
            orth = numpy.cross(normalizedPosition, normalizedTarget)
            axis = RotationTools.normalize(orth)
            if (
                numpy.linalg.norm(axis) > 0.01
                or numpy.linalg.norm(axis) < 0.01
            ):
                deltaQuaterion: Quaternion = Quaternion(axis=axis, angle=angle)
                currentQuaternion = self.transform.getQuaternion()
                rotationQuaternion = deltaQuaterion * currentQuaternion
                newQuaternion = rotationQuaternion.normalised
                self.transform.setQuaternion(newQuaternion)

    def alignToDirection(self, newDirection: ndarray) -> None:
        """
        Align the arrow to the desired direction

        Parameters
        ----------
        newDirection : ndarray
            The given direction
        """
        position = self.transform.getPosition()
        lookAt = position + newDirection
        self.lookAt(lookAt)

    def setPosition(self, position: ndarray) -> None:
        """
        Shortcut to define the position of the arrow

        Parameters
        ----------
        position : ndarray
            The desired position
        """
        self.position = position
        self.transform.setPosition(position)

    def translate(self, translation: ndarray) -> None:
        """
        Shortcut to translate the arrow

        Parameters
        ----------
        translation : ndarray
            How much to translate
        """
        self.transform.translate(translation)

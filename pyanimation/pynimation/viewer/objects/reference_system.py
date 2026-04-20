import numpy
from numpy import ndarray
from ..scene_graph import SceneNode
from .cylinder import Cylinder
from .sphere import Sphere
from .arrow import Arrow


class ReferenceSystem(SceneNode):
    """
    A 3D reference system

    Parameters
    ----------
    sizeFactor : float, optional
        The size factor of the arrow, by default 1
    radius : float, optional
        The total radius of the arrow, by default 0.05
    phong : bool, optional
        Sheder selector if True Phong, if False Diffuse, by default False

    Attributes
    ----------
    sizeFactor : float, optional
        The size factor of the arrow, by default 1
    radius : float, optional
        The total radius of the arrow, by default 0.05
    phong : bool, optional
        Sheder selector if True Phong, if False Diffuse, by default False

    """

    # TODO find a way to dynamically modify length and radius
    def __init__(
        self,
        sizeFactor: float = 0.3,
        radius: float = 0.03,
        phong: bool = False,
        alpha: float = 0.75,
        coneAxes: bool = False,
    ):
        """
        Initialize the reference system

        Parameters
        ----------
        sizeFactor : float, optional
            The size factor of the arrow, by default 1
        radius : float, optional
            The total radius of the arrow, by default 0.05
        phong : bool, optional
            Sheder selector if True Phong, if False Diffuse, by default False
        alpha : float, optional
            The alpha value of the axis, by default 0.75
        coneAxes : bool, optional
            If True the axis are represented as cones, if False as arrows, by default False
        """
        super().__init__("")
        self.sizeFactor: float = sizeFactor
        self.radius: float = radius
        self.phong: bool = phong
        self.alpha: float = alpha
        if coneAxes:
            self._generateRefereneSystemCones()
        else:
            self._generateRefereneSystemArrows()

    def _generateRefereneSystemCones(self) -> None:
        sphere: Sphere = Sphere(self.radius, [1, 1, 1, 1])
        cylinderX: Cylinder = Cylinder(
            height=self.sizeFactor * 0.45,
            radiusBase=self.radius * 0.75,
            radiusTop=0.001,
            numberOfSectors=30,
            numberOfStacks=3,
            center=False,
            color=[1, 0, 0, self.alpha],
            height_direction="x",
            phong=self.phong,
        )
        cylinderY: Cylinder = Cylinder(
            height=self.sizeFactor * 0.45,
            radiusBase=self.radius * 0.75,
            radiusTop=0.001,
            numberOfSectors=30,
            numberOfStacks=3,
            center=False,
            color=[0, 1, 0, self.alpha],
            height_direction="y",
            phong=self.phong,
        )
        cylinderZ: Cylinder = Cylinder(
            height=self.sizeFactor * 0.45,
            radiusBase=self.radius * 0.75,
            radiusTop=0.001,
            numberOfSectors=30,
            numberOfStacks=3,
            center=False,
            color=[0, 0, 1, self.alpha],
            height_direction="z",
            phong=self.phong,
        )
        self.addChild(cylinderX)
        self.addChild(cylinderY)
        self.addChild(cylinderZ)
        self.addChild(sphere)

    def _generateRefereneSystemArrows(self) -> None:
        sphere: Sphere = Sphere(self.radius, [1, 1, 1, 1])
        arrowX: Arrow = Arrow(
            length=self.sizeFactor * 0.45,
            radius=self.radius * 0.75,
            pointAt=numpy.array([1.0, 0.0, 0.0]),
            color=[1.0, 0.0, 0.0, self.alpha],
            phong=False,
            radiusBaseProp=0.4,
            radiusPointerProp=0.6,
            lengthBaseProp=0.85,
            lengthPointerProp=0.15,
        )
        arrowY: Arrow = Arrow(
            length=self.sizeFactor * 0.45,
            radius=self.radius * 0.75,
            pointAt=numpy.array([0.0, 1.0, 0.0]),
            color=[0.0, 1.0, 0.0, self.alpha],
            phong=False,
            radiusBaseProp=0.4,
            radiusPointerProp=0.6,
            lengthBaseProp=0.85,
            lengthPointerProp=0.15,
        )
        arrowZ: Arrow = Arrow(
            length=self.sizeFactor * 0.45,
            radius=self.radius * 0.75,
            pointAt=numpy.array([0.0, 0.0, 1.0]),
            color=[0.0, 0.0, 1.0, self.alpha],
            phong=False,
            radiusBaseProp=0.4,
            radiusPointerProp=0.6,
            lengthBaseProp=0.85,
            lengthPointerProp=0.15,
        )
        self.addChild(arrowX)
        self.addChild(arrowY)
        self.addChild(arrowZ)
        self.addChild(sphere)

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

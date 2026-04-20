import numpy
from pynimation.common import Transform
from pynimation.common import RotationTools
from pynimation.common import _Singleton
from pynimation.common import defaults


class LightManager(metaclass=_Singleton):
    """
    Singleton class managing lights in the scene
    """

    def __init__(
        self,
        view_width: int = defaults.VIEWPORT_WIDTH,
        view_height: int = defaults.VIEWPORT_HEIGHT,
    ) -> None:
        self.lightDirection = numpy.array([-1.0, -2.0, -1.0], dtype="float32")
        self.lightSpecular = numpy.array([1.0, 1.0, 1.0], dtype="float32")
        self.lightDiffuse = numpy.array([0.7, 0.7, 0.7], dtype="float32")
        self.lightAmbient = numpy.array([0.2, 0.2, 0.2], dtype="float32")

        self.lightTarget = numpy.array([0, 1, 5], dtype="float32")

        self.lightView = Transform()
        self.lightProj = Transform()

        self.viewWidth = view_width
        self.viewHeight = view_height
        self.near = 0.5
        self.far = 50
        self.fov = 30

        self.computeViewAndProjectionMatrices()

    def computeViewAndProjectionMatrices(self) -> None:
        lightPosition = self.lightTarget - self.lightDirection * 5
        lightUpVector = numpy.array([0, 1, 0], dtype="float32")
        angle = RotationTools.unsignedAngleBetweenDeg(
            self.lightDirection, lightUpVector
        )
        if angle < 0.001 or angle > 179.999:
            lightUpVector = numpy.array([0, 0, -1], dtype="float32")

        self.lightProj.computeProjectionMatrix(
            self.viewWidth, self.viewHeight, self.fov, self.near, self.far
        )
        self.lightView.lookAt(lightPosition, self.lightTarget, lightUpVector)

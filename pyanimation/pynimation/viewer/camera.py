import numpy

from pynimation.common import Transform
from pynimation.common import defaults


class Camera:
    """
    A scene camera
    """

    def __init__(
        self,
        width: int = defaults.VIEWPORT_WIDTH,
        height: int = defaults.VIEWPORT_HEIGHT,
        near: float = 0.001,
        far: int = 1000,
        fov: int = 30,
        initPos: None = None,
        initRot: None = None,
    ) -> None:
        self.viewWidth = width
        self.viewHeight = height
        self.near = near
        self.far = far
        self.fov = fov
        self.defaultPosition = initPos or numpy.array([0.0, 0.6, 4])
        self.defaultRotation = initRot or numpy.identity(3)

        self.projectionMatrix = Transform()
        self.viewMatrix = Transform()
        self.viewMatrix.translate(self.defaultPosition)

        self.position = self.defaultPosition
        self.orientation = Transform()

        self.computeProjectionMatrix()

    def computeProjectionMatrix(self) -> None:
        """"""
        self.projectionMatrix.computeProjectionMatrix(
            self.viewWidth, self.viewHeight, self.fov, self.near, self.far
        )

    def translate(self, dx: float, dy: float, dz: float) -> None:
        """
        Translate the camera
        """
        self.viewMatrix.translate([dx, dy, dz], True)

    def rotateYaw(self, yaw: float) -> None:
        """

        Parameters
        ----------
        yaw:


        Returns
        -------

        """
        rotation = self.viewMatrix.getRotationTransform()
        position = self.viewMatrix.getPositionTransform()
        rot = Transform.rotationMatrixYDeg(yaw)
        self.viewMatrix = position * (rot * rotation)

    def rotatePitch(self, pitch: float) -> None:
        """

        Parameters
        ----------
        pitch:


        Returns
        -------

        """
        rotation = self.viewMatrix.getRotationTransform()
        position = self.viewMatrix.getPositionTransform()
        rot = Transform.rotationMatrixXDeg(pitch)
        self.viewMatrix = position * (rotation * rot)

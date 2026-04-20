import numpy
import math
from scipy.spatial.transform import Rotation
from pyquaternion import Quaternion
from .rotation_tools import RotationTools
from typing import List, Optional, cast

from .observer import _Observable


class Transform(_Observable):
    """
    A spatial 3D transform, it simplifies access and modification
    of the rotation, position and scale of the transform matrix.
    It encapsulates a transform matrix of size :code:`4x4` accessible as
    the :attr:`matrix` attribute.

    Modifications of the :class:`~pynimation.common.transform.Transform` are observable,
    :class:`~pynimation.common.observer.Observers` can register themselves
    and will be notified whenever the transform is updated. However, directly modifying
    elements of the :attr:`matrix` attribute will not trigger a notify


    Attributes
    ----------
    matrix: `numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_
        transform matrix, of size :code:`4x4`
    """

    def __init__(self, matrix: Optional[numpy.ndarray] = None) -> None:
        super().__init__()
        if matrix is None:
            self.setIdentity()
        else:
            self._matrix = matrix.copy()

    @property
    def matrix(self) -> numpy.ndarray:
        """
        transform matrix, of size :code:`4x4`

        """
        return self._matrix

    @matrix.setter
    def matrix(self, newTransform: numpy.ndarray) -> None:
        if newTransform is None:
            return
        self._matrix = newTransform
        self.notifyObservers()

    def copy(self) -> "Transform":
        """
        Get copy of the transform

        Returns
        -------
        Transform:
            a copy of the transform
        """
        return Transform(self._matrix.copy())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transform):
            raise NotImplementedError(
                "Could not compare Transform and " + other.__class__.__name__
            )

        else:
            return cast(bool, numpy.all(self.matrix == other.matrix))

    def setIdentity(self) -> None:
        """
        Set the transform to identity
        """
        self.matrix = numpy.identity(4, dtype="float64")

    def setPosition(self, position: numpy.ndarray) -> None:
        """
        Set the transform 3D position

        Parameters
        ----------
        position:
            3D position to set the transform to. Expected as an array of 3
            elements in "XYZ" order

        """
        self.matrix[0:3, 3] = numpy.array(position).transpose()
        self.notifyObservers()

    def getPosition(self) -> numpy.ndarray:
        """
        Get the 3D transform position

        Returns
        -------
        numpy.ndarray:
            3D position of the transform, as an array of 3 elements in "XYZ"
            order
        """
        return numpy.array(self.matrix[0:3, 3].transpose())

    def getPositionTransform(self) -> "Transform":
        """
        Get a transform that applies this transform's position.

        Returns
        -------
        Transform:
            a transform with this transform's position only
        """
        trans = Transform()
        trans.matrix[0:3, 3] = self.matrix[0:3, 3]
        return trans

    def translate(
        self, translation: numpy.ndarray, local: bool = False
    ) -> None:
        """
        Translate the transform's position with the :attr:`translation` vector.
        If :attr:`local` is :code:`True`, applies the transform rotation and
        scale to the translation vector.

        Parameters
        ----------
        translation:
            translation vector. Expected as an array of 3 elements in "XYZ"
            order

        local:
            wether to apply this transform's rotation and scale to the
            translation vector

        """
        if local:
            delta = numpy.matmul(self.matrix[0:3, 0:3], translation)
        else:
            delta = numpy.array(translation)

        self.matrix[0:3, 3] = self.matrix[0:3, 3] + delta
        self.notifyObservers()

    def setScale(self, scale: numpy.ndarray):
        """
        Set the scale of the transform to the :attr:`scale` vector

        Parameters
        ----------
        scale:
            scale vector. Expected as an array of 3 elements in "XYZ" order
        """
        self.matrix[0:3, 0:3] = numpy.dot(
            self.matrix[0:3, 0:3], numpy.diag(scale)
        )
        self.notifyObservers()

    def getScale(self) -> numpy.ndarray:
        """
        Get the scale vector of the transform

        Returns
        -------
        numpy.ndarray:
            the scale vector of the transform as a 3 elements array in "XYZ"
            order
        """
        return numpy.linalg.norm(self.matrix.transpose(), axis=1)[:3]

    def getScaleTransform(self) -> "Transform":
        """
        Get a transform that applies only this transform's scale

        Returns
        -------
        Transform:
            a transform with this transform's scale only
        """
        trans = Transform()
        scale = self.getScale()
        for a in range(3):
            trans.matrix[a, a] = scale[a]
        return trans

    def setRotation(self, rotation: numpy.ndarray) -> None:
        """
        Set the rotation the transform

        Parameters
        ----------
        rotation:
            rotation matrix of shape :code:`(3,3)`
        """
        scale = self.getScale()
        self.matrix[0:3, 0:3] = numpy.dot(
            numpy.array(rotation)[0:3, 0:3], numpy.diag(scale)
        )
        self.notifyObservers()

    def getRotation(self) -> numpy.ndarray:
        """
        Get the rotation matrix of the transform

        Returns
        -------
        numpy.ndarray:
            the rotation matrix of this transform, of shape :code:`(3,3)`
        """
        scale = self.getScale()
        return self.matrix[0:3, 0:3] / scale

    def getQuaternion(self) -> Quaternion:
        """
        Get the rotation of this transform as a :class:`Quaternion` object,
        from the `pyquaternion <https://kieranwynn.github.io/pyquaternion/>`_
        package

        Returns
        -------
        Quaternion:
            the rotation of this transform as a :class:`Quaternion` object
        """
        return Quaternion(matrix=self.getRotation())

    def setQuaternion(self, quat):
        """
        Set the rotation of this transform from a :class:`Quaternion` object,
        from the `pyquaternion <https://kieranwynn.github.io/pyquaternion/>`_
        package

        Parameters
        ----------
        quat:
            the quaternion that will be set to this transform's rotation
        """
        self.setRotation(quat.rotation_matrix)

    def setAxisAngle(self, axis, angle):
        """
        Set the rotation of this transform from an axis angle representation

        Parameters
        ----------
        axis:
            axis of the rotation to set as this transform's rotation
        angle:
            angle of the rotation to set as this transform's rotation
        """
        self.setQuaternion(Quaternion(axis=axis, angle=angle))

    def getRotationTransform(self) -> "Transform":
        """
        Get a transform that applies this transform's rotation

        Returns
        -------
        Transform:
            a transform with this transform's rotation only
        """
        trans = Transform()
        trans.matrix[0:3, 0:3] = self.getRotation()
        return trans

    def rotate(self, rotation: numpy.ndarray) -> None:
        """
        Rotate this transform with by the :attr:`rotation` matrix

        Parameters
        ----------
        rotation:
            rotation matrix by which to rotate this transform, expected of
            shape :code:`(3,3)`
        """
        rot = self.getRotation()
        self.matrix[0:3, 0:3] = numpy.matmul(rot, rotation)
        self.notifyObservers()

    def inverse(self) -> "Transform":
        """
        Get this transform's inverse

        Returns
        -------
        Transform:
            the inverse of this transform
        """
        return Transform(numpy.linalg.inv(self.matrix))

    def transpose(self) -> "Transform":
        """
        Get this transform's transpose

        Returns
        -------
        Transform:
            the transpose of this transform
        """
        return Transform(self.matrix.transpose())

    def getXVector(self) -> numpy.ndarray:
        """
        Get this transform's X vector (1st column vector)

        Returns
        -------
        numpy.ndarray:
            X vector of this transform
        """
        return self.matrix[0:3, 0].transpose()

    def getYVector(self) -> numpy.ndarray:
        """
        Get this transform's Y vector (1st column vector)

        Returns
        -------
        numpy.ndarray:
            Y vector of this transform
        """
        return self.matrix[0:3, 1].transpose()

    def getZVector(self) -> numpy.ndarray:
        """
        Get this transform's Z vector (1st column vector)

        Returns
        -------
        numpy.ndarray:
            Z vector of this transform
        """
        return self.matrix[0:3, 2].transpose()

    def __mul__(self, other: "Transform") -> "Transform":
        if not isinstance(other, Transform):
            raise Exception(
                "Cannot multiply Transform and " + str(type(other))
            )
        return Transform(numpy.matmul(self.matrix, other.matrix))

    def __imul__(self, other: "Transform") -> None:
        if not isinstance(other, Transform):
            raise Exception(
                "Cannot multiply Transform and " + str(type(other))
            )
        self.matrix = numpy.matmul(self.matrix, other.matrix)

    @staticmethod
    def rotationMatrixXDeg(angle: float) -> "Transform":
        """
        Get a transform rotating by :attr:`angle` degrees around the X
        axis

        Parameters
        ----------
        angle:
            angle of the rotation in degrees


        Returns
        -------
        Transform:
            transform rotating :attr:`angle` degrees around the X axis

        """
        angle = math.radians(angle)
        cx = math.cos(angle)
        sx = math.sin(angle)
        return Transform(
            numpy.array(
                [[1, 0, 0, 0], [0, cx, sx, 0], [0, -sx, cx, 0], [0, 0, 0, 1]],
                dtype="float64",
            )
        )

    @staticmethod
    def rotationMatrixYDeg(angle: float) -> "Transform":
        """
        Get a transform rotating by :attr:`angle` degrees around the Y
        axis

        Parameters
        ----------
        angle:
            angle of the rotation in degrees


        Returns
        -------
        Transform:
            transform rotating :attr:`angle` degrees around the Y axis

        """
        angle = math.radians(angle)
        cy = math.cos(angle)
        sy = math.sin(angle)
        return Transform(
            numpy.array(
                [[cy, 0, -sy, 0], [0, 1, 0, 0], [sy, 0, cy, 0], [0, 0, 0, 1]],
                dtype="float64",
            )
        )

    @staticmethod
    def rotationMatrixZDeg(angle: float) -> "Transform":
        """
        Get a transform rotating by :attr:`angle` degrees around the Z
        axis

        Parameters
        ----------
        angle:
            angle of the rotation in degrees


        Returns
        -------
        Transform:
            transform rotating :attr:`angle` degrees around the Z axis

        """
        angle = math.radians(angle)
        cz = math.cos(angle)
        sz = math.sin(angle)
        return Transform(
            numpy.array(
                [[cz, sz, 0, 0], [-sz, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                dtype="float64",
            )
        )

    def computeProjectionMatrix(
        self,
        viewWidth: int,
        viewHeight: int,
        fov: int,
        near: float,
        far: int,
    ) -> None:
        """
        Set this transform to the projection matrix for the frustum of
        dimensions :attr:`viewWidth`, :attr:`viewHeight`, :attr:`fov`,
        :attr:`near` and :attr:`far`

        Parameters
        ----------
        viewWidth:
            width of the viewport in pixels

        viewHeight:
            height of the viewport in pixels

        fov:
            field of view

        near:
            distance of the near plane

        far:
            distance of the far plane
        """
        aspect = viewWidth / viewHeight
        fovRad = numpy.radians(fov)
        range = math.tan(fovRad / 2.0) * near

        sx = (2.0 * near) / (range * aspect + range * aspect)
        sy = near / range
        sz = -(far + near) / (far - near)
        pz = -(2.0 * far * near) / (far - near)

        self.setIdentity()
        self.matrix[0, 0] = sx
        self.matrix[1, 1] = sy
        self.matrix[2, 2] = sz
        self.matrix[2, 3] = pz
        self.matrix[3, 2] = -1.0

    def lookAt(
        self,
        cameraPos: numpy.ndarray,
        targetPos: numpy.ndarray,
        upVector: numpy.ndarray,
    ) -> None:
        """
        Set this transform to a view matrix using the opengl lookAt style. COLUMN ORDER.

        Parameters
        ----------
        cameraPos:
            position of the camera in 3D space, expected as an array of 3
            elements in "XYZ" order

        targetPos:
            position of the target to look at, expected as an array of 3
            elements in "XYZ" order

        upVector:
            vector indicating the roll rotation, expected as an array of 3
            elements in "XYZ" order

        """
        self.setIdentity()
        p = Transform()
        p.setPosition(-cameraPos)
        # p = translate (p, vec3 (-cam_pos.v[0], -cam_pos.v[1], -cam_pos.v[2]))
        ori = Transform()
        ori.lookAtOrientation(cameraPos, targetPos, upVector)
        self.matrix = (ori * p).matrix

    def lookAtOrientation(
        self,
        cameraPos: numpy.ndarray,
        targetPos: numpy.ndarray,
        upVector: numpy.ndarray,
    ) -> None:
        d = targetPos - cameraPos  # distance vector
        fwd = RotationTools.normalize(d)  # forward vector
        right = RotationTools.normalize(
            numpy.cross(fwd, upVector)
        )  # right vector
        up = RotationTools.normalize(numpy.cross(right, fwd))  # real up vector

        self.matrix[0, 0] = right[0]
        self.matrix[1, 0] = right[1]
        self.matrix[2, 0] = right[2]
        self.matrix[0, 1] = up[0]
        self.matrix[1, 1] = up[1]
        self.matrix[2, 1] = up[2]
        self.matrix[0, 2] = -fwd[0]
        self.matrix[1, 2] = -fwd[1]
        self.matrix[2, 2] = -fwd[2]
        self.notifyObservers()

    @staticmethod
    def rotationMatrixAlignVectors(
        vFrom: numpy.ndarray, vTo: numpy.ndarray
    ) -> "Transform":
        # TODO: confirm behaviour is what docstring describes
        """
        Get the transform that aligns vector :attr:`vFrom` with vector
        :attr:`vTo`

        Parameters
        ----------
        vFrom:
            vector to align to :attr:`vTo`

        vTo:
            vector to align :attr:`vFrom` to

        Returns
        -------
        Transform:
            a transform that aligns vector :attr:`vFrom` with vector
            :attr:`vTo`

        """
        rot = Transform()
        vF = RotationTools.normalize(vFrom.copy())
        vT = RotationTools.normalize(vTo.copy())

        angle = numpy.clip(numpy.dot(vF, vT), -1, 1)
        angle = math.acos(angle)
        if angle > 0:
            n = numpy.cross(vF, vT)
            if numpy.linalg.norm(n) == 0:
                n = [1, 1, 1]
                if vFrom[2] != 0:
                    n[2] = -(vFrom[0] * n[0] + vFrom[1] * n[1]) / (vFrom[2])
                elif vFrom[1] != 0:
                    n[1] = -(vFrom[0] * n[0] + vFrom[2] * n[2]) / (vFrom[1])
                elif vFrom[0] != 0:
                    n[0] = -(vFrom[1] * n[1] + vFrom[2] * n[2]) / (vFrom[0])
            n = RotationTools.normalize(n) * angle
            rot.setRotation(Rotation.from_rotvec(n).as_matrix())
        return rot

    @staticmethod
    def interpolate(
        transforms: List["Transform"], weigths: numpy.ndarray
    ) -> "Transform":
        # TODO: clarify behaviour for more than 2 transforms as input
        """
        Interpolate :attr:`transforms` given :attr:`weights`

        Parameters
        ----------
        transforms:
            transforms to interpolate

        weigths:
            weights associated to each transform


        Returns
        -------
        Transorm:
            interpolated transform

        """
        q = transforms[0].getQuaternion()
        p = transforms[0].getPosition()
        w = weigths[0]
        for i in range(1, len(transforms)):
            alpha = w / (w + weigths[i])
            qt = transforms[i].getQuaternion()
            pt = transforms[i].getPosition()
            q = Quaternion.slerp(q, qt, 1.0 - alpha)
            p = alpha * p + (1 - alpha) * pt
            w += weigths[i]

        transf = Transform()
        transf.setRotation(q.rotation_matrix)
        transf.setPosition(p)
        return transf

    @staticmethod
    def computeXZOffset(
        fromTransform: "Transform", toTransform: "Transform"
    ) -> "Transform":
        """
        Compute offset transformation from :attr:`fromTransform` to
        :attr:`toTransform` with regard to the XZ position and Y rotation

        Parameters
        ----------
        fromTransform:
            base transform of the offset

        toTransform:
            target transform of the offset

        Returns
        -------
        Transform:
            offset transformation

        """

        offsetPosition = (fromTransform.inverse() * toTransform).getPosition()
        offsetPosition[1] = 0

        fromXVector = fromTransform.getXVector().copy()
        toXVector = toTransform.getXVector().copy()
        fromXVector[1] = 0
        toXVector[1] = 0
        angle = RotationTools.signedAngleBetweenDeg(
            toXVector, fromXVector, RotationTools.getAxis("Y")
        )

        offsetTransform = Transform.rotationMatrixYDeg(angle)
        offsetTransform.setPosition(offsetPosition)

        return offsetTransform

    def extractXZTransform(self) -> "Transform":
        """
        Extract the XZ transformation (XZ position and Y rotation) of this
        transform

        Returns
        -------
        Transform:
            XZ transformation of this transform

        """

        return Transform.computeXZOffset(Transform(), self)

import collections
import inspect
from pyquaternion import Quaternion
from pynimation.common import Transform
from pynimation.common import RotationTools
from pynimation.common import _Observable
from pynimation.common import _Observer
from .skeleton import Skeleton
from typing import List, Optional, Any, MutableSequence
import numpy


class Frame(_Observer):
    """
    A frame of an animation. This class regroups the local and global
    transforms of each joint of the animation's skeleton at a particular
    frame. The :attr:`localTransforms` attribute is the main interface to edit
    the animation


    Attributes
    ----------

    skeleton: Skeleton
        The skeleton that is animated. The transformation of each
        :class:`~pynimation.anim.joint.Joint` :code:`j` of the
        :class:`~pynimation.anim.skeleton.Skeleton` is accessible in
        :attr:`localTransforms` as :code:`frame.localTransforms[j.id]`.
        The skeleton of a frame must be the same as the skeleton of its
        animation

    nbJoints: int
        number of joints of the frame's skeleton
    """

    class _FrameTransformList(collections.abc.MutableSequence):
        def __init__(
            self, frame: "Frame", list: Optional[List[Transform]] = None
        ):
            self.frame = frame
            self._list = list or []

        def __setitem__(self, i, value) -> None:
            if not issubclass(value.__class__, Transform):
                raise ValueError(
                    "Cannot add value of type "
                    + value.__class__.__name__
                    + " to list of Transform"
                )

        def __getitem__(self, i) -> Any:
            return self._list[i]

        def __contains__(self, item) -> bool:
            return item in self._list

        def __len__(self) -> int:
            return len(self._list)

        def index(self, item, *args):
            return self._list.index(item, *args)

        def __delitem__(self, i) -> Any:
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def __add__(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def insert(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def append(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def extend(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def remove(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def pop(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def reverse(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def sort(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        def clear(*args, **kwargs):
            Frame._FrameTransformList._raiseNotImplemented(
                inspect.stack()[0][3]
            )

        @staticmethod
        def _raiseNotImplemented(funcName: str) -> None:
            raise NotImplementedError(
                "cannot call " + funcName + " on immutable TransformList"
            )

    class _FrameLocalTransformList(_FrameTransformList):
        def __init__(
            self, frame: "Frame", list: Optional[List[Transform]] = None
        ) -> None:
            super().__init__(frame, list)

        def __setitem__(self, i, value) -> None:
            super().__setitem__(i, value)
            self.frame._invalidateRecursive(i)
            self._list[i]._matrix = value._matrix

    class _FrameGlobalTransformList(_FrameTransformList):
        def __init__(
            self, frame: "Frame", list: Optional[List[Transform]] = None
        ) -> None:
            super().__init__(frame, list)

        def __setitem__(self, i, value) -> None:
            super().__setitem__(i, value)
            if i != 0:
                raise AttributeError(
                    "Could not set globalTransform of non root joint"
                )
            else:
                self._list[0]._matrix = value._matrix
                # globalTransform[0] == localTransform[0] should always be
                # true
                self.frame._localTransforms._list[0]._matrix = value._matrix
                self.frame._invalidateRecursive(0)

        def __getitem__(self, i) -> Any:
            if not self.frame._valid[i]:
                self.frame.update(i)
            return self._list[i]

    def __init__(self, skeleton: Skeleton) -> None:
        self.skeleton = skeleton

        self.nbJoints = len(self.skeleton.joints)
        self._localTransforms = Frame._FrameLocalTransformList(
            self, [Transform() for a in range(self.nbJoints)]
        )
        self._globalTransforms = Frame._FrameGlobalTransformList(
            self, [Transform() for a in range(self.nbJoints)]
        )
        self._valid = [True for a in range(self.nbJoints)]
        for transform in [
            *self._localTransforms._list,
            *self._globalTransforms._list,
        ]:
            transform.registerObserver(self)

    @property
    def globalTransforms(self) -> _FrameGlobalTransformList:
        """
        Global transforms of the skeleton's joints. Transforms are indexed like
        the skeleton's joints.
        Elements of this list are automatically invalidated when their
        corresponding local transforms are updated, or the global transform of
        an ancestor is invalidated.
        Invalid global transforms are recomputed when accessed

        Note
        ----
        Except for the global transform of the root joint, the global transform list
        cannot be modified directly


        Examples
        --------
        >>> # Get the global transform of joint id 4 of this frame
        >>> frame.globalTransforms[4]

        >>> # the global transform of a non root joint cannot be set
        >>> frame.globalTransforms[4] = Transform()
        Traceback (most recent call last):
          File "examples/offset.py", line 12, in <module>
            animation.frames[0].globalTransforms[1] = Transform()
          File "/home/robin/src/pynimation/pynimation/anim/frame.py", line 136, in __setitem__
            raise AttributeError(
        AttributeError: Could not set globalTransform of non root joint
        """
        return self._globalTransforms

    @globalTransforms.setter
    def globalTransforms(
        self, newGlobalTransforms: MutableSequence[Transform]
    ) -> None:
        raise AttributeError(
            "cannot set globalTransforms attribute, please set localTransforms"
            + "and compute globalTransforms using updateRecursive()"
        )

    @property
    def localTransforms(self) -> _FrameLocalTransformList:
        """
        Local transforms of the skeleton's joints. Transforms are indexed like
        the skeleton's joints. Modifying this list or any of its elements will
        invalidate global transforms of the corresponding joints and those of
        their descendants. Invalid global transforms will then be computed
        automatically when accessed.

        Note
        ----
        Modifying the transform matrix elements directly will not invalidate
        the global transforms

        Examples
        --------
        >>> # Get the local transform of joint id 4 of this frame
        >>> frame.localTransforms[4]

        >>> # Set the local transform of joint id 4 of this frame
        >>> frame.localTransforms[4] = Transform()
        """
        return self._localTransforms

    @localTransforms.setter
    def localTransforms(
        self, newLocalTransforms: MutableSequence[Transform]
    ) -> None:
        if len(newLocalTransforms) != self.nbJoints:
            raise ValueError(
                "number of transforms does not match number of joints"
            )
        for (i, transform) in enumerate(newLocalTransforms):
            self._localTransforms[i]._matrix = transform._matrix
        self._invalidateRecursive(self.skeleton.root.id)

    def _invalidateRecursive(self, from_: Optional[int] = None):
        if from_ is None:
            from_ = self.skeleton.root.id
        if not self._valid[from_]:
            # assume descendants we correctly invalidated
            return
        self._valid[from_] = False
        for child in self.skeleton.joints[from_].children:
            self._invalidateRecursive(child.id)

    def update(self, id: Optional[int] = None):
        """
        Recompute global transform of joint :attr:`id`

        Parameters
        ----------
        id:
            id of the joint whose global transform will be recomputed

        """
        boneId = id or self.skeleton.root.id
        boneParent = self.skeleton.joints[boneId].parent

        if boneParent is None:
            parentTransform = numpy.identity(4)
        else:
            # accessing globalTransforms[parent] rather _globalTransforms[parent]
            # implicitly calls update() on it if it is invalid
            # via _FrameGobalTransformList.__getitem__
            parentTransform = self.globalTransforms[boneParent.id]._matrix

        self.globalTransforms._list[boneId]._matrix = numpy.dot(
            parentTransform,
            numpy.dot(
                self.skeleton.joints[boneId].transform._matrix,
                self.localTransforms[boneId]._matrix,
            ),
        )
        self._valid[boneId] = True

    def updateRecursive(self, from_: Optional[int] = None):
        """
        Recompute global transform of joint :attr:`from_` and its descendants

        Parameters
        ----------
        id:
            id of the joint from which to recompute global transforms
        """
        if from_ is None:
            from_ = 0
        self.update(from_)
        for child in self.skeleton.joints[from_].children:
            self.updateRecursive(child.id)

    def notify(self, observable: _Observable, *args, **kwargs) -> None:
        """
        Notify of a transform update

        Parameters
        ----------
        observable:
            transform that was updated
        """
        try:
            index = self.localTransforms.index(observable)
            self._invalidateRecursive(index)
        except ValueError:
            # observable is not a local transform
            try:
                index = self.globalTransforms.index(observable)
                if index != 0:
                    raise AttributeError(
                        "Could not mutate global Transform of non root joint"
                    )
                else:
                    # globalTransform[0] == localTransform[0] should always be
                    # true
                    # globalTransform[0] is not accessed directly so it is not
                    # overwritten by localTransform[0]
                    self.localTransforms[
                        0
                    ]._matrix = self._globalTransforms._list[0]._matrix
                    self._invalidateRecursive(0)
            except ValueError:
                print("Got notified by a Transform we do not have")

    def copy(self):
        """
        Copy this frame

        Returns
        -------
        Frame:
            copy of this frame
        """
        fr = Frame(self.skeleton)
        for i in range(len(self.localTransforms)):
            fr.localTransforms[i].matrix = self.localTransforms[i].matrix.copy()
        fr._invalidateRecursive()
        return fr

    def setBonePosition(self, boneId: int, position: numpy.ndarray) -> None:
        """
        Set position of :attr:`boneId`

        Parameters
        ----------
        boneId:
            id of the bone whose position will be set

        position:
            position to be set, expected as an 3 element array in "XYZ" order

        """
        self.localTransforms[boneId].setPosition(position)

    def setBoneLocalRotationEuler(
        self,
        boneId: int,
        seq: str,
        angles: numpy.ndarray,
        degrees: bool = False,
    ) -> None:
        """
        Set local rotation of :attr:`boneId` with a rotation specified as Euler
        :attr:`angles` in :attr:`degrees` or not and with order :attr:`seq`

        Parameters
        ----------
        boneId:
            id of the bone whose rotation will be set

        seq:
            axis order, for example : "xyz"

        angles:
            euler angles specifying the rotation

        degrees:
            wether the euler angles are represented in degrees (:code:`True`)
            of radians (:code:`False`)

        """
        _axis = RotationTools.getAxis(seq[0])
        if degrees:
            Q = Quaternion(axis=_axis, degrees=angles[0])
            for i in range(1, len(seq)):
                _axis = RotationTools.getAxis(seq[i])
                Q = Q * Quaternion(axis=_axis, degrees=angles[i])
        else:
            Q = Quaternion(axis=_axis, radian=angles[0])
            for i in range(1, len(seq)):
                _axis = RotationTools.getAxis(seq[i])
                Q = Q * Quaternion(axis=_axis, radian=angles[i])

        self.setBoneLocalRotation(boneId, Q.rotation_matrix)

    def setBoneLocalRotation(
        self, boneId: int, rotation: numpy.ndarray
    ) -> None:
        """
        Set local rotation of bone :attr:`boneId` to rotation matrix
        :attr:`rotation`

        Parameters
        ----------
        boneId:
            bone whose rotation will be set

        rotation:
            rotation matrix of shape :code:`(3,3)`

        """
        self.localTransforms[boneId].setRotation(rotation)

    def getRootPosition(self) -> numpy.ndarray:
        """
        Get the position of the root joint for this frame
        Returns
        -------
        numpy.ndarray:
            global position of bone :attr:`boneId` as an array of 3 elements in
            "XYZ" order
        """
        return self.localTransforms[self.skeleton.root.id].getPosition()

    def getBoneGlobalPosition(self, boneId: int) -> numpy.ndarray:
        """
        Get the global position of bone :attr:`boneId`

        Parameters
        ----------
        boneId:
            ID of the bone


        Returns
        -------
        numpy.ndarray:
            global position of bone :attr:`boneId` as an array of 3 elements in
            "XYZ" order

        """
        return self.getBoneGlobalTransform(boneId).getPosition()

    def getBoneGlobalTransform(self, boneId: int) -> numpy.ndarray:
        """
        Get the global transform of bone :attr:`boneId`

        Parameters
        ----------
        boneId:
            ID of the bone


        Returns
        -------
        Transform:
            global transform of bone :attr:`boneId`
        """
        return self.globalTransforms[boneId]

    def getBoneLocalTransform(self, boneId: int) -> numpy.ndarray:
        """
        Get the local transform of bone :attr:`boneId`

        Parameters
        ----------
        boneId:
            ID of the bone


        Returns
        -------
        Transform:
            local transform of bone :attr:`boneId`
        """
        return self.localTransforms[boneId]

    @staticmethod
    def interpolate(frames: List["Frame"], weights: numpy.ndarray) -> "Frame":
        # TODO : confirm behaviour for more than 2 frames
        """
        Compute the interpolation of :attr:`frames` with :attr:`weights`. Uses
        spherical interpolation for the rotation

        Parameters
        ----------
        frames:
            frames to interpolate

        weights:
            weights of each frame

        Returns
        -------
        Frame:
            the interpolated frame

        """
        if len(frames) != len(weights):
            raise ValueError(
                "number of frames has to match number of weights, got "
                + str(len(frames))
                + " frames and "
                + str(len(weights))
                + " weights"
            )

        for i in range(1, len(frames)):
            if frames[i].skeleton != frames[0].skeleton:
                raise ValueError(
                    "Skeleton of frame "
                    + str(i)
                    + " differs from skeleton of frame 0"
                )

        fr = Frame(frames[0].skeleton)
        for i in range(len(frames[0].localTransforms)):
            fr.localTransforms[i] = Transform.interpolate(
                [fr.localTransforms[i] for fr in frames], weights
            )

        return fr

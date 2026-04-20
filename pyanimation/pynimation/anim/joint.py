from typing import Optional, Tuple, TYPE_CHECKING, cast, TypeVar, Generic
import numpy
from pynimation.common import Transform
from pynimation.common import TransformNode

if TYPE_CHECKING:
    from .skeleton import Skeleton

JointLike = TypeVar("JointLike", bound="Joint")


class Joint(Generic[JointLike], TransformNode[JointLike]):
    """
    Joint of a :class:`~pynimation.anim.skeleton.Skeleton`
    """

    def __init__(
        self,
        name: str,
        parent: Optional[JointLike] = None,
        children: Optional[Tuple[JointLike, ...]] = None,
        position: numpy.ndarray = [],
        orientation: numpy.ndarray = [],
    ) -> None:
        super().__init__(name, parent, children, None)
        if len(position) > 0:
            self.transform.setPosition(position)
        if len(orientation) > 0:
            self.transform.setRotation(orientation)
        self._id: int = self._getIdFromSkeleton()

    @property
    def id(self) -> int:
        """
        id of the joint
        """
        if self._id == -1:
            self._id = self._getIdFromSkeleton()
        return self._id

    @property
    def skeleton(self) -> Optional["Skeleton"]:
        """
        skeleton of the joint
        """
        return cast(Skeleton, self._graph)

    def _getIdFromSkeleton(self) -> int:
        if self._graph is not None:
            return self._graph.nodes.index(self)
        else:
            return -1

    def getInverseBindMatrix(self) -> Transform:
        """
        Computes the inverse of the global transform of the joint
        """
        return self.globalTransform.inverse()

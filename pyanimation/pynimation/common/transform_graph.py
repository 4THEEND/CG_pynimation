import inspect
import collections
from typing import (
    Optional,
    Tuple,
    Generic,
    TypeVar,
    Any,
    List,
    MutableSequence,
)
import numpy
from .transform import Transform
from .graph import Graph
from .graph import Node
from .observer import _Observer
from .observer import _Observable

TransformNodeLike = TypeVar("TransformNodeLike", bound="TransformNode")


class TransformNode(
    Generic[TransformNodeLike], Node[TransformNodeLike], _Observer
):
    """
    A node of :class:`~pynimation.common.transform_graph.TransformGraph`. Each
    node has a :attr:`transform` (that is local) and a :attr:`globalTransform`.
    A node global transform is equal to the dot product of its ancestors'
    transforms and of its own. This property allows defining a common transform
    for multiple nodes.
    Modifying a node's local transform will invalidate its global transform and
    those of its children. Global transforms are recomputed when accessed

    Examples
    --------
    >>> root = TransformNode("root")
    >>> n1 = TransformNode("1", parent=root)
    >>> n1.globalTransform.isIdentity()
    True
    >>> root.transform.setPosition([1,1,1])
    >>> n1.globalTransform.getPosition()
    [1,1,1]
    """

    def __init__(
        self,
        name: str,
        parent: Optional[TransformNodeLike] = None,
        children: Optional[Tuple[TransformNodeLike, ...]] = None,
        graph: Optional["TransformGraph"] = None,
    ) -> None:
        self._transform = Transform()
        self._globalTransform = Transform()
        self._transform.registerObserver(self)
        self._globalTransform.registerObserver(self)
        self._valid = True
        super().__init__(name, parent, children, graph)

    @property
    def valid(self) -> bool:
        """
        Is the global transform of this node valid.
        Global transforms of invalid nodes will be recomputed when accessed
        Setting this property will invalidate the children descendants.

        Examples
        --------
        >>> node.valid
        True
        >>> node.children[0].valid
        True
        >>> node.transform = Transform()
        >>> node.valid
        False
        >>> node.children[0].valid
        False
        >>> node.globalTransform
        <pynimation.common.transform.Transform object at 0x7effe85b7130>
        >>> node.valid
        True
        """
        return self._valid

    @valid.setter
    def valid(self, newValue: bool) -> None:
        if self._valid == newValue:
            return

        if newValue:
            if self.parent is not None:
                if not self.parent._valid:
                    raise AttributeError(
                        "Could not set TransformNode as valid when parent is not"
                    )
                shouldBe = self.parent._globalTransform * self.transform
            else:
                shouldBe = self.transform
            if self._globalTransform != shouldBe:
                raise AttributeError(
                    "Could not set TransformNode as valid as it appears it is not (globalTransform != parent.globalTransform * transform)"
                )
        else:
            self._invalidateRecursive()

        self._valid = newValue

    @property
    def transform(self) -> Transform:
        """
        local transform of the node. Setting of modifying it will invalidate
        the node's global transform.

        Note
        ----
        Directly modifying the matrix elements like :
        :code:`node.transform.matrix[0][0] = 1` will not invalidate it
        """
        return self._transform

    @transform.setter
    def transform(self, newTransform: Transform) -> None:
        if newTransform is None or self._transform == newTransform:
            return
        self._transform._matrix = newTransform.matrix.copy()
        self._invalidateRecursive()

    @property
    def globalTransform(self) -> Transform:
        """
        global transform of this node. Accessing this transform will recompute
        it if it is invalid
        """
        if not self._valid:
            self.update()
        return self._globalTransform

    @globalTransform.setter
    def globalTransform(self, newGlobalTransform: Transform) -> None:
        if newGlobalTransform is None:
            return
        self._globalTransform._matrix = newGlobalTransform.matrix.copy()
        self._updateTransformFromGlobalTransform()
        self._invalidateRecursive()

    def _updateTransformFromGlobalTransform(self):
        self._transform.unregisterObserver(self)
        if self.parent is not None:
            self._transform._matrix = numpy.dot(
                self.parent.globalTransform.inverse().matrix,
                self._globalTransform.matrix,
            )
        else:
            self._transform._matrix = self._globalTransform.matrix.copy()
        self._transform.registerObserver(self)

    def _invalidateRecursive(self):
        self._valid = False
        for child in self.children:
            child._invalidateRecursive()

    def update(self) -> None:
        """
        Recompute this node's globalTransform
        """
        # modifying matrix directly avoid having to register
        # observers on a new Transform
        # accessing _matrix rather than matrix ensures that we don't get
        # notified of our own changes
        if self.parent is not None:
            self._globalTransform._matrix = numpy.dot(
                self.parent.globalTransform.matrix, self.transform.matrix
            )
        else:
            self._globalTransform._matrix = self.transform.matrix.copy()
        self._valid = True

    def updateRecursive(self) -> None:
        """
        Recompute this node and its children globalTransforms
        """
        self.update()
        for child in self.children:
            child.updateRecursive()

    def notify(self, observable: _Observable, *args, **kwargs):
        """
        Notify of a transform change
        """
        if observable is self._globalTransform:
            self._updateTransformFromGlobalTransform()
        self._invalidateRecursive()


class TransformGraph(Generic[TransformNodeLike], Graph[TransformNodeLike]):
    """
    A graph of :class:`~pynimation.common.transform_graph.TransformNode`.
    """

    def __init__(self, root: TransformNodeLike) -> None:
        super().__init__(root)
        self._globalTransforms = _TransformList(self._nodes, "globalTransform")
        self._localTransforms = _TransformList(self._nodes, "transform")

    @property
    def globalTransforms(self) -> MutableSequence[Transform]:
        """
        List of the globalTransforms of all the nodes
        """
        return self._globalTransforms

    @property
    def transforms(self) -> MutableSequence[Transform]:
        """
        List of the local transforms of all the nodes
        """
        return self._localTransforms

    def add(
        self,
        node: TransformNodeLike,
        parent: Optional[TransformNodeLike] = None,
    ) -> None:
        # FIXME: test is needed because of recursive calls, but lookup is slow
        # maybe keep a list of names ? or construct and test against it here ?
        if node in self._nodes:
            return
        super().add(node, parent)
        node._invalidateRecursive()

    def updateAll(self) -> None:
        """
        Recompute the global transforms of all nodes
        """
        for node in self.nodes:
            node.update()


class _TransformList(collections.abc.MutableSequence):  # type: ignore
    def __init__(self, initlist: List[TransformNodeLike] = [], attrname=""):
        self.attrname = attrname
        self._nodes = initlist

    def _getlist(self) -> List["Transform"]:
        return [getattr(a, self.attrname) for a in self._nodes]

    def __setitem__(self, i, value) -> None:
        setattr(self._nodes[i], self.attrname, value)

    def __getitem__(self, i) -> Any:
        return getattr(self._nodes[i], self.attrname)

    def __contains__(self, item) -> bool:
        return item in self._getlist()

    def __len__(self) -> int:
        return len(self._nodes)

    def index(self, item, *args):
        self._getlist.index(item, *args)

    def __delitem__(self, i) -> Any:
        _TransformList._raiseNotImplemented()

    def __add__(*args, **kwargs):
        _TransformList._raiseNotImplemented()

    def insert(*args, **kwargs):
        _TransformList._raiseNotImplemented()

    def append(*args, **kwargs):
        _TransformList._raiseNotImplemented()

    def extend(*args, **kwargs):
        _TransformList._raiseNotImplemented()

    def reverse(*args, **kwargs):
        _TransformList._raiseNotImplemented()

    def sort(*args, **kwargs):
        _TransformList._raiseNotImplemented()

    def clear(*args, **kwargs):
        _TransformList._raiseNotImplemented()

    @staticmethod
    def _raiseNotImplemented() -> None:
        raise NotImplementedError(
            "cannot call " + inspect.stack()[1][3] + " on _TransformList"
        )

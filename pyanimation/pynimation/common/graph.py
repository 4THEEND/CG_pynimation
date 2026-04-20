import json
from typing import TypeVar, Generic, Tuple, Dict, Optional, List, Any

NodeLike = TypeVar("NodeLike", bound="Node")


class Graph(Generic[NodeLike]):
    """
    A generic graph. Manages parent/children relationships and a list of
    nodes through node addition/deletion
    """

    def __init__(self, root: NodeLike) -> None:
        self._nodes: List[NodeLike] = []
        self._root: NodeLike = root
        self._initRoot()
        self._hash = self._computeHash()

    def __str__(self) -> str:
        return str(self._root)

    def hasSameTopology(self, other: object) -> bool:
        """
        Determine if this graph and :attr:`other` have the same topology and
        nodes with the same names. This method is relatively inexpensive as it
        uses a hash that is recomputed every time the graph is modified

        Parameters
        ----------
        other:
            graph to compare topology with

        Raises
        ------
        NotImplementedError:
            If other is not a subclass of graph

        Returns
        -------
        boolean:
            does this graph and :attr:`other` have the same topology

        """
        # ensure we can access _hash
        if issubclass(other.__class__, Graph):
            return self._hash == other._hash  # type: ignore
        else:
            raise NotImplementedError(
                "cannot compare "
                + self.__class__.__name__
                + " to "
                + other.__class__.__name__
            )

    @property
    def root(self) -> NodeLike:
        """
        the root node of the graph, cannot be removed
        """
        return self._root

    @root.setter
    def root(self, newRoot: NodeLike) -> None:
        if newRoot is None:
            return
        self._removeUnsafe(self._root)
        assert len(self._nodes) == 0  # sanity check
        self._root = newRoot
        self._initRoot()
        self._hash = self._computeHash()

    @property
    def nodes(self) -> Tuple[NodeLike, ...]:
        """
        list of all nodes of the graph, is updated automatically on node
        addition/deletion
        """
        # return tuple to prevent user from touching the original
        return tuple(self._nodes)

    def _initRoot(self) -> None:
        self._root.parent = None
        self._root._graph = self
        self._nodes.append(self._root)
        for child in self._root.children:
            self._addRecursive(child)

    def _computeHash(self) -> int:
        return hash(json.dumps(self.toDict()))

    def add(self, node: NodeLike, parent: Optional[NodeLike] = None) -> None:
        """
        Add :attr:`node` to the graph, with :attr:`parent` as its parent. if
        :attr:`parent` is :code:`None`, :attr:`node` is added to the root

        Parameters
        ----------
        node:
            node to add

        parent:
            if not :code:`None`, will add :attr:`node` as its child, otherwise
            will add to root's children

        Raises
        ------
        ValueError:
            if :attr:`parent` is not in the graph
        """
        if node in self._nodes:
            return

        node._graph = self

        # add to hashmap
        self._nodes.append(node)

        # add to parent's children
        if parent is None:
            if node.parent is None:
                node.parent = self._root
            else:
                if node.parent not in self._nodes:
                    node.parent.removeChild(node)
                    node.parent = self._root
        else:
            if parent not in self._nodes:
                raise ValueError(
                    "parent node "
                    + parent.name
                    + " was not found in the graph, maybe add it first ?"
                )
            if node not in parent.children:
                parent.addChild(node)

        # add children recursively
        for child in node.children:
            self._addRecursive(child)

        # recompute hash
        self._hash = self._computeHash()

    def _addRecursive(self, node: NodeLike) -> None:
        if node in self._nodes:
            return

        self._nodes.append(node)
        node._graph = self

        for child in node.children:
            self._addRecursive(child)

    def remove(self, node: NodeLike) -> None:
        """
        Remove :attr:`node` from graph. Will remove its children as well

        Raises
        ------
        ValueError:
            If :attr:`node` is not in the graph

        Parameters
        ----------
        node:
            node to remove
        """
        if node not in self._nodes:
            return
        if node == self._root:
            return
        self._removeUnsafe(node)

    def _removeUnsafe(self, node: NodeLike) -> None:
        # remove from hashmap
        self._nodes.remove(node)

        node._graph = None

        # remove from parent's children
        if node.parent is not None:
            node.parent.removeChild(node)

        # remove children recursively
        for child in node.children:
            self._removeRecursive(child)

        # recompute hash
        self._hash = self._computeHash()

    def _removeRecursive(self, node: NodeLike) -> None:
        if node not in self._nodes:
            return

        self._nodes.remove(node)
        node._graph = None

        for child in node.children:
            self._removeRecursive(child)

    def getNode(self, name: str) -> Optional[NodeLike]:
        """
        Search for node of :attr:`name`

        Parameters
        ----------
        name:
            name of the node to search

        Returns
        -------
        Optional[NodeLike]:

        """
        results = [a for a in self.nodes if a.name == name]
        if len(results) > 0:
            return results[0]
        else:
            return None

    @staticmethod
    def fromDict(dict_: Dict[str, Dict], classNode: Any, classGraph) -> "Any":
        """
        Construct a graph from a nested dictionary with string keys. Mainly for
        testing purposes
        """
        root = classNode.fromDict("Root", dict_, classNode, None)
        graph = classGraph(root)
        return graph

    def toDict(self) -> Dict[str, Dict]:
        """
        Get a dictionary representation of the graph. Mainly for
        testing purposes
        """
        return self._root.toDict()


class Node(Generic[NodeLike]):
    """
    A node of :class:`~pynimation.common.graph.Graph`

    Attributes
    ----------

    name:
        name of the node
    """

    def __init__(
        self,
        name: str,
        parent: Optional[NodeLike] = None,
        children: Optional[Tuple[NodeLike, ...]] = None,
        graph: Optional[Graph] = None,
    ):
        if len(name) == 0:
            name = self.__class__.__name__ + "_" + str(hash(self))
        self.name = name
        if children is None:
            children = ()
        # tuple gives immutability
        self._children: Tuple[NodeLike, ...] = children
        self._parent: Optional[NodeLike] = parent
        self._graph: "Optional[Graph]" = graph
        if self._parent is not None:
            self._graph = self._parent._graph
            self._parent.addChild(self)
        if self._graph is not None:
            self._graph.add(self, self._parent)

    def __del__(self):
        if self._parent is not None:
            self._parent.removeChild(self)
        else:
            if self._graph is not None:
                self._graph.remove(self)
        for child in self.children:
            child.parent = None

    @property
    def children(self) -> Tuple[NodeLike, ...]:
        """
        Children of the node

        Note
        ----
        A tuple is used to prevent direct modification of the set of children.
        A child can only be added with :attr:`addChild`. The set of children
        can however be replaced by a new tuple: :code:`self.children = (Node("a"), Node("b"))`
        """
        return self._children

    @children.setter
    def children(self, newChildren: Tuple[NodeLike, ...]) -> None:
        oldChildren = self._children
        self._children = newChildren

        added = [
            newChild for newChild in newChildren if newChild not in oldChildren
        ]

        for child in added:
            child.parent = self
            if self._graph is not None:
                self._graph.add(child, self)

        removed = [
            oldchild for oldchild in oldChildren if oldchild not in newChildren
        ]

        for child in removed:
            child.parent = None
            if self._graph is not None:
                self._graph.remove(child)

    @children.deleter
    def children(self):
        del self._children
        self._children = ()

    @property
    def parent(self) -> Optional[NodeLike]:
        """
        parent of the node, can be :code:`None`.
        Directly setting the parent will the graph accordingly

        Examples
        --------
        >>> # Set node's parent to another node will update the parent's
        >>> # children
        >>> node = Node("a")
        >>> node.parent = graph.root
        >>> node in graph.root.children
        True
        >>> node in graph.nodes
        True

        >>> # Set node's parent to a node that is not in the graph will remove
        >>> # it and its descendants from the graph
        >>> node.parent = Node("a")
        """
        return self._parent

    @parent.setter
    def parent(self, newParent: Optional["NodeLike"]):
        if newParent == self or newParent in self._children:
            return

        if newParent is None:
            if self._graph is not None:
                self._graph.remove(self)
            self._parent = None
            return

        # remove self from old parent's children
        if self._parent is not None:
            self._parent.removeChild(self)

        # add self to new parent's children
        newParent.addChild(self)

        self._parent = newParent

    @parent.deleter
    def parent(self):
        del self._parent
        self._parent = None

    def addChild(self, child: NodeLike) -> None:
        """
        Add :attr:`child` to the node's children

        Parameters
        ----------
        child:
            child to add to the node's children
        """
        if child in self._children or child == self:
            return

        child._graph = self._graph

        # add to children
        self._children = (*self._children, child)

        # add self as child's parent
        child.parent = self

        # add to graph
        if self._graph is not None:
            self._graph.add(child, self)

    def removeChild(self, childToRemove: NodeLike):
        """
        Remove :attr:`childToRemove` from children. Updates its parent and the
        graph

        Parameters
        ----------
        childToRemove:
            child to remove from node's children

        """
        if childToRemove not in self._children:
            return

        # remove from children
        self._children = tuple(
            [child for child in self._children if child != childToRemove]
        )

        # remove self as child's parent
        childToRemove.parent = None

        # remove from graph
        if self._graph is not None:
            self._graph.remove(childToRemove)

    def descendants(self) -> List["Node[NodeLike]"]:
        """
        Get the list of descendants, :code:`self` is excluded

        Returns
        -------
        List["Node[NodeLike]"]:
            a list of this node's descendants

        """
        descendants: List["Node[NodeLike]"] = []
        for child in self.children:
            child._descendantsRecursive(descendants)
        return descendants

    def _descendantsRecursive(
        self, descendants: List["Node[NodeLike]"]
    ) -> None:
        descendants.append(self)
        for child in self.children:
            child._descendantsRecursive(descendants)

    def toDict(self) -> Dict[str, Dict]:
        dict_: Dict[str, Dict] = {}
        for child in self.children:
            dict_[child.name] = child.toDict()
        return dict_

    @staticmethod
    def fromDict(
        name: str,
        dict_: Dict[str, Dict],
        class_: Any,
        parent: Optional[NodeLike] = None,
    ):
        node: Any = class_(name)
        if parent is not None:
            parent.addChild(node)
        children = []
        for key in dict_.keys():
            if isinstance(dict_[key], dict) and isinstance(key, str):
                children.append(Node.fromDict(key, dict_[key], class_, node))
        node.children = tuple(children)
        return node

    def __str__(self) -> str:
        return self._tostring("", [])

    def _tostring(self, tab="", visited: List["Node[NodeLike]"] = []) -> str:
        if self in visited:
            return "__CYCLE__"
        return (
            tab
            + self.name
            + "\n"
            + "\n".join(
                [
                    child._tostring(tab + "    ", visited + [self])
                    for child in self.children
                ]
            )
        )

from typing import Generic, TypeVar, Optional, Tuple
from pynimation.common import TransformGraph
from pynimation.common import TransformNode

SceneNodeLike = TypeVar("SceneNodeLike", bound="SceneNode")


class SceneNode(Generic[SceneNodeLike], TransformNode[SceneNodeLike]):
    """
    A node of :class:`~pynimation.viewer.scene_graph.SceneGraph`.
    """

    def __init__(
        self,
        name: str,
        parent: Optional[SceneNodeLike] = None,
        children: Optional[Tuple[SceneNodeLike, ...]] = None,
        graph: Optional["SceneGraph"] = None,
    ) -> None:
        super().__init__(name, parent, children, graph)
        self.hidden = False

    def display(self):
        """ """
        if self.hidden:
            return
        # TODO display Transform axes


class SceneGraph(Generic[SceneNodeLike], TransformGraph["SceneNode"]):
    """
    A graph of :class:`~pynimation.viewer.scene_graph.SceneNode`.
    """

    def __init__(self, root: SceneNodeLike) -> None:
        super().__init__(root)

from .scene_graph import SceneGraph
from .scene_graph import SceneNode
from .camera import Camera
from .light import LightManager

from .animated import Animated
from typing import Optional, List


class Scene:
    """
    Representation of a 3D Scene, with its objects, cameras and lights

    Parameters
    ----------

    cameras: Optional[List[Camera]]:
        cameras of the scene, default will be created if :code:`None`
    root: Optional[SceneNode]:
        root of the scene :attr:`graph`, default will be created if :code:`None`
    light: Optional[LightManager]:
        light manager for the scene, default will be created if :code:`None`

    Attributes
    ----------

    cameras: Optional[List[Camera]]:
        cameras of the scene
    root: Optional[SceneNode]:
        root of the scene :attr:`graph`
    graph: SceneGraph:
        scene graph of the scene, contains all the objects
    light: Optional[LightManager]:
        light manager for the scene
    """

    def __init__(
        self,
        cameras: Optional[List[Camera]] = None,
        root: Optional[SceneNode] = None,
        light: Optional[LightManager] = LightManager(),
    ):
        if root is None:
            root = SceneNode("root", None)
        self.root = root
        self.graph = SceneGraph(root)
        if cameras is None:
            cameras = []
        if len(cameras) == 0:
            cameras = [Camera()]
        self.cameras = cameras

    def addInLine(
        self,
        nodes: List["SceneNode"],
        distance: float = 1.0,
        parent: Optional["SceneNode"] = None,
    ) -> None:
        """Adds objects to the scene as children of the root node
        , aligned and separated by distance

        Parameters
        ----------
        nodes:
            nodes to add
        distance:
            distance between them
        parent:
            if not :code:`None`, will be added to this node's children
        """

        for (i, node) in enumerate(nodes):
            node.transform.translate([distance * i, 0, 0])
            self.graph.add(node, parent=parent)

    def add(
        self, node: "SceneNode", parent: Optional["SceneNode"] = None
    ) -> None:
        """Add node to scene

        Parameters
        ----------
        node: "SceneNode" :

        parent: Optional["SceneNode"] :
             (Default value = None)
        """
        self.graph.add(node, parent=parent)

    def remove(self, node: "SceneNode") -> None:
        """Remove node from scene

        Parameters
        ----------
        node:
            node to remove
        """
        self.graph.remove(node)

    def display(self):
        """
        Animate and display all nodes
        """
        for node in self.graph.nodes:
            if issubclass(node.__class__, Animated):
                node.animate()
        for node in self.graph.nodes:
            node.display()

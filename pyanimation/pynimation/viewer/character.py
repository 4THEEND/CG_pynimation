from typing import List, Optional
from pynimation.anim import Animation
from .stickfigure import StickFigure
from .scene_graph import SceneNode
from .animated import Animated
from .animatable import Animatable
from .player import Player


class Character(SceneNode, Animated):
    """
    Representation of an animated 3D character in the scene
    Holds an animation and the mesh it animates
    Responsible for animating the mesh at each frame

    Parameters
    ----------
    animation: Animation:
        animation of the character
    meshes: List[SceneNode]:
        animated meshes, must be subclass of
        :class:`~pynimation.viewer.animatable.Animatable`

    Attributes
    ----------
    animation: Animation:
        animation of the character
    meshes: List[SceneNode]:
        animated meshes, must be subclass of
        :class:`~pynimation.viewer.animatable.Animatable`
    """

    def __init__(
        self, animation: Animation, meshes: Optional[List[SceneNode]] = None
    ):
        super().__init__("")
        self.animation = animation
        if meshes is None:
            meshes = []
        if len(meshes) == 0:
            meshes.append(StickFigure(self.animation.skeleton))
        for mesh in meshes:
            self.addChild(mesh)

    def animate(self) -> None:
        """
        Animate :attr:`meshes` with :attr:`animation` at the current time
        """
        frame = self.animation.getFrameFromTime(Player().time)
        for mesh in self.children:
            assert issubclass(mesh.__class__, Animatable)
            mesh.animate(frame)  # type: ignore

from typing import Tuple, Dict, List, Callable, Any
from enum import Enum
from functools import partial


import numpy
import pygame as pg


from .viewport import Viewport
from .camera import Camera
from .objects.plane import Plane
from .scene import Scene
from .scene import SceneNode
from .player import Player
from .character import Character
from .events import EventManager
from .events import _partialsEq
from .bindings import getDefaultBindings
from pynimation.anim import Animation
from pynimation.common import defaults

from pynimation.common import data as data_


class Viewer:
    """
    Display scenes and objects with a typical main loop implementation

    Parameters
    ----------
    size: Tuple[int, int]
        size of the viewport

    Attributes
    ----------
    camera: Camera:
        camera from which the scene will be displayed

    viewport: Viewport:
        reference to viewport singleton

    player: Player:
        reference to player singleton

    cameraData: Dict[str, numpy.ndarray]
        view and projection matrix of :attr:`camera`, is updated at each frame
        according to user input
    """

    class CallbackTime(Enum):
        """
        Steps in the main loop when a callback can be called
        """

        BEFORE_EVENTS = 0
        AFTER_EVENTS = 1
        BEFORE_DISPLAY = 2
        AFTER_DISPLAY = 3

    def __init__(
        self,
        size: Tuple[int, int] = (
            defaults.VIEWPORT_WIDTH,
            defaults.VIEWPORT_HEIGHT,
        ),
    ):
        if size is not None:
            self.viewport = Viewport(*size)
        else:
            self.viewport = Viewport()
        self.camera = Camera(self.viewport.width, self.viewport.height)
        self.viewport.setMainCamera(self.camera)
        self.bindings = tuple(getDefaultBindings(self))
        self.eventManager = EventManager(self.bindings)
        self.player = Player()
        self.cameraData: Dict[str, numpy.ndarray] = {}
        self._callbacks: Dict[
            Viewer.CallbackTime, List[Tuple[int, partial]]
        ] = {}

    def addCallback(
        self,
        callback: Callable,
        when: CallbackTime = CallbackTime.BEFORE_DISPLAY,
        priority: int = 50,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> None:
        """
        Add a callback to the viewer's main loop

        Parameters
        ----------
        callback:
            function to add as callback
        when:
            when in the main loop will the callback be called
        priority:
            callbacks will be called by priority order
        args:
            arguments of the callback
        kwargs:
            keyword arguments of the callback
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        partialCallback = partial(callback, *args, **kwargs)
        self.addCallbackPartial(partialCallback, when, priority)

    def addCallbackPartial(
        self,
        partialCallback: partial,
        when: CallbackTime = CallbackTime.BEFORE_DISPLAY,
        priority: int = 50,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> None:
        """
        Add a callback to the viewer's main loop as a partial object

        Parameters
        ----------
        partialCallback:
            partial to add as callback
        when:
            when in the main loop will the callback be called
        priority:
            callbacks will be called by priority order
        args:
            arguments of the callback
        kwargs:
            keyword arguments of the callback
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        callbackEntry = (priority, partialCallback)
        if when not in self._callbacks:
            self._callbacks[when] = [callbackEntry]
        else:
            self._callbacks[when].append(callbackEntry)
            # sort by priority
            self._callbacks[when].sort(key=lambda x: x[0])

    def removeCallback(
        self,
        callback: Callable,
        when: CallbackTime = CallbackTime.BEFORE_DISPLAY,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> None:
        """
        Remove a callback from the viewer's main loop

        Parameters
        ----------
        callback:
            function to remove from callbacks
        when:
            when in the main loop is the callback called
        args:
            arguments of the callback
        kwargs:
            keyword arguments of the callback
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        partialCallback = partial(callback, args, kwargs)
        self.removeCallbackPartial(partialCallback, when)

    def removeCallbackPartial(
        self,
        partialCallback: partial,
        when: CallbackTime = CallbackTime.BEFORE_DISPLAY,
    ) -> None:
        """
        Remove a callback from the viewer's main loop

        Parameters
        ----------
        partialCallback:
            partial to remove from callbacks
        when:
            when in the main loop is the callback called
        """
        if when in self._callbacks:
            self._callbacks[when] = [
                entry
                for entry in self._callbacks[when]
                if not _partialsEq(entry[1], partialCallback)
            ]

    def _callCallbacks(self, when: CallbackTime) -> None:
        if when in self._callbacks:
            for callbackEntry in self._callbacks[when]:
                callbackEntry[1]()

    def displayScene(self, scene: Scene) -> None:
        """
        Display :attr:`scene` with this viewer
        Uses a typical main loop implementation

        Parameters
        ----------
        scene:
            scene to display
        """
        while 1:
            self._callCallbacks(Viewer.CallbackTime.BEFORE_EVENTS)

            self.eventManager.update()

            self._callCallbacks(Viewer.CallbackTime.AFTER_EVENTS)

            self.viewport.updateCamera()

            self._callCallbacks(Viewer.CallbackTime.BEFORE_DISPLAY)

            self.viewport.display()

            scene.display()

            self._callCallbacks(Viewer.CallbackTime.AFTER_DISPLAY)

            pg.display.flip()

            self.viewport.handleRecording()

            self.player.tick()

    @staticmethod
    def defaultScene() -> Scene:
        """
        Contructs an scene with :attr:`defaultFloor`

        Returns
        -------
        Scene
            empty scene with :attr:`defaultFloor`
        """
        scene = Scene()
        plane = Viewer.defaultFloor()
        scene.add(plane)
        return scene

    @staticmethod
    def defaultFloor() -> Plane:
        """
        Construct a :class:`~pynimation.viewer.objects.plane.Plane` with a
        repeating checker pattern

        Returns
        -------
        Plane
            plane object with checker pattern
        """
        return Plane(data_.getDataPath(defaults.FLOOR_TEXTURE))

    def displayAnimation(self, animation: Animation) -> None:
        """
        Add a character created with :attr:`animation` to a default scene and display the scene

        Parameters
        ----------
        animation:
            animation to display
        """
        scene = Viewer.defaultScene()
        scene.add(Character(animation))
        self.displayScene(scene)

    def displayAnimations(self, animations: List[Animation]) -> None:
        """
        Add characters created with :attr:`animations` to a default scene and display the scene

        Parameters
        ----------
        animations:
            animations to display
        """
        scene = Viewer.defaultScene()
        scene.addInLine([Character(animation) for animation in animations])
        self.displayScene(scene)

    def display(self, node: SceneNode) -> None:
        """
        Add :attr:`node` to a default scene and display the scene

        Parameters
        ----------
        node:
            node to display
        """
        scene = self.defaultScene()
        scene.add(node)
        self.displayScene(scene)

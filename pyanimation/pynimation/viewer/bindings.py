from typing import TYPE_CHECKING, Dict, List, Tuple
from functools import partial
import pygame as pg

from pygame.event import Event
from .events import Binding

if TYPE_CHECKING:
    from pynimation.viewer import Viewer
    from pynimation.viewer import Viewport


_keysToAxis: Dict[int, Tuple[int, int, str]] = {
    pg.K_RIGHT: (0, 1, "Move right"),
    pg.K_LEFT: (0, -1, "Move left"),
    pg.K_UP: (2, -1, "Move forward"),
    pg.K_DOWN: (2, 1, "Move backward"),
    pg.K_PAGEUP: (1, 1, "Move up"),
    pg.K_PAGEDOWN: (1, -1, "Move down"),
}


def _getCameraTranslateBindings(viewport: "Viewport", eventType: int):
    bindings = []
    for key in _keysToAxis:
        axis = _keysToAxis[key][0]
        direction = _keysToAxis[key][1] if eventType == pg.KEYDOWN else 0
        bindings.append(
            Binding(
                Event(eventType, {"key": key}),
                [
                    partial(
                        viewport.setCameraTranslationalDirection,
                        axis,
                        direction,
                    )
                ],
                _keysToAxis[key][2],
            )
        )
    return bindings


descriptions = {
    "quit": "Exit PyNimation",
    "screenshot": "Capture a screenshot of the viewport",
    "recording": "Toggle recording",
    "camera": "Move Camera",
}


def getDefaultBindings(
    viewer: "Viewer",
) -> List[Binding]:
    viewport = viewer.viewport
    return [
        Binding(
            Event(pg.QUIT), [partial(viewport.quit)], descriptions["quit"]
        ),
        Binding(
            Event(pg.KEYDOWN, {"key": pg.K_q}),
            [partial(viewport.quit)],
            descriptions["quit"],
        ),
        Binding(
            Event(pg.KEYDOWN, {"key": pg.K_ESCAPE}),
            [partial(viewport.quit)],
            descriptions["quit"],
        ),
        Binding(
            Event(pg.KEYDOWN, {"key": pg.K_s}),
            [partial(viewport._createUniqueScreenshot)],
            descriptions["screenshot"],
        ),
        Binding(
            Event(pg.KEYDOWN, {"key": pg.K_r}),
            [partial(viewport.startStopRecording)],
            descriptions["recording"],
        ),
        *_getCameraTranslateBindings(viewport, pg.KEYDOWN),
        *_getCameraTranslateBindings(viewport, pg.KEYUP),
        Binding(
            Event(pg.MOUSEBUTTONDOWN, {"button": 1}),
            [partial(viewport.setCameraIsRotating, True)],
            descriptions["camera"],
        ),
        Binding(
            Event(pg.MOUSEBUTTONUP, {"button": 1}),
            [partial(viewport.setCameraIsRotating, False)],
            descriptions["camera"],
        ),
        Binding(
            Event(pg.MOUSEMOTION),
            [
                partial(
                    viewport.rotateCameraWithMouse,
                )
            ],
            descriptions["camera"],
        ),
    ]

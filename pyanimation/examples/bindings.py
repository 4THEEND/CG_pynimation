from typing import Optional
from functools import partial
import numpy as np
import pygame as pg
from pygame.event import Event
from pynimation.io import load
from pynimation.viewer import Viewer
from pynimation.viewer import Binding
from pynimation.viewer import Character
from pynimation.common import data as data_

bvh_file = data_.getDataPath("data/animations/Walk_loop.bvh")

[animation] = load(bvh_file)
character = Character(animation)

v = Viewer()

# get the list of bindings
bindings = v.eventManager.bindings
print([str(b) for b in bindings])


# bind a handler to an event
def translateCharacter(character: Character, trans: np.ndarray) -> None:
    character.globalTransform.translate(trans)


event = Event(pg.KEYDOWN, {"key": pg.K_h})
v.eventManager.bind(event, translateCharacter, args=[character, [0.1, 0, 0]])


# if the handler has a keyword argument named "event", it will take the value
# of the Event received at runtime. It is useful to get additional information
# on the event
def printMousePos(event: Optional[Event] = None) -> None:
    if event is not None and "pos" in event.dict:
        print(event.pos)


mouseevent = Event(pg.MOUSEMOTION, {})
v.eventManager.bind(mouseevent, printMousePos)

# rebind all handlers bound to an event to another
newevent = Event(pg.KEYDOWN, {"key": pg.K_j})
v.eventManager.rebind(event, newevent)

# rebind a specific handler bound to an event to another (in case multiple handlers)
newevent = Event(pg.KEYDOWN, {"key": pg.K_j})
v.eventManager.rebind(newevent, event, translateCharacter)

# unbind all handlers bound to an event
v.eventManager.unbind(event)

# unbind a specific handler bound to an event (in case multiple handlers)
v.eventManager.unbind(mouseevent, printMousePos)

# bindings can also be modified and added by setting the tuple of bindings of the
# eventManager
# for this, Bindings objects are constructed, with handlers given as partial objects
# a partial object contains a function and a set of values for its arguments
# it is directly callable, it will call the function with the set of values
binding = Binding(
    event, [partial(translateCharacter, character, [0.01, 0, 0])]
)
mousebinding = Binding(mouseevent, [partial(printMousePos)])

# construct the new tuple of bindings
newbindings = (*v.eventManager.bindings, binding, mousebinding)

# set the tuple of bindings
v.eventManager.bindings = newbindings

v.display(character)

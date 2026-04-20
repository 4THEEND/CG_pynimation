from typing import Dict, List, Callable, Any, Optional, Tuple
import inspect
from functools import partial
import pygame as pg
from pygame.event import Event

from pynimation.common import _Singleton


def _partialsEq(p1: partial, p2: partial) -> bool:
    return (
        isinstance(p1, partial)
        and isinstance(p2, partial)
        and p1.args == p2.args
        and p1.func == p2.func
        and p1.keywords == p2.keywords
    )


class Binding:
    """
    Data structure for an event binding. Binds an event to one or multiple
    handlers. Handlers are stored as partial objects (from the standard library
    functools module). A partial object contains a function and a set of values
    for its arguments it is directly callable, it will call the function with
    the set of values

    Attributes
    ----------
    event: Events:
        event that :attr:`handlers` are bound to

    handlers: List[partial]:
        handlers bound to :attr:`event`

    description: str:
        description of the binding, can be used to generate documentation


    Parameters
    ----------
    event: Events:
        event that :attr:`handlers` are bound to

    handlers: List[partial]:
        handlers bound to :attr:`event`

    description: str:
        description of the binding, can be used to generate documentation


    """

    def __init__(
        self, event: Event, handlers: List[partial], description=None
    ):
        self.event = event
        self.handlers = handlers
        if description is None:
            description = ". ".join(
                [
                    "Call the "
                    + str(h.func.__name__)
                    + " function with "
                    + ", ".join(
                        [
                            args[0] + "=" + str(args[1])
                            for args in zip(
                                inspect.signature(h.func).parameters.keys(),
                                h.args,
                            )
                        ]
                    )
                    for h in handlers
                ]
            )
        self.description = description

    def __eq__(self, other):
        return (
            isinstance(other, Binding)
            and self.event == other.event
            and len(self.handlers) == len(other.handlers)
            and all(
                [_partialsEq(*h) for h in zip(self.handlers, other.handlers)]
            )
        )

    def __iter__(self):
        return iter((self.event, self.handlers))

    def __str__(self):
        return str((self.event, self.handlers, self.description))


class EventManager(metaclass=_Singleton):
    """
    Holds event bindings, calls handlers when matching events are detected

    Parameters
    ----------
    bindings: Tuple[Binding]:
        bindings that will triggered when calling :attr:`update()`
    """

    def __init__(
        self,
        bindings: Tuple[Binding, ...],
    ):
        self.bindings = bindings

    @property
    def bindings(
        self,
    ) -> Tuple[Binding, ...]:
        """
        The bindings that will triggered when calling :attr:`update()`.

        Warning
        -------
        The :attr:`bindings` attribute returns a copy of the current bindings,
        directly modifying elements of the tuple will not affect the current bindings.
        However, this attribute can be modified by setting it to a modified tuple

        Example
        -------
        >>> # get a copy of the list of current bindings
        >>> bindings = eventManaget.bindings
        >>> bindings
        >>> ((<Event(12-MouseMotion {})>, [functools.partial(<function
        >>> printMousePos>)]), (<Event(2-KeyDown {'key': 27, 'mod': 0})>,
        >>> [functools.partial(<function dostuff>, ('arg0', 'arg1'))]))
        >>>
        >>> # The bindings tuple cannot be modified directly
        >>> eventManager.bindings[0] = Binding(Event(pg.MOUSEMOTION, [partial(dootherstuff)])))
        >>>
        >>> TypeError: 'tuple' object does not support item assignment
        >>>
        >>> # nothing was added
        >>> eventManager.bindings
        >>> ((<Event(12-MouseMotion {})>, [functools.partial(<function
        >>> printMousePos>)]), (<Event(2-KeyDown {'key': 27, 'mod': 0})>,
        >>> [functools.partial(<function dostuff>, ('arg0', 'arg1'))]))
        >>>
        >>> # add the binding to a new tuple
        >>> bindings = (*bindings, Binding(Event(pg.MOUSEMOTION, [partial(dootherstuff)]))))
        >>> # set the attribute to the modified list
        >>> eventManager.bindings = bindings
        >>> # the new binding was added
        >>> eventManager.bindings
        >>> ((<Event(12-MouseMotion {})>, [functools.partial(<function
        >>> printMousePos>)]), (<Event(2-KeyDown {'key': 27, 'mod': 0})>,
        >>> [functools.partial(<function dostuff>, ('arg0', 'arg1'))]),
        >>> (<Event(12-MouseMotion {})>, [functools.partial(<function
            dootherstuff>)])>))

        """
        return tuple(
            [binding for types in self._bindings.values() for binding in types]
        )

    @bindings.setter
    def bindings(self, newKeybindings: Tuple[Binding, ...]) -> None:
        self._bindings: Dict[int, List[Binding]] = {}
        for binding in newKeybindings:
            for handler in binding.handlers:
                self.bindPartial(binding.event, handler)

    def bind(
        self,
        event: Event,
        handler: Callable,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> None:
        """
        Maps :attr:`handler` to :attr:`event`, :attr:`handler` will be called with
        the event and :attr:`args` each time :attr:`event` is detected

        Parameters
        ----------

        event:
            event that triggers :attr:`handler`
        handler:
            function that will be called when :attr:`event` is detected,
            if it takes a keyword argument named event, this argument will take
            the value of the event it is called for
        args:
            additional positional argument values of the handler
        kwargs:
            additional keyword argument values of the handler
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        partialHandler = partial(handler, *args, **kwargs)
        self.bindPartial(event, partialHandler)

    def bindPartial(self, event: Event, partialHandler: partial) -> None:
        """
        Maps :attr:`partialHandler` to :attr:`event`, :attr:`handler` will be called with
        the event and :attr:`args` each time :attr:`event` is detected

        Parameters
        ----------

        event:
            event that triggers :attr:`handler`
        partialHandler:
            partial object that will be called when :attr:`event` is detected
        """
        if event.type in [pg.KEYDOWN, pg.KEYUP] and "mod" not in event.dict:
            # You probably meant key+(no mod) and not key+(any or no mod)
            event.dict["mod"] = 0
        if event.type not in self._bindings:
            self._bindings[event.type] = []
        else:
            # check for duplicate events
            dupBind = next(
                (b for b in self._bindings[event.type] if event == b.event),
                None,
            )
            if dupBind is not None:
                # found event in self.bindings
                # check for duplicate handlers
                dupHand = next(
                    (
                        h
                        for h in dupBind.handlers
                        if _partialsEq(h, partialHandler)
                    ),
                    None,
                )
                if dupHand is None:
                    dupBind.handlers.append(partialHandler)
                return
        self._bindings[event.type].append(Binding(event, [partialHandler]))

    def unbind(
        self,
        event: Event,
        handler: Callable = None,
    ) -> List[partial]:
        """
        Unbinds all handlers from :attr:`event`.
        If :attr:`handler` is provided, unbinds it from :attr:`event`.
        If :attr:`args` and :attr:`handler` are provided, will unbind the
        handler that has these arguments from :attr:`event`

        Parameters
        ----------
        event:
            event to unbind handlers from
        handler:
            handler to remove from :attr:`event`, in case multiple handlers are
            binded to :attr:`event`. Optional

        Returns
        -------
        List[partial]:
            unbinded handlers
        """
        if event.type in self._bindings:
            binding: Optional[Binding] = next(
                (b for b in self._bindings[event.type] if event == b.event),
                None,
            )

            if binding is not None:
                handToKeep: List[partial] = []
                handBefore = binding.handlers
                if handler is not None:
                    handToKeep = [h for h in handBefore if h.func != handler]
                if len(handToKeep) != len(handBefore):
                    # remove binding
                    self._bindings[event.type].remove(binding)
                    if len(handToKeep) > 0:
                        # add binding with updated list of handlers
                        self._bindings[event.type].append(
                            Binding(event, handToKeep)
                        )
                    if len(self._bindings[event.type]) == 0:
                        del self._bindings[event.type]
                    return list(set(handBefore) - set(handToKeep))
        return []

    def rebind(
        self,
        event: Event,
        newevent: Event,
        handler: Callable = None,
    ) -> None:
        """
        Rebinds all handlers of :attr:`event` to :attr:`newevent`
        If :attr:`handler` is provided, only rebind it to :attr:`newevent`, in
        case :attr:`event is binded to multiple handlers
        If :attr:`args` and :attr:`handler` are provided, will rebind only the
        handler that has these arguments to :attr:`newevent`

        Parameters
        ----------
        event:
            event to replace handlers from
        handler:
            handler to replace, in case multiple handlers are binded to
            :attr:`event`. Optional
        newevent:
            event to rebind handlers of :attr:`event` to
        """
        handlers = self.unbind(event, handler)
        for handler in handlers:
            self.bindPartial(newevent, handler)

    def _matchEvent(self, event) -> Optional[Binding]:
        if event.type in self._bindings:
            for b in self._bindings[event.type]:
                # '>=': is superset of
                if event.dict.items() >= b.event.dict.items():
                    return b
        return None

    def update(self) -> None:
        """
        Check for events and call event handlers binded to those events
        """
        while pg.event.peek():  # type: ignore
            event = pg.event.poll()
            # ignore num lock as a mod key
            if (
                event.type in [pg.KEYDOWN, pg.KEYUP]
                and "mod" in event.dict
                and event.dict["mod"] == 4096
            ):
                # patch this event
                event.dict["mod"] = 0
                # disable num lock
                pg.key.set_mods(0)  # type: ignore
            binding = self._matchEvent(event)
            if binding is not None:
                for handler in binding.handlers:
                    if (
                        "event"
                        in inspect.signature(handler.func).parameters.keys()
                    ):
                        handler(event)
                    else:
                        handler()

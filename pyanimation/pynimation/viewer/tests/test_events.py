from functools import partial
from typing import List, Callable
import pytest
import pygame as pg
from pygame.event import Event
from pynimation.viewer import EventManager
from pynimation.viewer import Binding
from pynimation.common import _Singleton
from pynimation.viewer.events import _partialsEq


def handler0(event):
    pass


def handler1(a, event):
    pass


def handler2(a, b, event):
    pass


def badhandler():
    pass


@pytest.fixture
def handlers() -> List[Callable]:
    return [handler0, handler1, handler2]


@pytest.fixture
def arguments() -> List[List[str]]:
    return [[], ["a"], ["a", "b"]]


@pytest.fixture
def partials(
    handlers: List[Callable], arguments: List[List[str]]
) -> List[partial]:
    return [partial(handlers[i], *arguments[i]) for i in range(len(handlers))]


@pytest.fixture
def events() -> List[Event]:
    return [
        Event(pg.MOUSEMOTION),
        Event(pg.KEYUP, {"key": pg.K_r}),
        Event(pg.KEYDOWN, {"key": pg.K_s, "mod": 0 & pg.KMOD_CTRL}),
    ]


@pytest.fixture
def bindings(events: List[Event], partials: List[partial]) -> List[Binding]:
    return [Binding(events[i], [partials[i]]) for i in range(len(events))]


@pytest.fixture(autouse=True)
def clearSingleton():
    _Singleton._instances = {}


def getTestEventManager():
    return EventManager(bindings)


def testConstructor(bindings: List[Binding]):
    e = EventManager(bindings)
    for binding in bindings:
        assert binding in e._bindings[binding.event.type]


def testSetSingleKeybinding(bindings: List[Binding]):
    e = EventManager([])
    testbindings = bindings[:1]
    e.bindings = testbindings
    [testbinding] = testbindings
    assert e._bindings[testbinding.event.type] == testbindings


def testSetMultipleKeybindings(bindings: List[Binding]):
    e = EventManager([])
    testbindings = bindings
    e.bindings = testbindings
    for testbinding in testbindings:
        assert testbinding in e._bindings[testbinding.event.type]


def testSetDuplicateKeybindingsSameHandlers(bindings: List[Binding]):
    e = EventManager([])
    testbindings = [bindings[0], bindings[0]]
    e.bindings = testbindings
    [testbinding] = testbindings[:1]
    assert len(e._bindings[testbinding.event.type]) == 1
    assert e._bindings[testbinding.event.type] == testbindings[:1]


def testSetDuplicateKeybindingsDifferentHandlers(
    bindings: List[Binding], partials: List[partial]
):
    e = EventManager([])
    testbinding = bindings[0]
    testbindings = [bindings[0], Binding(testbinding.event, [partials[1]])]
    e.bindings = testbindings
    assert len(e._bindings[testbinding.event.type]) == 1
    assert e._bindings[testbinding.event.type][0].handlers == partials[:2]


def testGetSingleKeybinding(bindings: List[Binding]):
    testbindings = bindings[:1]
    e = EventManager(testbindings)
    assert e.bindings == tuple(testbindings)


def testGetMultipleKeybindings(bindings: List[Binding]):
    testbindings = bindings
    e = EventManager(testbindings)
    for testbinding in testbindings:
        assert testbinding in e.bindings


def testBind(
    bindings: List[Binding],
    handlers: List[Callable],
    events: List[Event],
    arguments: List[List[str]],
):
    testbindings = bindings[:2]
    e = EventManager(testbindings)
    e.bind(events[2], handlers[2], arguments[2])
    for testbinding in bindings:
        ev = testbinding.event
        assert testbinding.event == e._bindings[ev.type][0].event
        assert _partialsEq(
            testbinding.handlers[0], e._bindings[ev.type][0].handlers[0]
        )


def testBindDuplicateHandler(
    bindings: List[Binding],
    handlers: List[Callable],
    events: List[Event],
    arguments: List[List[str]],
    partials: List[partial],
):
    testbindings = bindings
    e = EventManager(testbindings)
    eve = events[2]
    han = handlers[2]
    arg = arguments[2]
    e.bind(eve, han, arg)
    assert len(e._bindings[eve.type]) == 1
    testbinding = e._bindings[eve.type][0]
    assert len(testbinding.handlers) == 1
    assert _partialsEq(testbinding.handlers[0], partials[2])


def testBindDuplicateEvent(
    bindings: List[Binding],
    handlers: List[Callable],
    events: List[Event],
    arguments: List[List[str]],
    partials: List[partial],
):
    testbindings = bindings
    e = EventManager(testbindings)
    eve = events[2]
    han = handlers[1]
    arg = arguments[1]
    e.bind(eve, han, arg)
    assert len(e._bindings[eve.type]) == 1
    testbinding = e._bindings[eve.type][0]
    assert len(testbinding.handlers) == 2
    assert _partialsEq(testbinding.handlers[0], partials[2])
    assert _partialsEq(testbinding.handlers[1], partials[1])


def testBindKeyWithoutMod(bindings: List[Binding]):
    testbindings = [bindings[1]]
    e = EventManager(testbindings)
    [testbinding] = e.bindings
    assert "mod" in testbinding.event.dict
    assert testbinding.event.dict["mod"] == 0


def testUnbindEvent(
    bindings: List[Binding], events: List[Event], partials: List[partial]
):
    testbindings = bindings
    e = EventManager(testbindings)
    ev = events[0]
    [unbound] = e.unbind(ev)
    assert ev.type not in e._bindings
    assert len(e._bindings) == len(testbindings) - 1
    assert _partialsEq(unbound, partials[0])


def testUnbindEventWithoutTypeDelete(
    bindings: List[Binding],
    events: List[Event],
    handlers: List[Callable],
    partials: List[partial],
):
    testevent = Event(pg.KEYUP, {"key": pg.K_l})
    testpartial = partials[2]
    testbinding = Binding(testevent, [testpartial])
    testbindings = [
        *bindings,
        testbinding,
    ]
    e = EventManager(testbindings)
    [unbound] = e.unbind(testevent)
    assert testevent.type in e._bindings
    assert len(e._bindings[testevent.type]) == 1
    leftBinding = e._bindings[testevent.type][0]
    assert leftBinding.event == events[1]
    assert _partialsEq(leftBinding.handlers[0], partials[1])
    assert _partialsEq(unbound, testpartial)


def testUnbindEventMultipleHandlers(
    bindings: List[Binding],
    events: List[Event],
    partials: List[partial],
):
    testbindings = bindings
    testevent = events[0]
    testpartial = partials[1]
    testbinding = Binding(testevent, [testpartial])
    e = EventManager([*testbindings, testbinding])
    unbounds = e.unbind(testevent)
    assert testevent.type not in e._bindings
    assert len(e._bindings) == len(testbindings) - 1
    assert all(
        [
            any([_partialsEq(u, h) for u in unbounds])
            for h in [testpartial, partials[1]]
        ]
    )


def testUnbindHandler(
    bindings: List[Binding],
    handlers: List[Callable],
    events: List[Event],
    partials: List[partial],
):
    testbindings = bindings
    e = EventManager(testbindings)
    testevent = events[0]
    testhandler = handlers[0]
    testpartial = partials[0]
    [unbound] = e.unbind(testevent, testhandler)
    assert testevent.type not in e._bindings
    assert len(e._bindings) == len(testbindings) - 1
    assert _partialsEq(unbound, testpartial)


def testUnbindMultipleHandlers(
    bindings: List[Binding],
    handlers: List[Callable],
    events: List[Event],
    partials: List[partial],
):
    testbindings = bindings
    testevent = events[1]
    testhandler = handlers[1]
    testargs = ("c",)
    testpartial = partial(testhandler, testargs)
    testbinding = Binding(testevent, [testpartial])
    e = EventManager([*testbindings, testbinding])
    unbounds = e.unbind(testevent, testhandler)
    assert testevent.type not in e._bindings
    assert len(e._bindings) == len(testbindings) - 1
    assert all(
        [
            any([_partialsEq(u, h) for u in unbounds])
            for h in [testpartial, partials[1]]
        ]
    )


def testUnbindHandlerWithoutTypeDelete(
    bindings: List[Binding],
    events: List[Event],
    partials: List[partial],
    handlers: List[Callable],
):
    testevent = events[1]
    testhandler = handlers[2]
    testpartial = partials[2]
    testbinding = Binding(testevent, [testpartial])
    testbindings = [
        *bindings,
        testbinding,
    ]
    e = EventManager(testbindings)
    [unbound] = e.unbind(testevent, testhandler)
    assert testevent.type in e._bindings
    assert len(e._bindings[testevent.type]) == 1
    assert len(e._bindings[testevent.type][0].handlers) == 1
    assert _partialsEq(
        e._bindings[testevent.type][0].handlers[0], bindings[1].handlers[0]
    )
    assert _partialsEq(unbound, testpartial)


def testRebindEvent(
    bindings: List[Binding],
    events: List[Event],
    partials: List[partial],
    handlers: List[Callable],
):
    testevent = events[1]
    testpartial = partials[1]
    testnewevent = Event(pg.KEYUP, {"key": pg.K_f})
    e = EventManager(bindings)
    e.rebind(testevent, testnewevent)
    assert len(e._bindings) == len(bindings)
    assert len(e._bindings[testnewevent.type]) == 1
    assert e._bindings[testnewevent.type][0] == Binding(
        testnewevent, [testpartial]
    )


def testRebindHandler(
    bindings: List[Binding],
    events: List[Event],
    partials: List[partial],
    handlers: List[Callable],
):
    testevent = events[1]
    testhandler = handlers[1]
    testpartial = partials[1]
    testnewevent = Event(pg.KEYUP, {"key": pg.K_f})
    e = EventManager(bindings)
    e.rebind(testevent, testnewevent, testhandler)
    assert len(e._bindings) == len(bindings)
    assert len(e._bindings[testnewevent.type]) == 1
    assert e._bindings[testnewevent.type][0] == Binding(
        testnewevent, [testpartial]
    )


def testRebindHandlerAmongMultiple(
    bindings: List[Binding],
    events: List[Event],
    partials: List[partial],
    handlers: List[Callable],
):
    testevent = events[1]
    testhandler = handlers[1]
    testpartial = partials[1]
    testnewevent = Event(testevent.type, {"key": pg.K_f})
    testbinding = Binding(testevent, [partials[2]])
    testbindings = [*bindings, testbinding]
    e = EventManager(testbindings)
    e.rebind(testevent, testnewevent, testhandler)
    assert len(e._bindings) == len(bindings)
    assert len(e._bindings[testnewevent.type]) == 2
    assert testbinding in e._bindings[testevent.type]
    assert Binding(testnewevent, [testpartial]) in e._bindings[testevent.type]


def testMatchEventSingleLarger(
    bindings: List[Binding],
):
    e = EventManager(bindings)
    a = e._matchEvent(Event(pg.MOUSEMOTION, {"bar": 0, "foo": 1})) is not None
    assert a


def testMatchEventMultipleLarger(
    bindings: List[Binding],
):
    e = EventManager(bindings)
    assert (
        e._matchEvent(
            Event(
                pg.KEYDOWN,
                {"key": pg.K_s, "mod": 0 & pg.KMOD_CTRL, "bar": 0},
            )
        )
        is not None
    )


def testMatchEventSingleEqual(
    bindings: List[Binding],
):
    e = EventManager(bindings)
    assert e._matchEvent(Event(pg.MOUSEMOTION, {})) is not None


def testMatchEventMultipleEqual(
    bindings: List[Binding],
):
    e = EventManager(bindings)
    assert (
        e._matchEvent(
            Event(pg.KEYDOWN, {"key": pg.K_s, "mod": 0 & pg.KMOD_CTRL})
        )
        is not None
    )


def testMatchEventSingleSmaller(
    bindings: List[Binding],
):
    e = EventManager(bindings)
    assert e._matchEvent(Event(pg.KEYUP, {})) is None


def testMatchEventMultipleSmaller(
    bindings: List[Binding],
):
    e = EventManager(bindings)
    assert e._matchEvent(Event(pg.KEYDOWN, {"key": pg.K_s})) is None


def testMatchEventSingleDifferent(
    bindings: List[Binding],
):
    e = EventManager(bindings)
    assert e._matchEvent(Event(pg.KEYUP, {"key": pg.K_i})) is None


def testMatchEventMultipleDifferent(
    bindings: List[Binding],
):
    e = EventManager(bindings)
    assert e._matchEvent(Event(pg.KEYDOWN, {"foo": 0, "bar": 1})) is None

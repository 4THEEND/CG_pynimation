import numpy
import pytest
from pytest_mock import MockerFixture
from pynimation.common import Transform


def isIdentity(array: numpy.ndarray) -> bool:
    return (array.shape[0] == array.shape[1]) and numpy.allclose(
        array, numpy.eye(array.shape[0])
    )


def testIsIdentity():
    assert isIdentity(numpy.identity(4))


def patchNotify(transform: Transform, mocker: MockerFixture):
    mocker.patch.object(transform, "notifyObservers")


def testTransformInitSetsMatrixtoIdentity():
    t = Transform()
    assert isIdentity(t.matrix)


def testTransformMatrixSetterNotifiesObservers(mocker: MockerFixture):
    t = Transform()
    patchNotify(t, mocker)
    t.matrix = numpy.identity(4)
    t.notifyObservers.assert_called_once_with()  # type: ignore


def testTransformEqualIsTrueWhenEqual():
    t = [Transform(), Transform()]
    t[0]._matrix = numpy.array(
        [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
    )
    t[1]._matrix = numpy.array(
        [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
    )
    assert t[0] == t[1]


def testTransformEqualIsFalseWhenNotEqual():
    t = [Transform(), Transform()]
    t[0]._matrix = numpy.array(
        [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
    )
    t[1]._matrix = numpy.array(
        [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 4]]
    )
    assert t[0] != t[1]


def testTransformEqualRaisesExceptionWhenNotTransform():
    t = Transform()
    t._matrix = numpy.array(
        [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
    )
    with pytest.raises(
        NotImplementedError, match="Could not compare Transform and"
    ):
        t == ""


def testTransformSetIdentitySetsIdentity():
    t = Transform()
    t._matrix = numpy.array(
        [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
    )
    t.setIdentity()
    assert isIdentity(t.matrix)


def testTransformSetPositionSetsPosition(mocker: MockerFixture):
    t = Transform()
    t.setPosition([0, 1, 2])
    for a in range(3):
        assert numpy.all(t.matrix[0:3, 3][a] == a)


def testTransformSetPositionNotifiesObservers(mocker: MockerFixture):
    t = Transform()
    patchNotify(t, mocker)
    t.setPosition([0, 1, 2])
    t.notifyObservers.assert_called_once_with()  # type: ignore


def testTransformRotateNotifiesObservers(mocker: MockerFixture):
    t = Transform()
    patchNotify(t, mocker)
    t.rotate(numpy.identity(3))
    t.notifyObservers.assert_called_once_with()  # type: ignore


def testTransformGetPositionGetsPosition(mocker: MockerFixture):
    t = Transform()
    t._matrix = numpy.array(
        [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
    )
    assert numpy.all(t.getPosition() == numpy.array([3, 3, 3]))


def testTransformGetPositionTransformGetsPositionTransform(
    mocker: MockerFixture,
):
    t = Transform()
    t._matrix = numpy.array(
        [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
    )
    positionTransform = numpy.array(
        [[1, 0, 0, 3], [0, 1, 0, 3], [0, 0, 1, 3], [0, 0, 0, 1]]
    )
    assert numpy.all(t.getPositionTransform().matrix == positionTransform)

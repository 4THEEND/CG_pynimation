import pytest
from pytest_mock import MockerFixture
import numpy as np
from pynimation.anim import Skeleton
from pynimation.anim import Joint
from pynimation.anim import Frame
from pynimation.common import Transform


def getTestSkeleton() -> Skeleton:
    hips: Joint = Joint("Hips")
    skel = Skeleton(hips)
    hips.addChild(Joint("LeftHip"))
    hips.addChild(Joint("RightHip"))
    return skel


def getTestFrame() -> Frame:
    return Frame(getTestSkeleton())


def testFrameSetLocalTransformsItemInvalidatesTransform():
    frame = getTestFrame()
    frame.localTransforms[0] = Transform()
    assert not frame._valid[0]


def testFrameSetLocalTransformsItemInvalidatesDescendantsTransform():
    frame = getTestFrame()
    frame.localTransforms[0] = Transform()
    assert not all(frame._valid)


def testFrameSetGlobalTransformsItemRaisesException():
    frame = getTestFrame()
    with pytest.raises(AttributeError):
        frame.globalTransforms[1] = Transform()


def testFrameSetGlobalTransformsRaisesException():
    frame = getTestFrame()
    with pytest.raises(AttributeError):
        frame.globalTransforms = []


def testFrameMutateGlobalTransformsItemRaisesException():
    frame = getTestFrame()
    with pytest.raises(AttributeError):
        frame.globalTransforms[1].translate([0, 1, 1])


def testFrameSetRootGlobalTransfom():
    frame = getTestFrame()
    m = np.random.rand(4, 4)
    t = Transform()
    t.matrix = m
    frame.globalTransforms[0] = t
    assert np.all(frame.globalTransforms[0].matrix == m)


def testFrameMutateRootGlobalTransfom():
    frame = getTestFrame()
    frame.globalTransforms[0].translate([1, 1, 1])
    m = np.identity(4)
    m[:3, 3:] = 1
    assert np.all(frame.globalTransforms[0].matrix == m)


def testFrameMutateLocalTransformsItemInvalidatesTransform():
    frame = getTestFrame()
    frame.localTransforms[0].translate([0, 1, 1])
    assert not frame._valid[0]


def testFrameAccessGlobalInvalidTransformUpdatesIt(mocker: MockerFixture):
    frame = getTestFrame()
    mocker.patch.object(frame, "update")
    for i in range(len(frame._valid)):
        frame._valid[i] = False
    frame.globalTransforms[0]
    frame.update.assert_called_once_with(0)  # type: ignore


def testFrameUpdateValidatesTransform():
    frame = getTestFrame()
    frame.localTransforms[0] = Transform()
    frame.update(0)
    assert frame._valid[0]


def testFrameUpdateNonRootValidatesTransform():
    frame = getTestFrame()
    frame.localTransforms[1] = Transform()
    frame.update(1)
    assert frame._valid[1]


def testFrameUpdateValidatesParentTransform():
    frame = getTestFrame()
    frame.localTransforms[0] = Transform()
    frame.update(1)
    assert frame._valid[0]


def testFrameUpdateRecursiveValidatesAllTransforms():
    frame = getTestFrame()
    frame.localTransforms[0] = Transform()
    frame.updateRecursive(0)
    assert all(frame._valid)

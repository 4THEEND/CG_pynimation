from typing import List, Dict, Any
from pytest_mock import MockerFixture
from pynimation.common import TransformGraph
from pynimation.common import TransformNode
from pynimation.common import Transform


test_graphs: Dict[int, Dict] = {}
test_graphs[16] = {
    "0": {"1": {"2": {"3": {}, "4": {"5": {}}}, "6": {"7": {}, "8": {}}}},
    "9": {"10": {"11": {"12": {}, "13": {}}}},
    "14": {"15": {}},
}


def nodeFromDict(name: str, dict_: Any):
    return TransformNode.fromDict(name, dict_, TransformNode)


def graphFromDict(dict_: Any):
    return TransformGraph.fromDict(dict_, TransformNode, TransformGraph)


def getNMockedTransforms(n: int, mocker: MockerFixture) -> List[TransformNode]:
    l: List[TransformNode] = []
    for a in range(n):
        l.append(TransformNode(""))
        mocker.patch.object(l[-1], "update")
    return l


def patchUpdate(node: TransformNode, mocker: MockerFixture) -> None:
    mocker.patch.object(node, "update")


def getTestMockedGraph(
    mocker: MockerFixture, nDescendants: int
) -> TransformGraph:
    graph = graphFromDict(test_graphs[nDescendants])
    for node in graph.nodes:
        patchUpdate(node, mocker)
    return graph


def testTransformNodeStub(mocker: MockerFixture):
    node: TransformNode = TransformNode("")
    patchUpdate(node, mocker)
    node.update()
    node.update.assert_called_once_with()  # type: ignore


def testTransformNodeTransformSetterInvalidates(mocker: MockerFixture):
    node: TransformNode = TransformNode("")
    transform = Transform()
    transform.translate([0, 1, 0])
    node.transform = transform
    assert not node._valid


def testTransformNodeTransformSetterInvalidatesDescendants(
    mocker: MockerFixture,
):
    graph = graphFromDict(test_graphs[16])
    transform = Transform()
    transform.translate([0, 1, 0])
    graph.root.transform = transform
    for node in graph.nodes:
        assert not node._valid


def testTransformNodeInvalidatesTransformOnNotify(mocker: MockerFixture):
    node: TransformNode = TransformNode("")
    node.notify(node.transform)
    assert not node._valid


def testTransformNodeInvalidatesDescendantsOnNotify(mocker: MockerFixture):
    graph = graphFromDict(test_graphs[16])
    transform = Transform()
    transform.translate([0, 1, 0])
    graph.root.notify(graph.root.transform)
    for node in graph.nodes:
        assert not node._valid


def testTransformNodeInvalidatesGlobalTransformOnNotify(mocker: MockerFixture):
    node: TransformNode = TransformNode("")
    node.notify(node.globalTransform)
    assert not node._valid


def testTransformNodeGlobalTransformGetterUpdates(mocker: MockerFixture):
    node: TransformNode = TransformNode("")
    patchUpdate(node, mocker)
    node._valid = False
    node.globalTransform
    node.update.assert_called_once_with()  # type: ignore


def testTransformNodeGlobalTransformGetterUpdatesParent(mocker: MockerFixture):
    node: TransformNode = TransformNode("")
    node1: TransformNode = TransformNode("")
    patchUpdate(node1, mocker)
    node.parent = node1
    node1._valid = False
    node._valid = False
    node.globalTransform
    node1.update.assert_called_once_with()  # type: ignore


def testTransformNodeGlobalTransformGetterUpdatesGrandParent(
    mocker: MockerFixture,
):
    node: TransformNode = TransformNode("")
    node1: TransformNode = TransformNode("")
    node2: TransformNode = TransformNode("")
    patchUpdate(node2, mocker)
    node.parent = node1
    node1.parent = node2
    node2._invalidateRecursive()
    node.globalTransform
    node2.update.assert_called_once_with()  # type: ignore


def testTransformNodeGlobalTransformSetterInvalidatesTransform(
    mocker: MockerFixture,
):
    node: TransformNode = TransformNode("")
    patchUpdate(node, mocker)
    node.globalTransform = Transform()
    assert not node.valid


def testTransformNodeGlobalTransformSetterInvalidatesAllTransform(
    mocker: MockerFixture,
):
    graph = getTestMockedGraph(mocker, 16)
    graph.root.globalTransform = Transform()
    for node in graph.nodes:
        assert not node.valid


def testTransformNodeUpdateRecursiveUpdatesTransform(
    mocker: MockerFixture,
):
    node: TransformNode = TransformNode("")
    patchUpdate(node, mocker)
    node.updateRecursive()
    node.update.assert_called_once_with()  # type: ignore


def testTransformNodeUpdateRecursiveUpdatesAllTransform(
    mocker: MockerFixture,
):
    graph = getTestMockedGraph(mocker, 16)
    graph.root.updateRecursive()
    for node in graph.nodes:
        node.update.assert_called_once_with()  # type: ignore


def testTransformNodeInvalidatesOnAddChild(
    mocker: MockerFixture,
):
    graph = getTestMockedGraph(mocker, 16)
    graph.root.globalTransform = Transform()
    node: TransformNode = TransformNode("")
    patchUpdate(node, mocker)
    graph.root.addChild(node)
    assert not node.valid


def testTransformListGetsRootTransform():
    node: TransformNode = TransformNode("")
    node1: TransformNode = TransformNode("")
    graph: TransformGraph = TransformGraph(node)
    graph.add(node1, parent=node)
    assert graph.transforms[0] is graph.nodes[0].transform


def testTransformListGetsRightTransform():
    node: TransformNode = TransformNode("")
    node1: TransformNode = TransformNode("")
    graph: TransformGraph = TransformGraph(node)
    graph.add(node1, parent=node)
    assert graph.transforms[1] is graph.nodes[1].transform


def testTransformListSetsRootTransform():
    node: TransformNode = TransformNode("")
    graph: TransformGraph = TransformGraph(node)
    transform = Transform()
    transform.translate([0, 1, 0])
    graph.transforms[0] = transform
    assert (graph.nodes[0].transform._matrix == transform._matrix).all()


def testTransformListSetsRightTransform():
    node: TransformNode = TransformNode("")
    node1: TransformNode = TransformNode("")
    graph: TransformGraph = TransformGraph(node)
    graph.add(node1, parent=node)
    transform = Transform()
    transform.translate([0, 1, 0])
    graph.transforms[1] = transform
    assert (graph.nodes[1].transform._matrix == transform._matrix).all()


def testTransformListIteratesOnRightTransforms():
    root: TransformNode = TransformNode("root")
    graph: TransformGraph = TransformGraph(root)
    nNodes = 10
    for a in range(nNodes):
        graph.add(TransformNode(str(a)))
    for (i, transform) in enumerate(graph.transforms):
        assert graph.nodes[i].transform is transform


def testTransformListGetsRootGlobalTransform():
    node: TransformNode = TransformNode("")
    node1: TransformNode = TransformNode("")
    graph: TransformGraph = TransformGraph(node)
    graph.add(node1, parent=node)
    assert graph.globalTransforms[0] is graph.nodes[0].globalTransform


def testTransformListGetsRightGlobalTransform():
    node: TransformNode = TransformNode("")
    node1: TransformNode = TransformNode("")
    graph: TransformGraph = TransformGraph(node)
    graph.add(node1, parent=node)
    assert graph.globalTransforms[1] is graph.nodes[1].globalTransform


def testTransformListSetsRootGlobalTransform():
    node: TransformNode = TransformNode("")
    graph: TransformGraph = TransformGraph(node)
    globalTransform = Transform()
    globalTransform.translate([0, 1, 0])
    graph.globalTransforms[0] = globalTransform
    assert graph.nodes[0].globalTransform == globalTransform


def testTransformListSetsRightGlobalTransform():
    node: TransformNode = TransformNode("")
    node1: TransformNode = TransformNode("")
    graph: TransformGraph = TransformGraph(node)
    graph.add(node1, parent=node)
    globalTransform = Transform()
    globalTransform.translate([0, 1, 0])
    graph.globalTransforms[1] = globalTransform
    assert graph.nodes[1].globalTransform == globalTransform


def testTransformListIteratesOnRightGlobalTransforms():
    root: TransformNode = TransformNode("root")
    graph: TransformGraph = TransformGraph(root)
    nNodes = 10
    for a in range(nNodes):
        graph.add(TransformNode(str(a)))
    for (i, globalTransform) in enumerate(graph.globalTransforms):
        assert graph.nodes[i].globalTransform is globalTransform


def testTransformGraphAddInvalidatesTransform(mocker: MockerFixture):
    node: TransformNode = TransformNode("")
    patchUpdate(node, mocker)
    root: TransformNode = TransformNode("root")
    graph: TransformGraph = TransformGraph(root)
    graph.add(node, parent=root)
    assert not node.valid


def testTransformGraphAddChildInvalidatesTransform(mocker: MockerFixture):
    node: TransformNode = TransformNode("")
    patchUpdate(node, mocker)
    root: TransformNode = TransformNode("root")
    graph: TransformGraph = TransformGraph(root)
    graph.add(node, parent=root)
    assert not node.valid

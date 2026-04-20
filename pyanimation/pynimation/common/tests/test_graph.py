import pytest
import copy
from typing import Dict, Any, List

from pynimation.common import Graph
from pynimation.common import Node

test_graphs: Dict[int, Dict] = {}
test_graphs[16] = {
    "0": {"1": {"2": {"3": {}, "4": {"5": {}}}, "6": {"7": {}, "8": {}}}},
    "9": {"10": {"11": {"12": {}, "13": {}}}},
    "14": {"15": {}},
}
test_graphs[15] = {
    "0": {"1": {"2": {"3": {}, "4": {"5": {}}}, "6": {"7": {}, "8": {}}}},
    "9": {"10": {"11": {"12": {}, "13": {}}}},
    "14": {},
}


def nodeFromDict(name: str, dict_: Any):
    return Node.fromDict(name, dict_, Node)


def graphFromDict(dict_: Any):
    return Graph.fromDict(dict_, Node, Graph)


def getTestGraph(nDescendants: int) -> Dict[int, Dict]:
    return copy.deepcopy(test_graphs[nDescendants])


def getNameList(nodes: List[Node]):
    return [a.name for a in nodes]


def initGraph():
    n = Node("Root")
    g = Graph(n)
    return (n, g)


def testGraphInitAddsRootToHashmap():
    root, graph = initGraph()
    assert root in graph.nodes
    assert len(graph.nodes) == 1


def testGraphInitAddsSelfReferenceToRoot():
    root, graph = initGraph()
    assert root._graph == graph


def testGraphInitSetsRootParentToNone():
    root, graph = initGraph()
    assert root.parent is None


def testGraphInitAddsRootDescendantsToHashmap():
    nDescendants = 16
    root = nodeFromDict("Root", test_graphs[nDescendants])
    graph = Graph(root)
    assert len(graph.nodes) == nDescendants + 1
    nameList = getNameList(graph.nodes)
    for i in range(nDescendants):
        assert str(i) in nameList


def testGraphCantDeleteRoot():
    _, graph = initGraph()
    with pytest.raises(AttributeError, match="can't delete attribute"):
        del graph.root


def testGraphAddAddsToHashmap():
    _, graph = initGraph()
    n = Node("n")
    graph.add(n)
    assert n in graph.nodes
    assert len(graph.nodes) == 2


def testGraphAddAddsRootAsDefaultParent():
    root, graph = initGraph()
    n = Node("n")
    graph.add(n)
    assert n.parent == root


def testGraphAddAddsSelfReference():
    root, graph = initGraph()
    n = Node("n")
    graph.add(n)
    assert n._graph == graph


def testGraphAddAddsToCorrectParent():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    graph.add(n)
    graph.add(n1, parent=n)
    assert n1.parent == n


def testGraphAddAddsChildToParent():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    graph.add(n)
    graph.add(n1, n)
    assert n1 in n.children


def testGraphAddAddsDescendantsToHashmap():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    root = nodeFromDict("Root", dict_)
    graph = Graph(root)
    assert len(graph.nodes) == nDescendants + 1
    nameList = getNameList(graph.nodes)
    for i in range(nDescendants):
        assert str(i) in nameList


def testGraphAddThrowsExceptionWhenParentNotFound():
    with pytest.raises(
        ValueError, match="was not found in the graph, maybe add it first ?"
    ):
        root, graph = initGraph()
        n = Node("n")
        n1 = Node("n1")
        graph.add(n1, n)


def testGraphRemoveCantRemoveRoot():
    root, graph = initGraph()
    root = graph.root
    graph.remove(root)
    assert graph.root is not None
    assert graph.root == root


def testGraphRemoveRemovesFromChildren():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    n = [a for a in graph.nodes if a.name == "0"][0]
    graph.remove(n)
    assert n not in graph.root.children


def testGraphRemoveRemovesDescendantsFromHashmap():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    n = [a for a in graph.nodes if a.name == "0"][0]
    graph.remove(n)
    assert n not in graph.nodes
    assert len(graph.nodes) == nDescendants + 1 - (len(n.descendants()) + 1)
    for child in n.descendants():
        assert child not in graph.nodes


def testGraphRemoveRemovesParent():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    n = [a for a in graph.nodes if a.name == "0"][0]
    graph.remove(n)
    assert n.parent is None


def testGraphRemoveRemovesSelfReferences():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    n = [a for a in graph.nodes if a.name == "0"][0]
    graph.remove(n)
    for c in n.descendants():
        assert c._graph is None


def testGraphEqIsTrueForSameStructure():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    graph1 = graphFromDict(dict_)
    assert graph.hasSameTopology(graph1)


def testGraphEqIsFalseForDifferentStructure():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    dict_ = getTestGraph(nDescendants - 1)
    graph1 = graphFromDict(dict_)
    assert not graph.hasSameTopology(graph1)


def testGraphUpdatesHashOnRemove():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    hash_ = graph._hash
    graph.remove(graph.root.children[0])
    hash1_ = graph._hash
    assert hash_ != hash1_


def testGraphUpdatesHashOnAdd():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    hash_ = graph._hash
    graph.add(Node("node"))
    hash1_ = graph._hash
    assert hash_ != hash1_


def testGraphEqIsTrueForSameStructureAfterEdit():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    dict_ = getTestGraph(nDescendants)
    graph1 = graphFromDict(dict_)
    graph.add(Node("node"))
    graph1.add(Node("node"))
    assert graph.hasSameTopology(graph1)


def testGraphEqIsFalseForSameStructureWithDifferentNames():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    dict_ = getTestGraph(nDescendants)
    graph1 = graphFromDict(dict_)
    graph.add(Node("node"))
    graph1.add(Node("node1"))
    assert not graph.hasSameTopology(graph1)


def testNodeInitAddsToRoot():
    root, graph = initGraph()
    n = Node("n", graph=graph)
    assert n.parent == root


def testNodeInitAddsParent():
    root, graph = initGraph()
    n = Node("n")
    graph.add(n)
    n1 = Node("n", parent=n)
    assert n1.parent == n


def testNodeInitGraphFromParent():
    root, graph = initGraph()
    n = Node("n")
    graph.add(n)
    n1 = Node("n", parent=n)
    assert n1._graph == graph


def testNodeInitAddsToParentChildren():
    root, graph = initGraph()
    n = Node("n")
    graph.add(n)
    n1 = Node("n", parent=n)
    assert n1 in n.children


def testNodeInitAddsToHashmap():
    root, graph = initGraph()
    n = Node("n", graph=graph)
    assert n in graph.nodes
    assert len(graph.nodes) == 2


def testNodeChildrenSetterAddsChildren():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    root.children = (n, n1)
    assert n in root.children
    assert n1 in root.children


def testNodeChildrenSetterAddsToHashmap():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    root.children = (n, n1)
    assert n in graph.nodes
    assert n1 in graph.nodes
    assert len(graph.nodes) == 3


def testNodeChildrenSetterAddsParent():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    root.children = (n, n1)
    assert n.parent == root
    assert n1.parent == root


def testNodeChildrenSetterRemovesChildren():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    root.children = (n, n1)
    root.children = ()
    assert n not in root.children
    assert n1 not in root.children


def testNodeChildrenSetterReplacesParent():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    n2 = Node("n2")
    root.children = (n, n1)
    root.children = (n1, n2)
    assert n.parent is None
    assert n2.parent == root
    assert n1.parent == root


def testNodeChildrenSetterRemovesParent():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    root.children = (n, n1)
    root.children = ()
    assert n.parent is None
    assert n1.parent is None


def testNodeChildrenSetterReplacesChildren():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    n2 = Node("n2")
    root.children = (n, n1)
    root.children = (n1, n2)
    assert n2 in root.children
    assert n not in root.children
    assert len(root.children) == 2


def testNodeChildrenSetterRemovesFromHashmap():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    root.children = (n, n1)
    root.children = ()
    assert n not in graph.nodes
    assert n1 not in graph.nodes
    assert len(graph.nodes) == 1


def testNodeChildrenSetterReplacesInHashmap():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    n2 = Node("n2")
    root.children = (n, n1)
    root.children = (n1, n2)
    assert n not in graph.nodes
    assert n2 in graph.nodes
    assert len(graph.nodes) == 3


def testNodeChildrenDeleterSetsEmptyTuple():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    root.children = (n, n1)
    del root.children
    assert hasattr(root, "children")
    assert root.children is not None
    assert len(root.children) == 0


def testNodeParentSetterNoneRemovesParent():
    root, graph = initGraph()
    n = Node("n")
    graph.add(n)
    n.parent = None
    assert n.parent is None


def testNodeParentSetterNoneRemovesFromParentChildren():
    root, graph = initGraph()
    n = Node("n")
    graph.add(n)
    n.parent = None
    assert n not in root.children


def testNodeParentSetterNoneRemovesFromHashmap():
    root, graph = initGraph()
    n = Node("n")
    graph.add(n)
    n.parent = None
    assert "n" not in graph.nodes


def testNodeParentSetterNoneRemovesDescendantsFromHashmap():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1", parent=n)
    n2 = Node("n2", parent=n)
    n3 = Node("n3", parent=n2)
    graph.add(n)
    n.parent = None
    assert n1 not in graph.nodes
    assert n2 not in graph.nodes
    assert n3 not in graph.nodes


def testNodeParentSetterSetsNewParent():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    graph.add(n)
    graph.add(n1)
    n1.parent = n
    assert n1.parent == n


def testNodeParentSetterAddsToChildren():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    graph.add(n)
    graph.add(n1)
    n1.parent = n
    assert n1 in n.children


def testNodeParentSetterRemovesFromChildren():
    root, graph = initGraph()
    n = Node("n")
    n1 = Node("n1")
    graph.add(n, parent=root)
    graph.add(n1, parent=root)
    n1.parent = n
    assert n1 not in root.children


def testNodeAddchildAddsChild():
    root, graph = initGraph()
    n = Node("n", parent=root)
    n1 = Node("n1")
    n.addChild(n1)
    assert n1 in n.children


def testNodeAddchildSetsParent():
    root, graph = initGraph()
    n = Node("n", parent=root)
    n1 = Node("n1")
    n.addChild(n1)
    assert n1.parent == n


def testNodeAddchildAddsDescendantsToHashmap():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    root = nodeFromDict("Root", dict_)
    graph = Graph(root)
    assert len(graph.nodes) == nDescendants + 1
    nameList = getNameList(graph.nodes)
    for i in range(nDescendants):
        assert str(i) in nameList


def testNodeAddchildSetsGraphReference():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    root = nodeFromDict("Root", dict_)
    graph = Graph(root)
    for i in range(nDescendants):
        assert graph.nodes[i]._graph == graph


def testNodeRemovechildRemovesChild():
    root, graph = initGraph()
    n = Node("n", parent=root)
    n1 = Node("n1", parent=n)
    n.removeChild(n1)
    assert n1 not in n.children


def testNodeRemovechildRemovesParent():
    root, graph = initGraph()
    n = Node("n", parent=root)
    n1 = Node("n1", parent=n)
    n.removeChild(n1)
    assert n1.parent is None


def testNodeRemovechildRemovesDescendantsFromHashmap():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    graph = graphFromDict(dict_)
    n = [a for a in graph.nodes if a.name == "0"][0]
    graph.root.removeChild(n)
    assert n not in graph.nodes
    assert len(graph.nodes) == nDescendants + 1 - (len(n.descendants()) + 1)
    for child in n.descendants():
        assert child not in graph.nodes


def testNodeRemovechildRemovesGraphReference():
    nDescendants = 16
    dict_ = getTestGraph(nDescendants)
    root = nodeFromDict("Root", dict_)
    graph = Graph(root)
    n = [a for a in graph.nodes if a.name == "0"][0]
    root.removeChild(n)
    for node in n.descendants():
        assert node._graph is None

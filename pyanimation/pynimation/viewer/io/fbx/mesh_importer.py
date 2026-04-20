from typing import List, Dict, Union
import fbx
import numpy
from pynimation.anim import Skeleton
from pynimation.anim import Animation
from pynimation.viewer.io import MeshImporter
from pynimation.io import FBXImporter

from .mesh import FBXMesh
from pynimation.viewer import SceneGraph
from pynimation.viewer import SceneNode


TIME_INFINITY = fbx.FbxTime(0x7FFFFFFFFFFFFFFF)


class FBXMeshImporter(MeshImporter, FBXImporter):
    """
    Imports meshes from an FBX file
    """

    extension = "fbx"

    def __init__(self):
        self.manager = fbx.FbxManager.Create()
        self.scene = fbx.FbxScene.Create(self.manager, "MyScene")
        self.importer = fbx.FbxImporter.Create(self.manager, "MyImporter")
        self.animations: List[Animation] = []
        self.skeletonObjects: List[Skeleton] = []
        self.sceneGraph = None
        self.rootNode = None

    def _loadSceneGraph(self) -> None:
        self.sceneGraph = SceneGraph(SceneNode(self.rootNode.GetName(), None))
        sn = self.sceneGraph.root
        sn.transform = self._getNodeLocalTransform(self.rootNode)
        self._parseSceneGraph(self.rootNode, sn)
        self.sceneGraph.updateAll()

        self.meshObjects: Union[Dict, List] = []
        self.meshInstancingOnName: bool = False
        self.skinnedMeshObjects: Union[Dict, List] = []
        self.skeletonNodes: Dict[Skeleton, List] = {}

    def loadMeshes(
        self, filename: str, meshInstancingOnName: bool = False
    ) -> List[SceneNode]:
        """
        Load meshes from :attr:`filename`

        Parameters
        ----------
        filename:
            file to load meshes from

        Returns
        -------
        List[SceneNode]
            meshes loaded from :attr:`filename`
        """
        if self.rootNode is None:
            self._loadFile(filename)
        if self.sceneGraph is None:
            self._loadSceneGraph()
        if self.meshObjects or self.skinnedMeshObjects:
            print("Mesh data already loaded")
            return []

        self.meshInstancingOnName = meshInstancingOnName
        if self.meshInstancingOnName:
            self.meshObjects = {}
            self.skinnedMeshObjects = {}
        else:
            self.meshObjects = []
            self.skinnedMeshObjects = []

        # Need skeletons to be loaded first (for SkinnedMesh purposes)
        if len(self.skeletonObjects) == 0:
            self._loadSkeletons()

        self._parseSceneMeshes(self.rootNode)

        if self.meshInstancingOnName:
            assert isinstance(self.skinnedMeshObjects, dict)
            assert isinstance(self.meshObjects, dict)
            meshes = [
                *[a[0] for a in self.skinnedMeshObjects.values()],
                *[a[0] for a in self.meshObjects.values()],
            ]
        else:
            assert isinstance(self.skinnedMeshObjects, list)
            assert isinstance(self.meshObjects, list)
            meshes = [
                *[a[0] for a in self.skinnedMeshObjects],
                *[a[0] for a in self.meshObjects],
            ]
        return meshes

    def _parseSceneGraph(
        self, parentNode: fbx.FbxNode, sceneGrapheNode: fbx.FbxNode
    ) -> None:
        for i in range(0, parentNode.GetChildCount()):
            node = parentNode.GetChild(i)
            sn: SceneNode = SceneNode(node.GetName())
            self.sceneGraph.add(sn, sceneGrapheNode)
            sn.transform = self._getNodeLocalTransform(node)
            self._parseSceneGraph(node, sn)

    def _parseSceneMeshes(self, parentNode: fbx.FbxNode) -> None:
        for i in range(0, parentNode.GetChildCount()):
            node = parentNode.GetChild(i)
            e = FBXImporter._getFbxNodeType(node)
            if fbx.FbxNodeAttribute.EType.eMesh == e:
                name = node.GetName()
                print("#Loading mesh: " + name)
                sn = self.sceneGraph.getNode(name)
                if self.meshInstancingOnName:
                    if (name not in self.meshObjects) and (
                        name not in self.skinnedMeshObjects
                    ):
                        vbo = FBXMesh(node, self.systemUnitScale)
                        if vbo.mIsSkinedMesh:
                            self.skinnedMeshObjects[name] = [vbo, []]
                        else:
                            self.meshObjects[name] = [vbo, []]
                    if vbo.mIsSkinedMesh:
                        self.skinnedMeshObjects[name][1].append(sn)
                    else:
                        self.skinnedMeshObjects[name][1].append(sn)
                else:
                    assert isinstance(self.skinnedMeshObjects, list)
                    assert isinstance(self.meshObjects, list)
                    vbo = FBXMesh(
                        node, self.skeletonNodes, self.systemUnitScale
                    )
                    if vbo.mIsSkinedMesh:
                        self.skinnedMeshObjects.append([vbo, [sn]])
                    else:
                        self.meshObjects.append([vbo, [sn]])
            self._parseSceneMeshes(node)

    def _getListMeshVertices(self) -> numpy.ndarray:
        v = []
        for obj in self.meshObjects:
            for vbo in obj[0].vbobjects:
                v.append(vbo.data["vPosition"])
        if v:
            return numpy.concatenate(v)
        else:
            return numpy.zeros([], dtype="float32")

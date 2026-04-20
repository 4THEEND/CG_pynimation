import fbx
import numpy
from pynimation.viewer import SceneNode
from pynimation.viewer import Animatable
from pynimation.viewer import VBObject
from pynimation.anim import Skeleton
from pynimation.common import data as data_
from typing import List, Tuple, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from pynimation.anim import Frame

TRIANGLE_VERTEX_COUNT = 3


class FBXMesh(SceneNode, Animatable):
    """
    Representation of a mesh obtained from an FBX file

    Parameters
    ----------
    node:
        node corresponding to this mesh in the scene graph of the FBX file

    listOfSkeletons:
        skeletons that animate this mesh

    scale:
        unit scale of the mesh
    """

    def __init__(
        self,
        node: fbx.FbxNode,
        listOfSkeletons: Dict[Skeleton, List] = {},
        scale=1.0,
    ) -> None:
        self.mHasNormal = False
        self.mHasUV = False
        self.mIsSkinedMesh = False
        self.skeleton: Optional[Skeleton] = None
        self.scaleFactor = scale
        self.meshName: str = node.GetName()
        super().__init__("")

        self._loadMeshSimple(node, False, listOfSkeletons)

    def animate(self, frame: "Frame") -> None:
        """
        Animate this mesh with the transforms of :attr:`frame`.

        Note
        ----
        The mesh has to be skinned

        Parameters
        ----------
        frame:
            frame to animate the mesh with
        """
        if not self.mIsSkinedMesh:
            raise ValueError("Cannot animate FBXMesh that is not skinned")
        nJoints = len(frame.globalTransforms)
        skinnedMatrix = [
            frame.globalTransforms[b]
            * frame.skeleton.joints[b].getInverseBindMatrix()
            for b in range(nJoints)
        ]

        skinningMatrices = [
            t.transpose().matrix.tolist() for t in skinnedMatrix
        ]
        for vbo in self.children:
            vbo.uniformData["SkinningMatrices"] = skinningMatrices

    def _assign(self, arrayOut: List, arrayIn: List, nbElements: int) -> None:
        for i in range(0, nbElements):
            arrayOut[i] = arrayIn[i]

    def _loadMeshSimple(
        self,
        node: fbx.FbxNode,
        useVertexIndex: bool,
        listOfSkeletons: Dict[Skeleton, List],
    ) -> None:
        mesh = node.GetMesh()
        attribType = node.GetNodeAttribute()
        defaultColor = numpy.array([0.5, 0.5, 0.5, 1.0], dtype="float32")
        if attribType is not None:
            c = attribType.Color
            defaultColor[0] = c.Get()[0]
            defaultColor[1] = c.Get()[1]
            defaultColor[2] = c.Get()[2]

        nbVertices = mesh.GetControlPointsCount()
        vertexPositions = numpy.zeros((nbVertices, 3), dtype="float32")
        vertexColors = numpy.zeros((nbVertices, 4), dtype="float32")

        v = mesh.GetControlPoints()
        for i in range(0, nbVertices):
            vertexPositions[i, 0] = v[i][0] * self.scaleFactor
            vertexPositions[i, 1] = v[i][1] * self.scaleFactor
            vertexPositions[i, 2] = v[i][2] * self.scaleFactor
            vertexColors[i, 0:4] = defaultColor[0:4]
            # TODO ADD NORMALS

        vertexIndexes = None

        self.mIsSkinedMesh = mesh.GetDeformerCount(
            fbx.FbxDeformer.EDeformerType.eSkin
        )
        if self.mIsSkinedMesh:
            (
                vertexSkinweights,
                vertexSkinbones,
                vertexJointcount,
                boneList,
            ) = self._getSkinningData(mesh, nbVertices, listOfSkeletons)

        if useVertexIndex:
            vertexIndexes = numpy.empty(0, dtype=int)
            nbPolygons = mesh.GetPolygonCount()
            vp = mesh.GetPolygonVertices()
            for i in range(0, nbPolygons):
                polygonSize = mesh.GetPolygonSize(i)
                polygonStartIndex = mesh.GetPolygonVertexIndex(i)
                if polygonStartIndex != -1:
                    for j in range(2, polygonSize):
                        tmp = numpy.array(
                            [
                                vp[polygonStartIndex],
                                vp[polygonStartIndex + j - 1],
                                vp[polygonStartIndex + j],
                            ],
                            dtype=int,
                        )
                        vertexIndexes = numpy.append(vertexIndexes, tmp)
        else:
            vNormals = fbx.FbxVector4Array()
            mesh.GetPolygonVertexNormals(vNormals)

            self.mHasNormal = vNormals.GetCount() > 0

            nbPolygons = mesh.GetPolygonCount()
            vp = mesh.GetPolygonVertices()

            totalNumberOfVertices = 0
            for i in range(0, nbPolygons):
                polygonSize = mesh.GetPolygonSize(i)
                totalNumberOfVertices += (polygonSize - 2) * 3

            vPositions = vertexPositions
            vColors = vertexColors
            vertexPositions = numpy.zeros(
                (totalNumberOfVertices, 3), dtype="float32"
            )
            vertexColors = numpy.zeros(
                (totalNumberOfVertices, 4), dtype="float32"
            )
            if self.mHasNormal:
                vertexNormals = numpy.zeros(
                    (totalNumberOfVertices, 3), dtype="float32"
                )
            if self.mIsSkinedMesh:
                vSkinWeights = vertexSkinweights
                vSkinBones = vertexSkinbones
                vertexSkinweights = numpy.zeros(
                    (totalNumberOfVertices, 4), dtype="float32"
                )
                vertexSkinbones = numpy.zeros(
                    (totalNumberOfVertices, 4), dtype="float32"
                )

            currentVertex = 0
            currentPolygonVertexCount = 0
            for i in range(0, nbPolygons):
                polygonSize = mesh.GetPolygonSize(i)
                polygonStartIndex = mesh.GetPolygonVertexIndex(i)
                for j in range(2, polygonSize):
                    vertexPositions[currentVertex] = vPositions[
                        vp[polygonStartIndex]
                    ]
                    vertexPositions[currentVertex + 1] = vPositions[
                        vp[polygonStartIndex + j - 1]
                    ]
                    vertexPositions[currentVertex + 2] = vPositions[
                        vp[polygonStartIndex + j]
                    ]
                    vertexColors[currentVertex] = vColors[
                        vp[polygonStartIndex]
                    ]
                    vertexColors[currentVertex + 1] = vColors[
                        vp[polygonStartIndex + j - 1]
                    ]
                    vertexColors[currentVertex + 2] = vColors[
                        vp[polygonStartIndex + j]
                    ]
                    if self.mHasNormal:
                        self._assign(
                            vertexNormals[currentVertex],
                            vNormals[currentPolygonVertexCount],
                            3,
                        )
                        self._assign(
                            vertexNormals[currentVertex + 1],
                            vNormals[currentPolygonVertexCount + j - 1],
                            3,
                        )
                        self._assign(
                            vertexNormals[currentVertex + 2],
                            vNormals[currentPolygonVertexCount + j],
                            3,
                        )
                    if self.mIsSkinedMesh:
                        vertexSkinweights[currentVertex] = vSkinWeights[
                            vp[polygonStartIndex]
                        ]
                        vertexSkinweights[currentVertex + 1] = vSkinWeights[
                            vp[polygonStartIndex + j - 1]
                        ]
                        vertexSkinweights[currentVertex + 2] = vSkinWeights[
                            vp[polygonStartIndex + j]
                        ]
                        vertexSkinbones[currentVertex] = vSkinBones[
                            vp[polygonStartIndex]
                        ]
                        vertexSkinbones[currentVertex + 1] = vSkinBones[
                            vp[polygonStartIndex + j - 1]
                        ]
                        vertexSkinbones[currentVertex + 2] = vSkinBones[
                            vp[polygonStartIndex + j]
                        ]

                        # Where compute bind pose?

                    currentVertex += 3
                currentPolygonVertexCount += polygonSize

        data = {}
        data["vPosition"] = vertexPositions
        data["vColor"] = vertexColors
        if self.mHasNormal:
            data["vNormal"] = vertexNormals
        if self.mIsSkinedMesh:
            data["vSkinWeights"] = vertexSkinweights
            data["vSkinBones"] = vertexSkinbones

        VERT, FRAG = self._getShaders()
        self.addChild(VBObject(data, vertexIndexes, VERT, FRAG))

    def _getSkinningData(
        self,
        mesh: fbx.FbxMesh,
        nbVertices: int,
        listOfSkeletons: Dict[Skeleton, List],
    ) -> Tuple[numpy.ndarray, numpy.ndarray, int, List]:

        vertexSkinweights = numpy.zeros((nbVertices, 4), dtype="float32")
        vertexSkinbones = numpy.zeros((nbVertices, 4), dtype="float32")
        vertexJointcount = numpy.zeros(nbVertices, dtype="int32")

        for i in range(
            mesh.GetDeformerCount(fbx.FbxDeformer.EDeformerType.eSkin)
        ):
            deformer = mesh.GetDeformer(i, fbx.FbxDeformer.EDeformerType.eSkin)

            for i2 in range(deformer.GetClusterCount()):
                cluster = deformer.GetCluster(i2)
                node = cluster.GetLink()

                if not self.skeleton:
                    self.skeleton = self._findCorrespondingSkeleton(
                        node, listOfSkeletons
                    )
                assert self.skeleton is not None
                jointsNames = self.skeleton.jointsNames
                if self.skeleton and (node.GetName() in jointsNames):
                    jointIndex: int = jointsNames.index(node.GetName())
                else:
                    print(
                        "Error loading skin for mesh "
                        + mesh.GetName()
                        + ": bone "
                        + node.GetName()
                        + " not found in hierarchy"
                    )

                controlPointIndices = cluster.GetControlPointIndices()
                controlPointWeights = cluster.GetControlPointWeights()

                for i3 in range(cluster.GetControlPointIndicesCount()):
                    controlPointIndex = (int)(controlPointIndices[i3])
                    controlPointWeight = controlPointWeights[i3]
                    jointCount = vertexJointcount[controlPointIndex]

                    # At most binding four joint per vertex
                    if jointCount < 4:
                        # Joint index
                        vertexSkinbones[
                            controlPointIndex, jointCount
                        ] = jointIndex
                        vertexSkinweights[
                            controlPointIndex, jointCount
                        ] = controlPointWeight
                        vertexJointcount[controlPointIndex] += 1
                    else:
                        # More than four joints, replace joint of minimum Weight
                        minW, minIdx = min(
                            (vertexSkinweights[controlPointIndex, i], i)
                            for i in range(
                                len(vertexSkinweights[controlPointIndex])
                            )
                        )
                        vertexSkinbones[controlPointIndex][minIdx] = jointIndex
                        vertexSkinweights[controlPointIndex][
                            minIdx
                        ] = controlPointWeight
                        vertexJointcount[controlPointIndex] += 1

                        print(
                            "More than 4 joints (%d joints) bound to per vertex in %s. "
                            % (jointCount, node.GetName())
                        )

        return (
            vertexSkinweights,
            vertexSkinbones,
            vertexJointcount,
            [],
        )

    def _findCorrespondingSkeleton(
        self, node: fbx.FbxNode, listOfSkeletons: Dict[Skeleton, List]
    ) -> Optional[Skeleton]:
        for skel in listOfSkeletons.keys():
            for i in listOfSkeletons[skel]:
                if node == i[1]:
                    return skel
        return None

    def _getShaders(self) -> Tuple[str, str]:

        if self.mIsSkinedMesh:  # TODO SOON
            vertSh = "phongShadingLBS_vs"
            fragSh = "phongShading_ps"
        else:
            vertSh = "phongShading_vs"
            fragSh = "phongShading_ps"

        self.VERT = data_.getDataPath("data/shaders/" + vertSh + ".glsl")
        self.FRAG = data_.getDataPath("data/shaders/" + fragSh + ".glsl")

        with open(self.VERT) as file:
            VERT = file.read()
        with open(self.FRAG) as file:
            FRAG = file.read()

        return VERT, FRAG

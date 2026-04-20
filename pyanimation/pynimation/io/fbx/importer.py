from typing import List, Optional, Any
import fbx
from pynimation.common import Transform
from pynimation.anim import Skeleton
from pynimation.anim import Animation
from pynimation.anim import Joint
from pynimation.io.importer import Importer


TIME_INFINITY = fbx.FbxTime(0x7FFFFFFFFFFFFFFF)


class FBXImporter(Importer):
    """
    Importer class for FBX files. Only imports animations. See
    :class:`~pynimation.viewer.io.fbx.FBXMeshImporter` to import meshes from
    FBX files
    """

    extension = "fbx"

    def __init__(self):
        self.manager = fbx.FbxManager.Create()
        self.scene = fbx.FbxScene.Create(self.manager, "MyScene")
        self.importer = fbx.FbxImporter.Create(self.manager, "MyImporter")
        self.animations: List[Animation] = []
        self.skeletonObjects: List[Skeleton] = []
        self.rootNode = None

    def _loadFile(self, filename: str) -> None:
        status = self.importer.Initialize(filename)

        if not status:
            err = "Error: " + self.importer.GetStatus().GetErrorString()
            raise Exception(err)

        self.importer.Import(self.scene)
        self.importer.Destroy()

        self.rootNode = self.scene.GetRootNode()

        self.systemUnit = self.scene.GetGlobalSettings().GetSystemUnit()
        self.systemUnitScale = self.systemUnit.GetConversionFactorTo(
            fbx.FbxSystemUnit.m
        )
        lTimeMode = self.scene.GetGlobalSettings().GetTimeMode()
        if lTimeMode == fbx.FbxTime.EMode.eCustom:
            self.framerate = (
                self.scene.GetGlobalSettings().GetCustomFrameRate()
            )
            fbx.FbxTime.SetGlobalTimeMode(lTimeMode, self.framerate)
        else:
            self.framerate = fbx.FbxTime.GetFrameRate(lTimeMode)
            fbx.FbxTime.SetGlobalTimeMode(lTimeMode)
        self.timespan = (
            self.scene.GetGlobalSettings().GetTimelineDefaultTimeSpan()
        )
        self.startTime = self.timespan.GetStart()
        self.stopTime = self.timespan.GetStop()

    def load(self, filename: str) -> List[Animation]:
        """
        Imports animations from FBX file :attr:`filename`

        Parameters
        ----------
        filename:
            file to import animations from

        Returns
        -------
        Animation
            Imported animations
        """
        if self.rootNode is None:
            self._loadFile(filename)

        self._loadAnimations()
        return self.animations

    def _loadSkeletons(self) -> None:
        if self.skeletonObjects:
            print("Skeleton data already loaded")
            return

        self.skeletonObjects = []
        self.skeletonNodes: Any = {}
        self._parseSceneSkeletons(self.rootNode)

    def _loadAnimations(self) -> None:
        if len(self.animations) > 0:
            print("Animation data already loaded")
            return

        if len(self.skeletonObjects) == 0:  # Need skeletons to be loaded first
            self._loadSkeletons()

        self._parseSceneAnimations()

    def _parseSceneSkeletons(
        self,
        parentNode: fbx.FbxNode,
        skeleton: Optional[Skeleton] = None,
        parentJoint: Optional[fbx.FbxNode] = None,
    ) -> None:
        for i in range(0, parentNode.GetChildCount()):
            node = parentNode.GetChild(i)
            e = FBXImporter._getFbxNodeType(node)
            if fbx.FbxNodeAttribute.EType.eSkeleton == e:
                name = node.GetName()
                skel = skeleton
                joint: Joint = Joint(name)
                if skel is None:
                    skel = Skeleton(joint)
                    self.skeletonObjects.append(skel)
                    self.skeletonNodes[skel] = [[joint, node]]
                    t = self._getNodeGlobalTransform(node)
                else:
                    t = self._getNodeLocalTransform(node)
                    skel.add(joint, parent=parentJoint)
                    self.skeletonNodes[skel].append([joint, node])
                joint.transform.matrix = t.matrix
                self._parseSceneSkeletons(node, skel, joint)
            else:
                self._parseSceneSkeletons(node)

    def _parseSceneAnimations(self) -> None:
        for skel in self.skeletonNodes.keys():

            rootNode = self.skeletonNodes[skel][0][1]
            timeSpan = fbx.FbxTimeSpan()

            if rootNode.GetAnimationInterval(timeSpan):
                animationLenght = timeSpan.GetDuration().GetFrameCount(
                    self.scene.GetGlobalSettings().GetTimeMode()
                )
                timeStart = timeSpan.GetStart().GetSecondDouble()
                timeEnd = timeSpan.GetStop().GetSecondDouble()
            else:
                timeStart = 0
                timeEnd = self.stopTime.GetSecondDouble()
                animationLenght = (int)(
                    (timeEnd - timeStart) * self.framerate + 1
                )

            anim = Animation(self.framerate, skel, animationLenght + 1)
            time = fbx.FbxTime()

            for i in self.skeletonNodes[skel]:
                joint = i[0]
                node = i[1]

                for i in range(animationLenght + 1):
                    t = min(timeStart + i / self.framerate, timeEnd)
                    time.SetSecondDouble(t)
                    if joint.parent is None:
                        transf = (
                            self._getNodeGlobalTransform(node, time)
                            * skel.joints[skel.root.id].transform.inverse()
                        )
                        anim.frames[i].setBonePosition(
                            joint.id, transf.getPosition()
                        )
                        anim.frames[i].setBoneLocalRotation(
                            joint.id, transf.matrix
                        )
                    else:
                        transf = self._getNodeLocalTransform(node, time)
                        anim.frames[i].setBoneLocalRotation(
                            joint.id, transf.matrix
                        )

            self.animations.append(anim)

    @staticmethod
    def _printNodeNames(self, node: fbx.FbxNode, ind: int = 0) -> None:
        s = FBXImporter._getFbxNodeTypeName(node) + ": " + node.GetName()
        for i in range(0, ind):
            s = "  " + s
        print(s)
        for i in range(0, node.GetChildCount()):
            n = node.GetChild(i)
            self._printNodeNames(n, ind + 1)

    @staticmethod
    def _getFbxNodeType(node: fbx.FbxNode) -> Optional[fbx.FbxNodeAttribute]:
        attribType = node.GetNodeAttribute()
        if attribType is None:
            return None
        return attribType.GetAttributeType()

    @staticmethod
    def _getFbxNodeTypeName(node: fbx.FbxNode) -> str:
        e = FBXImporter._getFbxNodeType(node)
        sType = "Unknown"
        if fbx.FbxNodeAttribute.EType.eNull == e:
            sType = "Null"
        elif fbx.FbxNodeAttribute.EType.eMarker == e:
            sType = "Marker"
        elif fbx.FbxNodeAttribute.EType.eSkeleton == e:
            sType = "Skeleton"
        elif fbx.FbxNodeAttribute.EType.eMesh == e:
            sType = "Mesh"
        elif fbx.FbxNodeAttribute.EType.eNurbs == e:
            sType = "Nurbs"
        elif fbx.FbxNodeAttribute.EType.ePatch == e:
            sType = "Patch"
        elif fbx.FbxNodeAttribute.EType.eCamera == e:
            sType = "Camera"
        elif fbx.FbxNodeAttribute.EType.eLight == e:
            sType = "Light"
        return sType

    def _getNodeLocalTransform(
        self, node: fbx.FbxNode, time: fbx.FbxTime = TIME_INFINITY
    ) -> Transform:
        t = Transform()
        matrix = node.EvaluateLocalTransform(time)
        for i in range(0, 4):
            for j in range(0, 4):
                t.matrix[i, j] = matrix[j][i]

        t.matrix[0:3, 3] *= self.systemUnitScale
        return t

    def _getNodeGlobalTransform(
        self, node: fbx.FbxNode, time: fbx.FbxTime = TIME_INFINITY
    ) -> Transform:
        t = Transform()
        matrix = node.EvaluateGlobalTransform(time)
        for i in range(0, 4):
            for j in range(0, 4):
                t.matrix[i, j] = matrix[j][i]

        t.matrix[0:3, 3] *= self.systemUnitScale
        return t

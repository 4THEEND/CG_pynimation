import fbx
from scipy.spatial.transform import Rotation
from pynimation.anim import Animation
from pynimation.anim import Joint
from pynimation.io import Exporter

TIME_INFINITY = fbx.FbxTime(0x7FFFFFFFFFFFFFFF)
FBXSDK_CURVENODE_COMPONENT_X = "X"
FBXSDK_CURVENODE_COMPONENT_Y = "Y"
FBXSDK_CURVENODE_COMPONENT_Z = "Z"
FBXSDK_CURVENODE_CHANNELS = [
    FBXSDK_CURVENODE_COMPONENT_X,
    FBXSDK_CURVENODE_COMPONENT_Y,
    FBXSDK_CURVENODE_COMPONENT_Z,
]


class FBXExporterSettings:
    """
    Data structure containing export settings for the :class:`~pynimation.io.fbx.exporter.FBXExporter` class.

    Parameters
    ----------
    scaleFactor: int
        factor by which to scale the exported scene
    axisSystem: fbx.FbxAxisSystem
        axis system used to export the scene, refer to `FBXSDK API
        <http://help.autodesk.com/view/FBX/2020/ENU/?guid=FBX_Developer_Help_cpp_ref_class_fbx_axis_system_html>`_
        for constructing an axis system or using a predefined one
    """

    def __init__(
        self,
        scaleFactor: int = 100,
        axisSystem: fbx.FbxAxisSystem = fbx.FbxAxisSystem.OpenGL,
    ) -> None:
        self.scaleFactor = scaleFactor
        self.axisSystem = axisSystem


class FBXExporter(Exporter):
    """
    Exporter class for FBX files. Holds data required to export an animation to
    FBX file format

    Attributes
    ----------
    settings: FBXExporterSettings
        settings for the exporter

    Note
    ----
    An exporter instance cannot be re-used to export multiple files
    """

    extension = "fbx"

    def __init__(self) -> None:
        self._manager = fbx.FbxManager.Create()
        self._fbxexporter = fbx.FbxExporter.Create(
            self._manager, "FBXExporter"
        )
        self.settings = FBXExporterSettings()

    def __del__(self) -> None:
        self._fbxexporter.Destroy()
        self._manager.Destroy()

    def save(
        self,
        animation: Animation,
        filename: str,
    ) -> None:
        """
        Export :attr:`animation` to FBX file :attr:`filename` using :attr:`settings`

        Parameters
        ----------
        animation:
            animation to export

        filename:

        settings:
             (Default value = None)

        Returns
        -------

        """

        fbxfile = _FBXFile(
            animation,
            self.settings,
            fbx.FbxScene.Create(self._manager, "Scene"),
        )

        status = self._fbxexporter.Initialize(filename)
        if not status:
            err = "Error: " + self._fbxexporter.GetStatus().GetErrorString()
            raise Exception(err)

        self._fbxexporter.Export(fbxfile.fbxscene)


class _FBXFile:
    def __init__(
        self,
        animation: Animation,
        settings: FBXExporterSettings,
        fbxscene: fbx.FbxScene,
    ) -> None:
        self._animation = animation
        self._settings = settings
        self._animLayer = None
        self._animStack = None

        self.fbxscene = fbxscene
        self._fbxglobalsettings = self.fbxscene.GetGlobalSettings()

        self._setMetadata()

        # Pynimation skeleton root
        self.skeletonRoot = self._animation.skeleton.joints[
            self._animation.skeleton.root.id
        ]

        self.fbxrootNode = self._buildSceneGraph(self.skeletonRoot)
        self.fbxskeletonRoot = self.fbxrootNode.GetChild(0)

        self._animStack = fbx.FbxAnimStack.Create(
            self.fbxscene, "character_animation"
        )
        self._animLayer = fbx.FbxAnimLayer.Create(
            self.fbxscene, "character_animation"
        )
        self._animStack.AddMember(self._animLayer)

        self._animate(self.fbxskeletonRoot, self.skeletonRoot)

    def _setMetadata(self) -> None:
        self._setFrameRate(self._animation.framerate)

        self._setTimespan(0, len(self._animation.frames))

        self._setUnit(self._settings.scaleFactor)

        self._setAxisSystem(self._settings.axisSystem)

    def _setAxisSystem(self, axisSystem: fbx.FbxAxisSystem) -> None:
        self._fbxglobalsettings.SetAxisSystem(axisSystem)

    def _setUnit(self, scaleFactor: int) -> None:
        systemUnit = fbx.FbxSystemUnit(scaleFactor)
        self._fbxglobalsettings.SetSystemUnit(systemUnit)
        self._fbxglobalsettings.SetOriginalSystemUnit(systemUnit)

    def _setTimespan(self, startframe: int, stopframe: int) -> None:
        fbxstart = fbx.FbxTime()
        # fbxstart.SetSecondDouble(start)
        fbxstart.SetFrame(startframe, self._fbxglobalsettings.GetTimeMode())
        fbxstop = fbx.FbxTime()
        fbxstop.SetFrame(stopframe, self._fbxglobalsettings.GetTimeMode())
        # fbxstop.SetSecondDouble(end)
        timespan = fbx.FbxTimeSpan(fbxstart, fbxstop)
        self._fbxglobalsettings.SetTimelineDefaultTimeSpan(timespan)

    def _setFrameRate(self, framerate: int) -> None:
        mode = fbx.FbxTime.ConvertFrameRateToTimeMode(framerate)
        if mode == fbx.FbxTime.EMode.eDefaultMode:
            # time mode is not standard
            # set custom one
            mode = fbx.FbxTime.EMode.eCustom
            self._fbxglobalsettings.SetTimeMode(mode)
            self._fbxglobalsettings.SetCustomFrameRate(framerate)
            fbx.FbxTime.SetGlobalTimeMode(mode, framerate)
        else:
            self._fbxglobalsettings.SetTimeMode(mode)
            fbx.FbxTime.SetGlobalTimeMode(mode)

    def _buildSceneGraph(self, skeletonRoot: Joint) -> fbx.FbxNode:
        fbxskeletonRoot = self._convertSkeleton(
            skeletonRoot, nodeType=fbx.FbxSkeleton.EType.eRoot
        )

        fbxrootNode = self.fbxscene.GetRootNode()
        fbxrootNode.AddChild(fbxskeletonRoot)
        return fbxrootNode

    def _convertSkeleton(
        self,
        joint: Joint,
        nodeType: fbx.FbxSkeleton.EType = fbx.FbxSkeleton.EType.eLimbNode,
    ) -> fbx.FbxNode:
        fbxjoint = self._convertJoint(joint, nodeType)
        for child in joint.children:
            fbxjoint.AddChild(self._convertSkeleton(child))
        return fbxjoint

    def _convertJoint(
        self,
        joint: Joint,
        node_type: fbx.FbxSkeleton.EType = fbx.FbxSkeleton.EType.eLimbNode,
    ) -> fbx.FbxNode:
        fbxskeletonAttribute = fbx.FbxSkeleton.Create(
            self.fbxscene, "Skeleton"
        )
        fbxskeletonAttribute.SetSkeletonType(node_type)
        fbxskeletonAttribute.Size.Set(1.0)

        fbxjoint = fbx.FbxNode.Create(self.fbxscene, joint.name)
        fbxjoint.SetNodeAttribute(fbxskeletonAttribute)

        translation = joint.transform.getPosition().tolist()
        fbxjoint.LclTranslation.Set(
            fbx.FbxDouble3(translation[0], translation[1], translation[2])
        )

        rotation = Rotation.from_matrix(joint.transform.getRotation().tolist())
        rotation = rotation.as_euler("xyz", degrees=True)
        fbxjoint.LclRotation.Set(
            fbx.FbxDouble3(rotation[0], rotation[1], rotation[2])
        )

        scaling = joint.transform.getScale().tolist()
        fbxjoint.LclScaling.Set(
            fbx.FbxDouble3(scaling[0], scaling[1], scaling[2])
        )

        return fbxjoint

    def _animate(self, fbxSkeleton: fbx.FbxNode, skeleton: Joint) -> None:
        self._animateJoint(fbxSkeleton, skeleton)
        for (i, child) in enumerate(skeleton.children):
            self._animate(fbxSkeleton.GetChild(i), child)

    def _animateJoint(self, fbxjoint: fbx.FbxNode, joint: Joint) -> None:
        if joint.id == self._animation.skeleton.root.id:
            # animate translation for root joint
            self._animateComponents(
                fbxjoint.LclTranslation, joint, translation=True
            )
        self._animateComponents(fbxjoint.LclRotation, joint)

    def _animateComponents(
        self,
        fbxproperty: fbx.FbxPropertyDouble3,
        joint: Joint,
        translation: bool = False,
    ) -> None:
        curves = [
            fbxproperty.GetCurve(self._animLayer, component, True)
            for component in FBXSDK_CURVENODE_CHANNELS
        ]
        t = fbx.FbxTime()
        for curve in curves:
            curve.KeyModifyBegin()

        for (i, frame) in enumerate(self._animation.frames):
            t.SetFrame(i, self._fbxglobalsettings.GetTimeMode())

            if translation:
                value = frame.localTransforms[joint.id].getPosition()
            else:
                value = Rotation.from_matrix(
                    frame.localTransforms[joint.id].getRotation()
                ).as_euler("xyz", degrees=True)

            keyIndex = 0
            for (k, curve) in enumerate(curves):
                keyIndex = curve.KeyAdd(t)[0]
                curve.KeySetValue(keyIndex, value[k])
                curve.KeySetInterpolation(
                    keyIndex, fbx.FbxAnimCurveDef.EInterpolationType.eInterpolationLinear
                )

        for curve in curves:
            curve.KeyModifyEnd()

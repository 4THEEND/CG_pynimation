import re
from enum import Enum
from typing import Optional, List, Union, Tuple, Any

from .joint import JointLike
from .joint import Joint
from pynimation.common import TransformGraph

enumId = 0


def _auto() -> int:
    global enumId
    enumId += 1
    return enumId


class Skeleton(TransformGraph[JointLike]):
    """
    Internal representation of an animation's skeleton. The skeleton is made of
    joints, one for each animated limb

    Parameters
    ----------
    root:
        root joint of the skeleton

    Attributes
    ----------
    root:
        root joint of the skeleton

    """

    class SkeletalPart(Enum):
        """
        Enumeration of joint types
        """

        HEAD = _auto()
        NECK = _auto()
        LEFT_CLAVICLE = _auto()
        LEFT_SHOULDER = _auto()
        LEFT_ELBOW = _auto()
        LEFT_WRIST = _auto()
        RIGHT_CLAVICLE = _auto()
        RIGHT_SHOULDER = _auto()
        RIGHT_ELBOW = _auto()
        RIGHT_WRIST = _auto()
        ROOT = _auto()
        LEFT_HIP = _auto()
        LEFT_KNEE = _auto()
        LEFT_ANKLE = _auto()
        LEFT_TOE = _auto()
        RIGHT_HIP = _auto()
        RIGHT_KNEE = _auto()
        RIGHT_ANKLE = _auto()
        RIGHT_TOE = _auto()

        @classmethod
        def defaultSkeleton(cls) -> List["Skeleton.SkeletalPart"]:
            return [
                cls.HEAD,
                cls.NECK,
                cls.LEFT_CLAVICLE,
                cls.LEFT_SHOULDER,
                cls.LEFT_ELBOW,
                cls.LEFT_WRIST,
                cls.RIGHT_CLAVICLE,
                cls.RIGHT_SHOULDER,
                cls.RIGHT_ELBOW,
                cls.RIGHT_WRIST,
                cls.ROOT,
                cls.LEFT_HIP,
                cls.LEFT_KNEE,
                cls.LEFT_ANKLE,
                cls.LEFT_TOE,
                cls.RIGHT_HIP,
                cls.RIGHT_KNEE,
                cls.RIGHT_ANKLE,
                cls.RIGHT_TOE,
            ]

    def __init__(self, root: JointLike) -> None:
        super().__init__(root)
        self.legs: Tuple[JointLike, ...] = ()
        self.upperBody: Optional[JointLike] = None

        self.leftLeg: Optional[JointLike] = None
        self.rightLeg: Optional[JointLike] = None
        self.leftArm: Optional[JointLike] = None
        self.rightArm: Optional[JointLike] = None
        self.headBranch: Optional[JointLike] = None
        self.neck: Optional[JointLike] = None
        self.head: Optional[JointLike] = None
        self.leftClavicle: Optional[JointLike] = None
        self.leftShoulder: Optional[JointLike] = None
        self.leftElbow: Optional[JointLike] = None
        self.leftWrist: Optional[JointLike] = None
        self.rightClavicle: Optional[JointLike] = None
        self.rightShoulder: Optional[JointLike] = None
        self.rightElbow: Optional[JointLike] = None
        self.rightWrist: Optional[JointLike] = None
        self.leftHip: Optional[JointLike] = None
        self.leftKnee: Optional[JointLike] = None
        self.leftAnkle: Optional[JointLike] = None
        self.leftToe: Optional[JointLike] = None
        self.rightHip: Optional[JointLike] = None
        self.rightKnee: Optional[JointLike] = None
        self.rightAnkle: Optional[JointLike] = None
        self.rightToe: Optional[JointLike] = None

        self.proxyBone: Optional[JointLike] = None

    @property
    def joints(self) -> Tuple[JointLike, ...]:
        """
        Joints of the skeleton
        """
        return self.nodes

    @property
    def jointsNames(self) -> Tuple[str, ...]:
        """
        Set of joint names
        """
        return tuple(a.name for a in self.nodes)

    def mapHumanoidSkeleton(self) -> None:
        # Case where it is not a triangle pelvis (i.e., hips are attached to the first spine node)
        rootBranches: Tuple[JointLike, ...] = self.root.children
        while len(rootBranches) == 1:
            rootBranches = rootBranches[0].children

        self._parseLegsAndUpperBody(rootBranches)

        self.SkeletalPartSwitcher = {
            self.SkeletalPart.HEAD: self.head,
            self.SkeletalPart.NECK: self.neck,
            self.SkeletalPart.LEFT_CLAVICLE: self.leftClavicle,
            self.SkeletalPart.LEFT_SHOULDER: self.leftShoulder,
            self.SkeletalPart.LEFT_ELBOW: self.leftElbow,
            self.SkeletalPart.LEFT_WRIST: self.leftWrist,
            self.SkeletalPart.RIGHT_CLAVICLE: self.rightClavicle,
            self.SkeletalPart.RIGHT_SHOULDER: self.rightShoulder,
            self.SkeletalPart.RIGHT_ELBOW: self.rightElbow,
            self.SkeletalPart.RIGHT_WRIST: self.rightWrist,
            self.SkeletalPart.ROOT: self.root,
            self.SkeletalPart.LEFT_HIP: self.leftHip,
            self.SkeletalPart.LEFT_KNEE: self.leftKnee,
            self.SkeletalPart.LEFT_ANKLE: self.leftAnkle,
            self.SkeletalPart.LEFT_TOE: self.leftToe,
            self.SkeletalPart.RIGHT_HIP: self.rightHip,
            self.SkeletalPart.RIGHT_KNEE: self.rightKnee,
            self.SkeletalPart.RIGHT_ANKLE: self.rightAnkle,
            self.SkeletalPart.RIGHT_TOE: self.rightToe,
        }

    def _parseLegsAndUpperBody(
        self, rootBranches: Tuple[JointLike, ...]
    ) -> None:
        unusedBranches: List[JointLike] = []
        for branch in rootBranches:
            if not self.upperBody:
                if self._searchNamesInBranch(
                    [
                        "spine",
                        "shoulder",
                        "clavicle",
                        "elbow",
                        "wrist",
                        "neck",
                        "head",
                    ],
                    branch,
                ):
                    self.upperBody = branch
            elif self._searchNamesInBranch(
                ["leg", "hip", "knee", "ankle", "foot"], branch
            ):
                self.legs = (*self.legs, branch)
            else:
                unusedBranches.append(branch)

        if self.legs:
            self._parseLowerBody()

        if self.upperBody:
            self._parseUpperBody()

    def _parseLowerBody(self) -> None:
        for b in self.legs:
            if self.leftLeg is None:
                if self._searchNamesInBranch(["Left", "L_", "L"], b):
                    self.leftLeg = b
                    continue
            if self.rightLeg is None:
                if self._searchNamesInBranch(["Right", "R_", "R"], b):
                    self.rightLeg = b
                    continue

        if self.leftLeg is None or self.rightLeg is None:
            return  # Not handled yet, look at checking for left/right ortientation of torso?

        self.leftHip = self.leftLeg
        self.leftKnee = self._searchNamesInBranch(
            "Knee", self.leftLeg.children[0]
        )
        self.leftAnkle = self._searchNamesInBranch(
            ["Ankle", "Foot"], self.leftLeg.children[0]
        )
        self.leftToe = self._searchNamesInBranch(
            "Toe", self.leftLeg.children[0]
        )

        if not self.leftKnee:
            if self.leftAnkle:
                self.leftKnee = self.leftAnkle.parent
            else:
                j = self._searchNamesInBranch("Leg", self.leftLeg.children[0])
                if j:
                    self.leftKnee = j
                else:
                    self.leftKnee = self.leftHip.children[0]

        self.rightHip = self.rightLeg
        self.rightKnee = self._searchNamesInBranch(
            "Knee", self.rightLeg.children[0]
        )
        self.rightAnkle = self._searchNamesInBranch(
            ["Ankle", "Foot"], self.rightLeg.children[0]
        )
        self.rightToe = self._searchNamesInBranch(
            "Toe", self.rightLeg.children[0]
        )

        if not self.rightKnee:
            if self.rightAnkle:
                self.rightKnee = self.rightAnkle.parent
            else:
                j = self._searchNamesInBranch("Leg", self.rightLeg.children[0])
                if j:
                    self.rightKnee = j
                else:
                    self.rightKnee = self.rightHip.children[0]

    def _parseUpperBody(self) -> None:
        assert self.upperBody is not None
        branches = self.upperBody.children
        while len(branches) == 1:
            branches = branches[0].children

        unusedBranches = []
        for b in branches:
            if not self.headBranch:
                if self._searchNamesInBranch(["Neck", "Head"], b):
                    self.headBranch = b
                    continue
            if not self.leftArm:
                if self._searchNamesInBranch(["Left", "L_"], b):
                    self.leftArm = b
                    continue
            if not self.rightArm:
                if self._searchNamesInBranch(["Right", "R_"], b):
                    self.rightArm = b
                    continue
            unusedBranches.append(b)

        if self.headBranch:
            self.neck = self._searchNamesInBranch("Neck", self.headBranch)
            self.head = self._searchNamesInBranch("Head", self.headBranch)

        if self.leftArm:
            self.leftClavicle = self._searchNamesInBranch(
                "Clavicle", self.leftArm
            )
            self.leftShoulder = self._searchNamesInBranch(
                ["Arm", "Shoulder"], self.leftArm
            )
            self.leftElbow = self._searchNamesInBranch(
                ["Elbow", "Forearm"], self.leftArm
            )
            self.leftWrist = self._searchNamesInBranch(
                ["Wrist", "Hand"], self.leftArm
            )

            if (
                self.leftElbow
                and self.leftElbow.parent is not self.leftShoulder
            ):
                self.leftClavicle = self.leftShoulder
                self.leftShoulder = self.leftElbow.parent

        if self.rightArm:
            self.rightClavicle = self._searchNamesInBranch(
                "Clavicle", self.rightArm
            )
            self.rightShoulder = self._searchNamesInBranch(
                ["Arm", "Shoulder"], self.rightArm
            )
            self.rightElbow = self._searchNamesInBranch(
                ["Elbow", "Forearm"], self.rightArm
            )
            self.rightWrist = self._searchNamesInBranch(
                ["Wrist", "Hand"], self.rightArm
            )

            if (
                self.rightElbow
                and self.rightElbow.parent is not self.rightShoulder
            ):
                self.rightClavicle = self.rightShoulder
                self.rightShoulder = self.rightElbow.parent

    def _searchNamesInBranch(
        self, names: Union[List[str], str], joint: JointLike
    ) -> Optional[JointLike]:
        if isinstance(names, list):
            for n in names:
                if re.search(n, joint.name, re.IGNORECASE):
                    return joint
        elif isinstance(names, str):
            if re.search(names, joint.name, re.IGNORECASE):
                return joint

        for c in joint.children:
            j = self._searchNamesInBranch(names, c)
            if j:
                return j
        return None

    def getSkeletalPart(
        self, sp: "Skeleton.SkeletalPart"
    ) -> Optional[JointLike]:
        """
        Get the joint that :attr:`sp` refers to

        Parameters
        ----------
        sp:
            skeletal part to get


        Returns
        -------
        Joint:
            joint corresponding to :attr:`sp`

        """
        return self.SkeletalPartSwitcher.get(sp, None)

    def getSubSkeleton(
        self,
        skeletonDefinition: Optional[List["Skeleton.SkeletalPart"]] = None,
    ) -> List[JointLike]:
        """
        Get the set of joints that :attr:`skeletonDefinition` refers to

        Parameters
        ----------
        skeletonDefinition:
            set of joints to retrieve


        Returns
        -------
            set of joints corresponding to :attr:`skeletonDefinition`

        """
        if skeletonDefinition:
            return [
                self.joints.index(joint)
                for joint in [
                    self.getSkeletalPart(sp) for sp in skeletonDefinition
                ]
                if joint is not None
            ]
        else:
            return [self.joints.index(j) for j in self.joints]

    def createProxyBone(self) -> None:
        """
        Creates a proxy bone, with the original root as direct child

        Parameters
        ----------

        Returns
        -------
        """
        self.proxyBone: Optional[JointLike] = Joint("Proxy")
        oldRoot = self.root
        # reset joints ids
        for n in self.nodes:
            n._id = -1
        assert self.proxyBone is not None
        self.root = self.proxyBone
        self.proxyBone.addChild(oldRoot)

    def destroyProxyBone(self) -> None:
        """
        Destroy the proxy bone, the original root becomes the new root

        Parameters
        ----------

        Returns
        -------
        """
        if self.proxyBone is None:
            return

        self.root = self.proxyBone.children[0]
        # reset joints ids
        for n in self.nodes:
            n._id = -1

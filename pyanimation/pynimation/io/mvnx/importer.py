import numpy
import time

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from pyquaternion import Quaternion
from typing import List, Optional

from pynimation.anim import Skeleton
from pynimation.anim import Animation
from pynimation.anim import Joint
from pynimation.common import Transform
from pynimation.io import Importer
from pynimation.common import data as data_


class MVNXImporter(Importer):
    """
    Import animations from MVNX files
    """

    extension = "mvnx"

    def __init__(self, numberOfFrames: int = 0):
        self._clear()
        self._ns = {"mvnx": "http://www.xsens.com/mvn/mvnx"}
        self._skelStructure = ET.parse(
            data_.getDataPath("data/animations/mvnxSkeleton.xml")
        ).getroot()
        self._frameRate: int = 0
        self.numberOfFrames: int = numberOfFrames

    def _clear(self) -> None:
        self._skeleton: Optional[Skeleton] = None
        self._animation: Animation = None

    def load(self, filename: str) -> List["Animation"]:
        self._clear()

        rootMVNX = ET.parse(filename).getroot()

        for subject in rootMVNX.findall("mvnx:subject", self._ns):
            self._loadSubject(subject, self.numberOfFrames)
        return [self._animation]

    def _loadSubject(
        self, subject: Element, numberOfFrames: int = None
    ) -> None:

        frames = subject.find("mvnx:frames", self._ns)
        self._frameRate = int(subject.attrib["frameRate"])
        if frames is None:
            raise Exception(
                "Error while reading MVNX file : could not find frames element"
            )
        identity = frames[0]

        self._skeleton = self._loadSkeleton(identity)

        self._loadAnimation(frames, self._skeleton)

    def _loadSkeleton(self, identityFrame: Element) -> Skeleton:

        root = self._skelStructure.find("Joint")
        if root is None:
            raise Exception(
                "Error while reading squeleton file : could not find root joint element"
            )
        self._loadJointMVNX(None, root, None)

        assert self._skeleton is not None

        globalTransforms = self._loadGlobalTransforms(identityFrame)

        for joint in self._skeleton.joints:
            if joint.parent is not None:
                localTrans = (
                    globalTransforms[joint.parent.id].inverse()
                    * globalTransforms[joint.id]
                )
                joint.transform.setPosition(localTrans.getPosition())

        return self._skeleton

    def _loadGlobalTransforms(self, frame: Element) -> List[Transform]:

        frPos = frame.find("mvnx:position", self._ns)
        frRot = frame.find("mvnx:orientation", self._ns)

        if frPos is None or frRot is None:
            raise Exception(
                "Error while reading MVNX file : could not find rotation or position element"
            )
        elif frPos.text is None or frRot.text is None:
            raise Exception(
                "Error while reading MVNX file : empty rotation or position element"
            )

        rotations = numpy.asarray([float(a) for a in (frRot.text.split())])
        positions = numpy.asarray([float(a) for a in (frPos.text.split())])

        rotations = numpy.split(rotations, len(rotations) / 4)
        positions = numpy.split(positions, len(positions) / 3)

        # SI changement de repère à faire

        globalTransforms = [None] * len(rotations)
        for i in range(len(rotations)):

            positions[i] = [positions[i][1], positions[i][2], positions[i][0]]
            rotations[i] = [
                rotations[i][0],
                rotations[i][2],
                rotations[i][3],
                rotations[i][1],
            ]  # TO FIX

            t = Transform()
            t.setPosition(positions[i])
            t.setRotation(Quaternion(rotations[i]).rotation_matrix)
            globalTransforms[i] = t

        return globalTransforms

    def _loadAnimation(self, frames: Element, skeleton: Skeleton) -> None:
        self._animation = Animation(self._frameRate, skeleton, len(frames) - 3)
        t = time.perf_counter() * 1000
        for fr in frames:
            if fr.attrib["type"] == "normal":
            #if "index" in fr.attrib:
                frame = self._animation.frames[int(fr.attrib["index"])]
                globalTransforms = self._loadGlobalTransforms(fr)
                for joint in skeleton.joints:
                    if joint.parent is not None:
                        localRot = (
                            globalTransforms[joint.parent.id].inverse()
                            * globalTransforms[joint.id]
                        )
                        frame.localTransforms[joint.id].setRotation(
                            localRot.getRotation()
                        )
                    else:
                        frame.localTransforms[joint.id] = globalTransforms[
                            joint.id
                        ]

        print("Finished: " + str(time.perf_counter() * 1000 - t))

    def _loadJointMVNX(
        self,
        skeleton: Optional[Skeleton],
        currentNode: Element,
        parent: Optional[Joint],
    ):

        joint = Joint(currentNode.attrib["name"])
        if skeleton is None:
            self._skeleton = Skeleton(joint)
            skeleton = self._skeleton
            assert parent is None

        skeleton.add(joint, parent=parent)

        for child in currentNode.findall("Joint"):
            self._loadJointMVNX(skeleton, child, joint)

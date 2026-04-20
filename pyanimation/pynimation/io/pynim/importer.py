import os, time
from typing import Dict, Optional, Any, List
from numpy.testing._private.utils import assert_equal

from pyquaternion import Quaternion

from pynimation.io.importer import Importer
from pynimation.io.pynim.exporter import PynimExporter
from pynimation.io import BinaryReader
from pynimation.anim import Skeleton
from pynimation.anim import Joint
from pynimation.anim import Animation
from pynimation.anim import Frame
import pynimation.io.common as common

class PynimImporter(Importer):
    """
    Importer class for Pynim binary files (internal file format).
    """

    extension = "pynim"

    def load(self, filename: str, **options: Any) -> List[Animation]:
        """
        Load animation from ".pynim" file :attr:`filename`

        Parameters
        ----------
        filename:
            ".pynim" file to Load
        options:
            dict of import options

        Returns
        -------
        List[Animation]:
            animation loaded from :attr:`filename`
        """

        with BinaryReader(filename) as bn:

            skeleton = self.loadSkeleton(bn)

            #bn.readBool()  # isCyclic
            # animation.isCyclic = isCyclic REMOVED FROM CURRENT ANIMATION IMPLEMENTATION
            # REMOVING THE READBOOL/WRITEBOOL REQUIRES TO REGENERATE OLD PYNIM FILES
            version = bn.readInt()
            assert_equal(version, PynimExporter.CURRENT_VERSION, "Pynim file version is incorrect (current = {}, requested={}). Cannot be loaded".format(PynimExporter.CURRENT_VERSION, version))
            framerate = bn.readFloat()
            frameNumber = bn.readInt()

            t = time.perf_counter()
        
            animation = Animation(framerate, skeleton, frameNumber)

            id = 0
            for fr in animation.frames:
                pc = int(float(id) / float(animation.getFrameNumber() - 1) * 100)
                print('\rLoading {}: {}%'.format(os.path.basename(filename),pc), end='')
                self.loadFrame(bn, skeleton, fr)
                id += 1

            print(" - Finished ({0:.2f}s)".format(time.perf_counter() - t))

        return [animation]

    @staticmethod
    def loadSkeleton(bn: BinaryReader) -> Skeleton:
        """
        Load the skeleton found in the ".pynim" file opened by
        :class:`~pynimation.io.binarywriter.BinaryWriter` :attr:`bn`

        Parameters
        ----------
        bn:
            Binary reader handle

        Returns
        -------
        Skeleton:
            skeleton loaded from opened file of :attr:`bn`
        """

        rootJointId = bn.readUnsignedShortInt()
        jointNumber = bn.readUnsignedShortInt()
        proxyId = bn.readShortInt()

        joints: Dict[int, Joint] = {}

        for j in range(jointNumber):
            jointName = bn.readString()
            jointID = bn.readUnsignedShortInt()
            jointParent = bn.readShortInt()
            jointPosition = bn.readVector(3)
            jointQuaternion = bn.readVector(4)

            parent = None if jointParent == -1 else joints[jointParent]
            joint = Joint(jointName, parent, None, list(jointPosition))
            joint.transform.setRotation(
                Quaternion(jointQuaternion).rotation_matrix
            )
            joints[jointID] = joint

        skel = Skeleton(joints[rootJointId])
        if proxyId >= 0:
            skel.proxyBone = skel.nodes[proxyId]

        return skel

    @staticmethod
    def loadFrame(
        bn: BinaryReader, skeleton: Skeleton, frame: Optional[Frame] = None
    ) -> Frame:
        """
        Load the next frame found at the current cursor position in
        the ".pynim" file opened by :class:`~pynimation.io.binarywriter.BinaryWriter`
        :attr:`bn`

        Parameters
        ----------
        bn:
            Binary reader handle

        skeleton:
            Skeleton representing the frame

        frame:
            if provided, load the data in the frame, otherwise create and return a new frame

        Returns
        -------
        Skeleton:
            skeleton loaded from opened file of :attr:`bn`
        """

        if frame is None:
            frame = Frame(skeleton)

        for jj in skeleton.joints:
            frame.setBonePosition(jj.id, bn.readVector(3))
            frame.setBoneLocalRotation(
                jj.id, Quaternion(bn.readVector(4)).rotation_matrix
            )

        return frame

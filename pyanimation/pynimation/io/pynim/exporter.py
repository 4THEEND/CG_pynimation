from typing import Any

import pynimation.io.common as common
from pynimation.io.exporter import Exporter
from pynimation.io import BinaryWriter
from pynimation.anim import Animation
from pynimation.anim import Skeleton
from pynimation.anim import Frame

class PynimExporter(Exporter):
    """
    Exporter class for Pynim binary files (internal file format).
    """

    CURRENT_VERSION = 4

    extension = "pynim"

    def save(
        self, animation: Animation, filename: str, **options: Any
    ) -> None:
        """
        Export :attr:`animation` to Pynim file :attr:`filename`

        Parameters
        ----------
        animation:
            animation to export

        filename:
            path to save the animation to

        options:
            options of the exporter, see ExporterOptions, IOOptions and options
            classes of exporter implementations
        """

        with BinaryWriter(filename) as bn:

            self.saveSkeleton(animation.skeleton, bn)

            bn.writeInt(PynimExporter.CURRENT_VERSION)
            bn.writeFloat(animation.framerate)
            bn.writeInt(animation.getFrameNumber())

            for frame in animation.frames:
                self.saveFrame(frame, bn)

    @staticmethod
    def saveSkeleton(skeleton: Skeleton, bn: BinaryWriter) -> None:
        """
        Export :attr:`skeleton` to binarywriter handle :attr:`bn`

        Parameters
        ----------
        skeleton:
            skeleton to export

        bn:
            Binary writer handle

        """

        bn.writeUnsignedShortInt(skeleton.root.id)
        bn.writeUnsignedShortInt(len(skeleton.joints))
        bn.writeShortInt(skeleton.proxyBone.id if skeleton.proxyBone else -1)

        for joint in skeleton.joints:
            bn.writeString(joint.name)
            bn.writeUnsignedShortInt(joint.id)
            if joint.parent is None:
                parent = -1
            else:
                parent = joint.parent.id
            bn.writeShortInt(parent)
            bn.writeVector(joint.transform.getPosition())
            bn.writeVector(joint.transform.getQuaternion().elements)

    @staticmethod
    def saveFrame(frame: Frame, bn: BinaryWriter) -> None:
        """
        Export :attr:`frame` to binarywriter handle :attr:`bn`

        Parameters
        ----------
        frame:
            frame to export

        bn:
            Binary writer handle

        """

        for trans in frame.localTransforms:
            bn.writeVector(trans.getPosition())
            bn.writeVector(trans.getQuaternion().elements)

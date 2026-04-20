import numpy
import math

from .. import VBObject
from pynimation.common import RotationTools
from pynimation.common import Transform
from numpy import float64
from typing import List, Union


class Capsule(VBObject):
    """
    A 3D capsule mesh for displaying a skeleton's joint

    Parameters
    ----------
    jointID: int:
        id of the joint displayed
    defaultRotation: Transform:
        default rotation of the mesh
    length: float:
        length of the capsule
    radius: float:
        radius of the capsule
    center: bool:
        whether to center the capsule around the bone or align it to the bone
    numberSegments: int:
        number of segments on the cross-section

    Attributes
    ----------
    jointID: int:
        id of the joint displayed
    defaultRotation: Transform:
        default rotation of the mesh
    length: float:
        length of the capsule
    radius: float:
        radius of the capsule
    numberSegments: int:
        number of segments on the cross-section
    """

    def __init__(
        self,
        jointID: int = 0,
        defaultRotation: Transform = Transform(),
        length: float64 = 1.0,
        radius: float = 1.0,
        center: bool = True,
        color: List[Union[float, int]] = [0.5, 0.5, 0.5, 1],
        numberSegments: int = 8,
    ) -> None:

        self.nbSegments = numberSegments
        self.radius = radius
        self.length = length
        self.color = color
        self.jointID = jointID
        self.defaultRotation = defaultRotation

        LIST_VERTICES = []
        LIST_COLORS = []
        LIST_NORMALS = []
        LIST_VERTEXINDEX: List[int] = []

        p = [0.0, 0.0, 0.0]
        n = [0.0, 0.0, 0.0]
        nbVertSeg = (int)(self.nbSegments / 2)

        limSeg = (int)(nbVertSeg / 2)
        if center:
            yOffset = -self.length * 0.5
        else:
            yOffset = 0
        listOfIdx = list(range(-limSeg + 1, 1)) + list(range(0, limSeg))

        LIST_VERTICES.append([0.0, -self.radius + yOffset, 0.0])
        LIST_COLORS.append(self.color)
        LIST_NORMALS.append([0.0, -1.0, 0.0])

        nbIntermSeg = len(listOfIdx)
        for k in range(0, nbIntermSeg):
            s = listOfIdx[k]
            angle = s / limSeg * math.pi * 0.5
            r = math.cos(angle) * self.radius
            p[1] = math.sin(angle) * radius + yOffset
            n[1] = math.sin(angle) * radius

            if s == 0:
                if center:
                    yOffset = abs(yOffset)
                else:
                    yOffset = self.length

            for i in range(0, self.nbSegments):
                angle = i / self.nbSegments * 2 * math.pi
                p[0] = r * math.cos(angle)
                p[2] = r * math.sin(angle)
                LIST_VERTICES.append(p.copy())
                LIST_COLORS.append(self.color)
                LIST_NORMALS.append(
                    RotationTools.normalize([p[0], n[1], p[2]])
                )

                if k == 0:
                    self.createFaceIndexes(
                        LIST_VERTEXINDEX,
                        0,
                        i + 1,
                        1 + (i + 1) % self.nbSegments,
                    )
                else:
                    self.createFaceIndexes(
                        LIST_VERTEXINDEX,
                        (k - 1) * self.nbSegments + i + 1,
                        k * self.nbSegments + i + 1,
                        k * self.nbSegments + (i + 1) % self.nbSegments + 1,
                        (k - 1) * self.nbSegments
                        + (i + 1) % self.nbSegments
                        + 1,
                    )

        LIST_VERTICES.append([0.0, self.radius + yOffset, 0.0])
        LIST_COLORS.append(self.color)
        LIST_NORMALS.append([0.0, 1.0, 0.0])

        # Create top face indexes
        lastVertexIdx = len(LIST_VERTICES) - 1
        for i in range(1, self.nbSegments + 1):
            self.createFaceIndexes(
                LIST_VERTEXINDEX,
                (nbIntermSeg - 1) * self.nbSegments + i,
                lastVertexIdx,
                (nbIntermSeg - 1) * self.nbSegments
                + (i % self.nbSegments)
                + 1,
            )

        data = {}
        data["vPosition"] = numpy.array(LIST_VERTICES, dtype="float32")
        data["vColor"] = numpy.array(LIST_COLORS, dtype="float32")
        data["vNormal"] = numpy.array(LIST_NORMALS, dtype="float32")

        super(Capsule, self).__init__(
            data, numpy.array(LIST_VERTEXINDEX, dtype="int32")
        )

import numpy
import math

from .. import VBObject
from pynimation.common import RotationTools


class Sphere(VBObject):
    """
    A 3D sphere mesh

    Parameters
    ----------
    radius: float:
        radius of the sphere
    color: numpy.ndarray:
        sphere color as RGB array
    numberSegments: int:
        number of segment on a central half section of the sphere

    Attributes
    ----------
    radius: float:
        radius of the sphere
    color: numpy.ndarray:
        sphere color as RGB array
    numberSegments: int:
        number of segment on a central half section of the sphere

    """

    def __init__(
        self, radius=1.0, color=[0.5, 0.5, 0.5, 1], numberSegments=32
    ):

        self.nbSegments = numberSegments
        self.radius = radius
        self.color = color

        LIST_VERTICES = []
        LIST_COLORS = []
        LIST_NORMALS = []
        LIST_VERTEXINDEX = []

        p = [1.0, -1.0, 0.0]
        nbVertSeg = (int)(self.nbSegments / 2)

        LIST_VERTICES.append([0.0, -self.radius, 0.0])
        LIST_COLORS.append(self.color)
        LIST_NORMALS.append([0.0, -1.0, 0.0])

        for s in range(1, nbVertSeg):
            angle = (s / nbVertSeg - 0.5) * math.pi
            r = math.cos(angle) * self.radius
            p[1] = math.sin(angle) * radius

            for i in range(0, self.nbSegments):
                angle = i / self.nbSegments * 2 * math.pi
                p[0] = r * math.cos(angle)
                p[2] = r * math.sin(angle)
                LIST_VERTICES.append(p.copy())
                LIST_COLORS.append(self.color)
                LIST_NORMALS.append(
                    RotationTools.normalize([p[0], p[1], p[2]])
                )

                if s == 1:
                    self.createFaceIndexes(
                        LIST_VERTEXINDEX,
                        0,
                        i + 1,
                        1 + (i + 1) % self.nbSegments,
                    )
                else:
                    self.createFaceIndexes(
                        LIST_VERTEXINDEX,
                        (s - 2) * self.nbSegments + i + 1,
                        (s - 1) * self.nbSegments + i + 1,
                        (s - 1) * self.nbSegments
                        + (i + 1) % self.nbSegments
                        + 1,
                        (s - 2) * self.nbSegments
                        + (i + 1) % self.nbSegments
                        + 1,
                    )

        LIST_VERTICES.append([0.0, self.radius, 0.0])
        LIST_COLORS.append(self.color)
        LIST_NORMALS.append([0.0, 1.0, 0.0])

        # Create top face indexes
        lastVertexIdx = len(LIST_VERTICES) - 1
        for i in range(1, self.nbSegments + 1):
            self.createFaceIndexes(
                LIST_VERTEXINDEX,
                (nbVertSeg - 2) * self.nbSegments + i,
                lastVertexIdx,
                (nbVertSeg - 2) * self.nbSegments + (i % self.nbSegments) + 1,
            )

        data = {}
        data["vPosition"] = numpy.array(LIST_VERTICES, dtype="float32")
        data["vColor"] = numpy.array(LIST_COLORS, dtype="float32")
        data["vNormal"] = numpy.array(LIST_NORMALS, dtype="float32")

        super(Sphere, self).__init__(
            data, numpy.array(LIST_VERTEXINDEX, dtype="int32")
        )

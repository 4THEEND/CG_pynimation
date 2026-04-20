import numpy

from .. import VBObject
import pynimation.common.data as data_

VERTICES = [
    [-1.0, -1.0, 1.0],
    [-1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0],
    [1.0, -1.0, 1.0],
    [-1.0, -1.0, -1.0],
    [-1.0, 1.0, -1.0],
    [1.0, 1.0, -1.0],
    [1.0, -1.0, -1.0],
]

COLORS = [
    [0.0, 0.0, 0.0, 1.0],  # Black
    [1.0, 0.0, 0.0, 1.0],  # Red
    [1.0, 1.0, 0.0, 1.0],  # Yellow
    [0.0, 1.0, 0.0, 1.0],  # Green
    [0.0, 0.0, 1.0, 1.0],  # Blue
    [1.0, 0.0, 1.0, 1.0],  # Magenta
    [1.0, 1.0, 1.0, 1.0],  # White
    [0.0, 1.0, 1.0, 1.0],
]  # Cyan

QUAD_IDS = [
    [1, 0, 3, 2],
    [2, 3, 7, 6],
    [3, 0, 4, 7],
    [6, 5, 1, 2],
    [4, 5, 6, 7],
    [5, 4, 0, 1],
]


class Cube(VBObject):
    """
    A 3D cube mesh

    Parameters
    ----------
    width: float:
        width of the cube's sides
    color: numpy.ndarray:
        cube color as RGB array

    Attributes
    ----------
    width: float:
        width of the cube's sides
    """

    def __init__(self, width=1.0, color=None) -> None:

        LIST_VERTICES = []
        LIST_COLORS = []
        FACEIDS = [0, 1, 2, 0, 2, 3]
        VERTEX_IDX = []

        self.width = width

        for i, value in enumerate(QUAD_IDS, 1):
            for j, v in enumerate(FACEIDS, 1):
                LIST_VERTICES.append(
                    [x * width * 0.5 for x in VERTICES[value[v]]]
                )
                if color:
                    LIST_COLORS.append(color)
                else:
                    LIST_COLORS.append(COLORS[value[v]])
                VERTEX_IDX.append(value[v])

        LIST_NORMALS = self.computeNormals(LIST_VERTICES)

        # vertSh = "diffuse_vs"
        # fragSh = "diffuse_ps"
        vertSh = "phongShading_vs"
        fragSh = "phongShading_ps"
        vertFileName = data_.getDataPath("data/shaders/" + vertSh + ".glsl")
        fragFileName = data_.getDataPath("data/shaders/" + fragSh + ".glsl")

        with open(vertFileName) as file:
            VERT = file.read()
        with open(fragFileName) as file:
            FRAG = file.read()

        data = {}
        # useIdxArray = False
        # if(useIdxArray):
        #     data["vPosition"] = numpy.array(VERTICES, dtype='float32')
        #     data["vColor"] = numpy.array(COLORS, dtype='float32')
        #     super(Cube, self).__init__(VERT, FRAG, data, numpy.array(VERTEX_IDX, dtype='int32'))
        # else:
        data["vPosition"] = numpy.array(LIST_VERTICES, dtype="float32")
        data["vColor"] = numpy.array(LIST_COLORS, dtype="float32")
        data["vNormal"] = numpy.array(LIST_NORMALS, dtype="float32")
        super(Cube, self).__init__(data, None, VERT, FRAG)

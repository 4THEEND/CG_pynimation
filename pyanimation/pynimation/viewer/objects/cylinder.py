import numpy
import math
from .. import VBObject
import pynimation.common.data as data_


# TODO
# 1. define the color of each vertex
class Cylinder(VBObject):
    """
    A 3D Cylinder

    Parameters
    ----------
    height : float, optional
        The height of the cylinder, by default 4.0
    radiusBase : float, optional
        The radius of the base, by default 1.0
    radiusTop : float, optional
        The radius of the top, by default 1.0
    numberOfSectors : int, optional
        The number of sectors, by default 15
    numberOfStacks : int, optional
        The number of stack, by default 3
    center : bool, optional
        Define if the cylinder is centered on the center(True) or on the base(False), by default True
    color : list, optional
        The color of the cylinder, by default [0.5, 0.5, 0.5, 1]
    height_direction : str, optional
        The default, axis aligned direction, by default "z"
    phong : bool, optional
        The selected shader, if True phong is selected, otherwise Diffuse, by default False

    Attributes
    ----------
    height : float, optional
        The height of the cylinder, by default 4.0
    radiusBase : float, optional
        The radius of the base, by default 1.0
    radiusTop : float, optional
        The radius of the top, by default 1.0
    numberOfSectors : int, optional
        The number of sectors, by default 15
    numberOfStacks : int, optional
        The number of stack, by default 3
    center : bool, optional
        Define if the cylinder is centered on the center(True) or on the base(False), by default True
    color : list, optional
        The color of the cylinder, by default [0.5, 0.5, 0.5, 1]
    height_direction : str, optional
        The default, axis aligned direction, by default "z"
    phong : bool, optional
        The selected shader, if True phong is selected, otherwise diffuse, by default False
    """

    def __init__(
        self,
        height=4.0,
        radiusBase=1.0,
        radiusTop=1.0,
        numberOfSectors=15,
        numberOfStacks=3,
        center=True,
        color=[0.5, 0.5, 0.5, 1],
        height_direction="z",
        phong=False,
    ):
        """[summary]"""
        self.height = height
        self.radiusBase = radiusBase
        self.radiusTop = radiusTop
        self.numberOfSectors = numberOfSectors
        self.numberOfStacks = numberOfStacks
        self.center = center
        self.color = color
        self.baseCenterIndex = 0
        self.topCenterIndex = 0

        self.radius = radiusBase

        LIST_VERTICES = []
        LIST_COLORS = []
        LIST_NORMALS = []
        LIST_VERTEXINDEX = []

        p = [0.0, 0.0, 0.0]

        coord = [0, 1, 2]
        if height_direction == "x" or height_direction == "X":
            coord[0] = 1
            coord[1] = 2
            coord[2] = 0
        elif height_direction == "y" or height_direction == "Y":
            coord[0] = 2
            coord[1] = 0
            coord[2] = 1
        elif height_direction == "z" or height_direction == "Z":
            coord[0] = 0
            coord[1] = 1
            coord[2] = 2
        else:
            print("NOT DEFINED DIRECTION")

        # base
        center_base = [0.0, 0.0, 0.0]
        LIST_VERTICES.append(center_base)
        LIST_NORMALS.append([0.0, 0.0, -1.0])
        LIST_COLORS.append(self.color)
        index_base_start = 1
        index_start = index_base_start
        for i in range(self.numberOfSectors + 1):
            angle = 2 * math.pi * (i / self.numberOfSectors)
            p[coord[0]] = self.radiusBase * math.cos(angle)
            p[coord[1]] = self.radiusBase * math.sin(angle)
            p[coord[2]] = 0
            LIST_VERTICES.append(p.copy())
            LIST_NORMALS.append(p.copy())
            LIST_COLORS.append(self.color)

        for i in range(0, self.numberOfSectors):
            index = i + index_start
            a = index_start
            b = index
            c = index + 1
            if i == self.numberOfSectors - 1:
                c = index_start + 1
            self.createFaceIndexes(LIST_VERTEXINDEX, a, b, c)

        # top
        center_top = [0, 0, self.height]
        LIST_VERTICES.append(center_top)
        LIST_NORMALS.append([0.0, 0.0, 1.0])
        LIST_COLORS.append(self.color)
        index_top_start = len(LIST_VERTICES)
        index_start = index_top_start
        for i in range(self.numberOfSectors + 1):
            angle = 2 * math.pi * (i / self.numberOfSectors)
            p[coord[0]] = self.radiusTop * math.cos(angle)
            p[coord[1]] = self.radiusTop * math.sin(angle)
            p[coord[2]] = self.height
            LIST_VERTICES.append(p.copy())
            p[coord[2]] = 0
            LIST_NORMALS.append(p.copy())
            LIST_COLORS.append(self.color)

        for i in range(0, self.numberOfSectors):
            index = i + index_start
            a = index_start
            b = index
            c = index + 1
            if i == self.numberOfSectors - 1:
                c = index_start + 1
            self.createFaceIndexes(LIST_VERTEXINDEX, a, b, c)

        # side faces
        for i in range(0, self.numberOfSectors):
            a = index_base_start + i
            b = index_base_start + i + 1
            c = index_top_start + i
            if i == self.numberOfSectors - 1:
                b = index_base_start
            self.createFaceIndexes(LIST_VERTEXINDEX, a, b, c)

            a = index_top_start + i
            b = index_top_start + i + 1
            c = index_base_start + i + 1
            if i == self.numberOfSectors - 1:
                b = index_top_start
                c = index_base_start
            self.createFaceIndexes(LIST_VERTEXINDEX, a, b, c)

        data = {}
        data["vPosition"] = numpy.array(LIST_VERTICES, dtype="float32")
        data["vColor"] = numpy.array(LIST_COLORS, dtype="float32")
        data["vNormal"] = numpy.array(LIST_NORMALS, dtype="float32")

        if phong:
            vertSh = "phongShading_vs"
            fragSh = "phongShading_ps"
            vertFileName = data_.getDataPath(
                "data/shaders/" + vertSh + ".glsl"
            )
            fragFileName = data_.getDataPath(
                "data/shaders/" + fragSh + ".glsl"
            )
        else:
            vertSh = "diffuse_vs"
            fragSh = "diffuse_ps"
            vertFileName = data_.getDataPath(
                "data/shaders/" + vertSh + ".glsl"
            )
            fragFileName = data_.getDataPath(
                "data/shaders/" + fragSh + ".glsl"
            )
        with open(vertFileName) as file:
            VERT = file.read()
        with open(fragFileName) as file:
            FRAG = file.read()

        super(Cylinder, self).__init__(
            vertexShader=VERT,
            fragmentShader=FRAG,
            bufferData=data,
            indexBuffer=numpy.array(LIST_VERTEXINDEX, dtype="int32"),
        )

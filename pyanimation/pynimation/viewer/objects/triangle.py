import numpy
from numpy import ndarray
from .. import VBObject
import pynimation.common.data as data_
from typing import List, Optional
from pynimation.common import RotationTools


class Triangle(VBObject):
    """
    A Triangle in 3D space

    Parameters
    ----------
        pointA : ndarray, optional
            position of the first point, by default numpy.array([0, 0, 0])
        pointB : ndarray, optional
            position of the second point, by default numpy.array([1, 0, 0])
        pointC : ndarray, optional
            position of the third point, by default numpy.array([1, 1, 0])
        colorA : list, optional
            color of the first point, by default [0.5, 0.5, 0.5, 1]
        colorB : list, optional
            color of the second point, by default [0.5, 0.5, 0.5, 1]
        colorC : list, optional
            color of the third point, by default [0.5, 0.5, 0.5, 1]
        normalA : Optional[ndarray], optional
            normal of the first point, by default None
        normalB : Optional[ndarray], optional
            normal of the second point, by default None
        normalC : Optional[ndarray], optional
            normal of the third point, by default None
        phong : bool, optional
            The selected shader, if True phong is selected, otherwise diffuse, by default False

    Attributes
    ----------
        pointA : ndarray, optional
            position of the first point, by default numpy.array([0, 0, 0])
        pointB : ndarray, optional
            position of the second point, by default numpy.array([1, 0, 0])
        pointC : ndarray, optional
            position of the third point, by default numpy.array([1, 1, 0])
        colorA : list, optional
            color of the first point, by default [0.5, 0.5, 0.5, 1]
        colorB : list, optional
            color of the second point, by default [0.5, 0.5, 0.5, 1]
        colorC : list, optional
            color of the third point, by default [0.5, 0.5, 0.5, 1]
        normalA : Optional[ndarray], optional
            normal of the first point, by default None
        normalB : Optional[ndarray], optional
            normal of the second point, by default None
        normalC : Optional[ndarray], optional
            normal of the third point, by default None
        phong : bool, optional
            The selected shader, if True phong is selected, otherwise diffuse, by default False
    """

    def __init__(
        self,
        pointA: ndarray = numpy.array([0, 0, 0]),
        pointB: ndarray = numpy.array([1, 0, 0]),
        pointC: ndarray = numpy.array([1, 1, 0]),
        colorA: List[float] = [1.0, 0.0, 0.0, 0.6],
        colorB: List[float] = [0.0, 1.0, 0.0, 0.6],
        colorC: List[float] = [0.0, 0.0, 1.0, 0.6],
        normalA: Optional[ndarray] = None,
        normalB: Optional[ndarray] = None,
        normalC: Optional[ndarray] = None,
        phong: bool = False,
    ):
        """[summary]

        Parameters
        ----------
        pointA : ndarray, optional
            position of the first point, by default numpy.array([0, 0, 0])
        pointB : ndarray, optional
            position of the second point, by default numpy.array([1, 0, 0])
        pointC : ndarray, optional
            position of the third point, by default numpy.array([1, 1, 0])
        colorA : list, optional
            color of the first point, by default [0.5, 0.5, 0.5, 1]
        colorB : list, optional
            color of the second point, by default [0.5, 0.5, 0.5, 1]
        colorC : list, optional
            color of the third point, by default [0.5, 0.5, 0.5, 1]
        normalA : Optional[ndarray], optional
            normal of the first point, by default None
        normalB : Optional[ndarray], optional
            normal of the second point, by default None
        normalC : Optional[ndarray], optional
            normal of the third point, by default None
        phong : bool, optional
            The selected shader, if True phong is selected, otherwise diffuse, by default False
        """
        LIST_VERTICES: List[List[float]] = []
        LIST_COLORS: List[List[float]] = []
        LIST_NORMALS: List[List[float]] = []
        LIST_VERTEXINDEX: List[int] = []
        LIST_VERTICES.append(pointA.tolist())
        LIST_VERTICES.append(pointB.tolist())
        LIST_VERTICES.append(pointC.tolist())
        LIST_COLORS.append(colorA)
        LIST_COLORS.append(colorB)
        LIST_COLORS.append(colorC)

        # normal computation
        vec1 = pointB - pointA
        vec2 = pointC - pointA
        normalTriangle = numpy.cross(vec1, vec2)
        normalTriangle = RotationTools.normalize(normalTriangle)
        if normalA is None:
            LIST_NORMALS.append(normalTriangle)
        else:
            LIST_NORMALS.append(normalA)
        if normalB is None:
            LIST_NORMALS.append(normalTriangle)
        else:
            LIST_NORMALS.append(normalB)
        if normalC is None:
            LIST_NORMALS.append(normalTriangle)
        else:
            LIST_NORMALS.append(normalC)

        self.createFaceIndexes(
            LIST_VERTEXINDEX,
            0,
            1,
            2,
        )

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

        super(Triangle, self).__init__(
            vertexShader=VERT,
            fragmentShader=FRAG,
            bufferData=data,
            indexBuffer=numpy.array(LIST_VERTEXINDEX, dtype="int32"),
        )

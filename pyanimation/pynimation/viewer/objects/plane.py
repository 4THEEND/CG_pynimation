import numpy
from typing import Dict, List, Optional, Union

from .. import VBObject
from .. import Texture
from pynimation.common import data as data_
from pynimation.viewer import Viewport


class Plane(VBObject):
    """
    A 3D dynamic quad with texture


    Parameters
    ----------
    width: float:
        width of the quad
    height: float:
        height of the quad
    normalDirectionAx: str:
        the base direction of the normal, x, y, z
    color: List[float]:
        the color of the quad
    textureFilename: str:
        the name of the texture file to use
    fromFloorPosition:
        relative position from the floor
    mixParameter:
        the parameter to mix from color to texture color

    Attributes
    ----------
    width: float:
        width of the quad
    height: float:
        height of the quad
    normalDirectionAx: str:
        the base direction of the normal, x, y, z
    color: List[float]:
        the color of the quad
    textureFilename: str:
        the name of the texture file to use
    fromFloorPosition:
        relative position from the floor
    mixParameter:
        the parameter to mix from color to texture color, from 0 only color, to 1 only texture
    """

    def __init__(
        self,
        textureFilename: str,
        width: float = 100,
        height: float = 100,
        fromFloorPosition: int = 0,
        normalDirectionAx: str = "y",
        color: List[float] = [0.5, 0.5, 0.5, 1],
        mixParameter: float = 1.0,
    ) -> None:

        if normalDirectionAx == "x" or normalDirectionAx == "X":
            LIST_VERTICES = [
                [fromFloorPosition, -width, -height],
                [fromFloorPosition, -width, height],
                [fromFloorPosition, width, height],
                [fromFloorPosition, -width, -height],
                [fromFloorPosition, width, height],
                [fromFloorPosition, width, -height],
            ]
        elif normalDirectionAx == "y" or normalDirectionAx == "Y":
            LIST_VERTICES = [
                [-width, fromFloorPosition, -height],
                [-width, fromFloorPosition, height],
                [width, fromFloorPosition, height],
                [-width, fromFloorPosition, -height],
                [width, fromFloorPosition, height],
                [width, fromFloorPosition, -height],
            ]
        elif normalDirectionAx == "z" or normalDirectionAx == "Z":
            LIST_VERTICES = [
                [-width, -height, fromFloorPosition],
                [-width, height, fromFloorPosition],
                [width, height, fromFloorPosition],
                [-width, -height, fromFloorPosition],
                [width, height, fromFloorPosition],
                [width, -height, fromFloorPosition],
            ]
        else:
            print("DIRECTION NOT DEFINED")
            LIST_VERTICES = [
                [-width, fromFloorPosition, -height],
                [-width, fromFloorPosition, height],
                [width, fromFloorPosition, height],
                [-width, fromFloorPosition, -height],
                [width, fromFloorPosition, height],
                [width, fromFloorPosition, -height],
            ]

        LIST_VERTICES_UV = [
            [-width, -height],
            [-width, height],
            [width, height],
            [-width, -height],
            [width, height],
            [width, -height],
        ]

        data = {}
        data["vPosition"] = numpy.array(LIST_VERTICES, dtype="float32")
        data["vTextCoord"] = numpy.array(LIST_VERTICES_UV, dtype="float32")

        vertSh = "quadTextured_vs"
        fragSh = "quadTextured_fs"
        vertFileName = data_.getDataPath("data/shaders/" + vertSh + ".glsl")
        fragFileName = data_.getDataPath("data/shaders/" + fragSh + ".glsl")
        with open(vertFileName) as file:
            VERT = file.read()
        with open(fragFileName) as file:
            FRAG = file.read()

        super(Plane, self).__init__(
            data, None, vertexShader=VERT, fragmentShader=FRAG
        )
        self.colorInId = super(Plane, self).setUndefinedShaderData("colorIn")
        self.mixParameterId = super(Plane, self).setUndefinedShaderData(
            "mixParameter"
        )

        self.loadTexture(textureFilename)
        self.setColor(color)
        self.setMixParameter(mixParameter)

    def setColor(self, color: List[Union[float, int]]) -> None:
        """
        Set the main color of the texture

        Parameters
        ----------
        color : List[Union[float, int]]
            the desired color with alpha
        """
        self.color = color

    def setMixParameter(self, mixParameter: float) -> None:
        """
        Set the mix parameter between color and texture

        Parameters
        ----------
        mixParameter : float
            the float value from 0 only color, to 1 only texture
        """
        self.mixParameter = mixParameter

    def loadTexture(self, textureFilename: str) -> None:
        """
        Load a desire texture

        Parameters
        ----------
        textureFilename : str
            The texture name
        """
        data_folder = "data/textures/"
        if data_folder in textureFilename:
            textureFilepath = textureFilename
        else:
            textureFilepath = data_.getDataPath(data_folder + textureFilename)
        self.texture: Texture = Texture(textureFilepath)
        self.textureName = "basicTexture"
        self.textureLocation = 0

    def display(
        self,
        uniformData: Optional[Dict[str, numpy.ndarray]] = None,
    ) -> None:
        if uniformData is None:
            uniformData = {}
        self.uniformData = {
            **uniformData,
            **self.uniformData,
            **Viewport().cameraData,
        }
        # if "model" in self.uniformData:
        #     self.uniformData["model"] = (
        #         self.globalTransform * self.uniformData["model"]
        #     )
        # else:
        self.uniformData["model"] = self.globalTransform.matrix
        color = self.color
        self.linkShaderData(self.uniformData)
        self.linkShaderTextureData(self.texture, "basicTexture", 0)
        self.automaticallyLinkShaderUniforms(self.colorInId, color)
        self.automaticallyLinkShaderUniforms(
            self.mixParameterId, self.mixParameter
        )
        self.linkShaderUniforms(self.uniformData)
        self.drawBuffers()

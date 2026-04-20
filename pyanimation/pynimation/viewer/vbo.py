import numpy
from OpenGL import GL
from OpenGL.GL.shaders import ShaderProgram, compileProgram, compileShader
import pygame as pg

from pynimation.common import Transform
from pynimation.common import RotationTools
from pynimation.common import defaults
from pynimation.common import data as data_
from .light import LightManager
from .texture import Texture
from .scene import SceneNode
from .displayable import Displayable
from .viewport import Viewport
from numpy import ndarray
from typing import Dict, List, Optional, Tuple


class VBObject(SceneNode, Displayable):
    """
    Encapsulates an OpenGL vertex buffer object
    """

    def __init__(
        self,
        bufferData: Dict[str, ndarray],
        indexBuffer: Optional[ndarray] = None,
        vertexShader: str = "",
        fragmentShader: str = "",
    ) -> None:

        super().__init__("")
        self.data = bufferData
        self.indexBuffer = indexBuffer
        self.uniformData: Dict[str, numpy.ndarray] = {}
        self.texture: Optional[Texture] = None

        if not pg.get_init():
            # FIXME : if this gets run before the user creates a viewport with
            # a custom size, the custom size will be ignored
            Viewport()  # make sure the context is initialized

        if len(vertexShader) == 0:
            vshader_fn = data_.getDataPath(defaults.VERTEX_SHADER)
            with open(vshader_fn) as file:
                vertexShader = file.read()
        if len(fragmentShader) == 0:
            fshader_fn = data_.getDataPath(defaults.FRAGMENT_SHADER)
            with open(fshader_fn) as file:
                fragmentShader = file.read()

        shader = compileProgram(
            compileShader(vertexShader, GL.GL_VERTEX_SHADER),
            compileShader(fragmentShader, GL.GL_FRAGMENT_SHADER),
        )
        self.setShaderData(shader)

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        for param in self.data:

            paramLocation = GL.glGetAttribLocation(self.shader, param)
            if paramLocation != -1:
                vbo = GL.glGenBuffers(1)
                GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)

                arraySize = self.data[param].size * self.data[param].itemsize
                GL.glBufferData(
                    GL.GL_ARRAY_BUFFER,
                    arraySize,
                    self.data[param],
                    GL.GL_STATIC_DRAW,
                )

                GL.glEnableVertexAttribArray(paramLocation)
                GL.glVertexAttribPointer(
                    paramLocation,
                    self.data[param][0].size,
                    GL.GL_FLOAT,
                    False,
                    0,
                    None,
                )

                self.numberVertices = len(self.data[param])

        self.ibo = None
        if self.indexBuffer is not None:
            self.ibo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
            arraySize = self.indexBuffer.size * self.indexBuffer.itemsize
            self.nbIndices = self.indexBuffer.size
            GL.glBufferData(
                GL.GL_ELEMENT_ARRAY_BUFFER,
                arraySize,
                indexBuffer,
                GL.GL_STATIC_DRAW,
            )
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        self.diffuseCoefficient = numpy.array([1, 1, 1], dtype="float32")
        self.ambientCoefficient = numpy.array([1, 1, 1], dtype="float32")
        self.specularCoefficient = numpy.array(
            [0.2, 0.2, 0.2, 3], dtype="float32"
        )

    def setShaderData(self, shaderID: ShaderProgram) -> None:
        """

        Parameters
        ----------
        shaderID: ShaderProgram :


        Returns
        -------

        """
        self.shader = shaderID
        self.locLightdir = GL.glGetUniformLocation(
            self.shader, "lightDirection"
        )
        self.locLightspec = GL.glGetUniformLocation(
            self.shader, "lightSpecular"
        )
        self.locLightdiffuse = GL.glGetUniformLocation(
            self.shader, "lightDiffuse"
        )
        self.locLightambient = GL.glGetUniformLocation(
            self.shader, "lightAmbient"
        )
        self.locKs = GL.glGetUniformLocation(self.shader, "Ks")
        self.locKd = GL.glGetUniformLocation(self.shader, "Kd")
        self.locKa = GL.glGetUniformLocation(self.shader, "Ka")
        self.locSkinningmatrices = GL.glGetUniformLocation(
            self.shader, "SkinningMatrices"
        )

    def setUndefinedShaderData(self, name):
        shader_data_id = GL.glGetUniformLocation(self.shader, name)
        return shader_data_id

    def display(
        self,
        uniformData: Optional[Dict[str, numpy.ndarray]] = None,
    ) -> None:
        """

        Parameters
        ----------
        uniformData: Optional[Dict[str :

        numpy.ndarray]] :
             (Default value = None)

        Returns
        -------

        """
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
        self.linkShaderData(self.uniformData)
        if self.texture is not None:
            self.linkShaderTextureData(self.texture)
        self.linkShaderUniforms(self.uniformData)
        self.drawBuffers()

    def linkShaderData(self, uniformData: Dict[str, numpy.ndarray]) -> None:
        """

        Parameters
        ----------
        uniformData: Dict[str :

        numpy.ndarray] :


        Returns
        -------

        """
        GL.glUseProgram(self.shader)

        for u in uniformData:
            uniformLoc = GL.glGetUniformLocation(self.shader, u)
            if uniformLoc != -1:
                buff = uniformData[u]

                if isinstance(buff, Transform):
                    buff = buff.matrix

                if isinstance(buff, int):
                    GL.glUniform1i(uniformLoc, buff)
                elif isinstance(buff, float):
                    GL.glUniform1f(uniformLoc, buff)
                elif isinstance(buff, numpy.ndarray) or isinstance(
                    buff, numpy.matrix
                ):
                    nbLines = len(buff)
                    nbColumns = buff[0].size
                    if nbLines == nbColumns:
                        if nbLines == 2:
                            GL.glUniformMatrix2fv(uniformLoc, 1, True, buff)
                        if nbLines == 3:
                            GL.glUniformMatrix3fv(uniformLoc, 1, True, buff)
                        if nbLines == 4:
                            GL.glUniformMatrix4fv(uniformLoc, 1, True, buff)
                elif isinstance(buff, list):
                    nbElements = len(buff)
                    nbLines = len(buff[0])
                    nbColumns = len(buff[0][0])
                    if nbLines == nbColumns:
                        if nbLines == 2:
                            GL.glUniformMatrix2fv(
                                uniformLoc, nbElements, True, buff
                            )
                        if nbLines == 3:
                            GL.glUniformMatrix3fv(
                                uniformLoc, nbElements, True, buff
                            )
                        if nbLines == 4:
                            GL.glUniformMatrix4fv(
                                uniformLoc, nbElements, True, buff
                            )
                else:
                    raise ValueError("Uniform Data Unsupported at the moment")

    def linkShaderTextureData(
        self,
        texture: Texture,
        textureName: str = "basicTexture",
        textureLocation: int = 0,
    ) -> None:
        """

        Parameters
        ----------
        texture: Texture :


        Returns
        -------

        """
        if not hasattr(self, "textureName"):
            self.textureName = textureName
        if not hasattr(self, "textureLocation"):
            self.textureLocation = textureLocation
        texLoc = GL.glGetUniformLocation(self.shader, self.textureName)
        if texLoc != -1:
            GL.glUniform1i(texLoc, self.textureLocation)
            texture.use(self.textureLocation)

    def linkShaderUniforms(
        self, uniformData: Dict[str, numpy.ndarray]
    ) -> None:
        """

        Parameters
        ----------
        uniformData: Dict[str :

        numpy.ndarray] :


        Returns
        -------

        """
        light = LightManager(0, 0)  # get the singleton, (0,0) makes mypy happy

        if self.locLightdir != -1:
            GL.glUniform3fv(self.locLightdir, 1, light.lightDirection)
        if self.locLightspec != -1:
            GL.glUniform3fv(self.locLightspec, 1, light.lightSpecular)
        if self.locLightdiffuse != -1:
            GL.glUniform3fv(self.locLightdiffuse, 1, light.lightDiffuse)
        if self.locLightambient != -1:
            GL.glUniform3fv(self.locLightambient, 1, light.lightAmbient)

        if self.locKs != -1:
            GL.glUniform4fv(self.locKs, 1, self.specularCoefficient)
        if self.locKd != -1:
            GL.glUniform3fv(self.locKd, 1, self.diffuseCoefficient)
        if self.locKa != -1:
            GL.glUniform3fv(self.locKa, 1, self.ambientCoefficient)

        if (
            self.locSkinningmatrices != -1
            and "SkinningMatrices" in uniformData.keys()
        ):
            m = uniformData["SkinningMatrices"]
            GL.glUniformMatrix4fv(self.locSkinningmatrices, len(m), False, m)

    def drawBuffers(self) -> None:
        """ """
        GL.glBindVertexArray(self.vao)
        if self.ibo is None:
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.numberVertices)
        else:
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ibo)
            GL.glDrawElements(
                GL.GL_TRIANGLES, self.nbIndices, GL.GL_UNSIGNED_INT, None
            )
        GL.glUseProgram(0)

    def computeNormals(self, vertices: numpy.ndarray) -> numpy.ndarray:
        """

        Parameters
        ----------
        vertices: numpy.ndarray :


        Returns
        -------

        """
        n = [0, 0, 0]
        nbVertices = len(vertices)
        normals = [n] * nbVertices
        for i in range(0, nbVertices, 3):
            a = numpy.array(vertices[i + 1]) - numpy.array(vertices[i])
            b = numpy.array(vertices[i + 2]) - numpy.array(vertices[i])
            n = numpy.cross(a, b).tolist()
            normals[i] = normals[i + 1] = normals[
                i + 2
            ] = RotationTools.normalize(n)
        return normals

    def createFaceIndexes(
        self,
        vertexIndexData: List[int],
        a: int,
        b: int,
        c: int,
        d: Optional[int] = None,
    ) -> None:
        """

        Parameters
        ----------
        vertexIndexData: List[int] :

        a: int :

        b: int :

        c: int :

        d: Optional[int] :
             (Default value = None)

        Returns
        -------

        """
        vertexIndexData.append(a)
        vertexIndexData.append(b)
        vertexIndexData.append(c)
        if d is not None:
            vertexIndexData.append(a)
            vertexIndexData.append(c)
            vertexIndexData.append(d)

    def automaticallyLinkShaderUniforms(self, location_id, *values):
        """
        link automatically the shader uniform base on the type

        Parameters
        ----------
        location_id : GLint
            The already generated location using 'glGetUniformLocation'

        *values:
            The parameter to pass as uniform:
            [float, int, bool, list, ndarray]
        """
        if len(values) == 1:
            value = values[0]
            if isinstance(value, int):
                GL.glUniform1i(location_id, value)
            elif isinstance(value, float):
                GL.glUniform1f(location_id, value)
            elif isinstance(value, bool):
                GL.glUniform1i(location_id, value)

            elif isinstance(values[0], list):
                value = values[0]
                if len(value) == 1:
                    if isinstance(value[0], int) or isinstance(value[0], bool):
                        GL.glUniform1iv(location_id, 1, value)
                    elif isinstance(value[0], float):
                        GL.glUniform1fv(location_id, 1, value)
                elif len(value) == 2:
                    if isinstance(value[0], int) or isinstance(value[0], bool):
                        GL.glUniform2iv(location_id, 1, value)
                    elif isinstance(value[0], float):
                        GL.glUniform2fv(location_id, 1, value)
                elif len(value) == 3:
                    if isinstance(value[0], int) or isinstance(value[0], bool):
                        GL.glUniform3iv(location_id, 1, value)
                    elif isinstance(value[0], float):
                        GL.glUniform3fv(location_id, 1, value)
                elif len(value) == 4:
                    if isinstance(value[0], int) or isinstance(value[0], bool):
                        GL.glUniform4iv(location_id, 1, value)
                    elif isinstance(value[0], float):
                        GL.glUniform4fv(location_id, 1, value)

            elif isinstance(value, ndarray):
                shape: Tuple = value.shape
                if len(shape) == 1:
                    if len(shape[0]) == 1:
                        if (
                            value.dtype == numpy.int
                            or value.dtype == numpy.bool
                        ):
                            GL.glUniform1iv(location_id, 1, value.tolist())
                        elif value.dtype == numpy.float:
                            GL.glUniform1fv(location_id, 1, value.tolist())
                    elif len(shape[0]) == 2:
                        if (
                            value.dtype == numpy.int
                            or value.dtype == numpy.bool
                        ):
                            GL.glUniform2iv(location_id, 1, value.tolist())
                        elif value.dtype == numpy.float:
                            GL.glUniform2fv(location_id, 1, value.tolist())
                    elif len(shape[0]) == 3:
                        if (
                            value.dtype == numpy.int
                            or value.dtype == numpy.bool
                        ):
                            GL.glUniform3iv(location_id, 1, value.tolist())
                        elif value.dtype == numpy.float:
                            GL.glUniform3fv(location_id, 1, value.tolist())
                    elif len(shape[0]) == 4:
                        if (
                            value.dtype == numpy.int
                            or value.dtype == numpy.bool
                        ):
                            GL.glUniform4iv(location_id, 1, value.tolist())
                        elif value.dtype == numpy.float:
                            GL.glUniform4fv(location_id, 1, value.tolist())

                if len(shape) == 2:

                    if len(shape[0]) == 1:  # vector
                        if len(shape[1]) == 1:  # 1x1
                            if (
                                value.dtype == numpy.int
                                or value.dtype == numpy.bool
                            ):
                                GL.glUniform1iv(
                                    location_id, 1, value.tolist()[0]
                                )
                            elif value.dtype == numpy.float:
                                GL.glUniform1fv(
                                    location_id, 1, value.tolist()[0]
                                )
                        elif len(shape[1]) == 2:  # 1x2
                            if (
                                value.dtype == numpy.int
                                or value.dtype == numpy.bool
                            ):
                                GL.glUniform2iv(
                                    location_id, 1, value.tolist()[0]
                                )
                            elif value.dtype == numpy.float:
                                GL.glUniform2fv(
                                    location_id, 1, value.tolist()[0]
                                )
                        elif len(shape[1]) == 3:  # 1x3
                            if (
                                value.dtype == numpy.int
                                or value.dtype == numpy.bool
                            ):
                                GL.glUniform3iv(
                                    location_id, 1, value.tolist()[0]
                                )
                            elif value.dtype == numpy.float:
                                GL.glUniform3fv(
                                    location_id, 1, value.tolist()[0]
                                )
                        elif len(shape[1]) == 4:  # 1x4
                            if (
                                value.dtype == numpy.int
                                or value.dtype == numpy.bool
                            ):
                                GL.glUniform4iv(
                                    location_id, 1, value.tolist()[0]
                                )
                            elif value.dtype == numpy.float:
                                GL.glUniform4fv(
                                    location_id, 1, value.tolist()[0]
                                )

                    elif len(shape[0]) == 2:
                        if len(shape[1]) == 1:  # 2x1 vector
                            value = value.transpose()
                            if (
                                value.dtype == numpy.int
                                or value.dtype == numpy.bool
                            ):
                                GL.glUniform1iv(
                                    location_id, 1, value.tolist()[0]
                                )
                            elif value.dtype == numpy.float:
                                GL.glUniform1fv(
                                    location_id, 1, value.tolist()[0]
                                )
                        elif len(shape[1]) == 2:  # 2x2
                            GL.glUniformMatrix2fv(
                                location_id, 1, value.flatten()
                            )
                        elif len(shape[1]) == 3:  # 2x3
                            GL.glUniformMatrix2x3fv(
                                location_id, 1, value.flatten()
                            )
                        elif len(shape[1]) == 4:  # 2x4
                            GL.glUniformMatrix2x4fv(
                                location_id, 1, value.flatten()
                            )

                    elif len(shape[0]) == 3:
                        if len(shape[1]) == 1:  # 3x1 vector
                            value = value.transpose()
                            if (
                                value.dtype == numpy.int
                                or value.dtype == numpy.bool
                            ):
                                GL.glUniform1iv(
                                    location_id, 1, value.tolist()[0]
                                )
                            elif value.dtype == numpy.float:
                                GL.glUniform1fv(
                                    location_id, 1, value.tolist()[0]
                                )
                        elif len(shape[1]) == 2:  # 3x2
                            GL.glUniformMatrix3x2fv(
                                location_id, 1, value.flatten()
                            )
                        elif len(shape[1]) == 3:  # 3x3
                            GL.glUniformMatrix3fv(
                                location_id, 1, value.flatten()
                            )
                        elif len(shape[1]) == 4:  # 3x4
                            GL.glUniformMatrix3x4fv(
                                location_id, 1, value.flatten()
                            )

                    elif len(shape[0]) == 4:
                        if len(shape[1]) == 1:  # 4x1 vector
                            value = value.transpose()
                            if (
                                value.dtype == numpy.int
                                or value.dtype == numpy.bool
                            ):
                                GL.glUniform1iv(
                                    location_id, 1, value.tolist()[0]
                                )
                            elif value.dtype == numpy.float:
                                GL.glUniform1fv(
                                    location_id, 1, value.tolist()[0]
                                )
                        elif len(shape[1]) == 2:  # 4x2
                            GL.glUniformMatrix4x2fv(
                                location_id, 1, value.flatten()
                            )
                        elif len(shape[1]) == 3:  # 4x3
                            GL.glUniformMatrix4x3fv(
                                location_id, 1, value.flatten()
                            )
                        elif len(shape[1]) == 4:  # 4x4
                            GL.glUniformMatrix4fv(
                                location_id, 1, value.flatten()
                            )

        elif len(values) == 2:
            value_0 = values[0]
            value_1 = values[1]
            if isinstance(value_0, int) and isinstance(value_1, int):
                GL.glUniform2i(location_id, value_0, value_1)
            elif isinstance(value_0, float) or isinstance(value_1, float):
                GL.glUniform2f(location_id, value_0, value_1)

        elif len(values) == 3:
            value_0 = values[0]
            value_1 = values[1]
            value_2 = values[2]
            if (
                isinstance(value_0, int)
                and isinstance(value_1, int)
                and isinstance(value_2, int)
            ):
                GL.glUniform3i(location_id, value_0, value_1, value_2)
            elif (
                isinstance(value_0, float)
                or isinstance(value_1, float)
                or isinstance(value_2, float)
            ):
                GL.glUniform3f(location_id, value_0, value_1, value_2)

        elif len(values) == 4:
            value_0 = values[0]
            value_1 = values[1]
            value_2 = values[2]
            value_3 = values[3]
            if (
                isinstance(value_0, int)
                and isinstance(value_1, int)
                and isinstance(value_2, int)
                and isinstance(value_3, int)
            ):
                GL.glUniform4i(location_id, value_0, value_1, value_2, value_3)
            elif (
                isinstance(value_0, float)
                or isinstance(value_1, float)
                or isinstance(value_2, float)
                or isinstance(value_3, float)
            ):
                GL.glUniform4f(location_id, value_0, value_1, value_2, value_3)

        else:
            print("VBObject automaticallyLinkShaderUniforms: undefined input")

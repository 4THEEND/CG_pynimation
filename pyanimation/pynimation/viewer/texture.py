from OpenGL import GL
import pygame as pg


class Texture:
    """
    Encapsulate an OpenGL texture object

    Parameters
    ----------
    filename: str
        path to the texture image

    Parameters
    ----------
    image: pg.image
        pygame image object of the texture image
    imageData: bytes
        RGBA buffer of the texture image
    texID: int
        OpenGL internal texture ID
    """

    def __init__(self, filename: str) -> None:
        self.image = pg.image.load(filename).convert_alpha()
        self.imageData = pg.image.tostring(self.image, "RGBA", True)

        self.texID = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texID)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            self.image.get_width(),
            self.image.get_height(),
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            self.imageData,
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT
        )
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def use(self, textureUnit: int) -> None:
        """
        Use this texture as OpenGL :attr:`textureUnit`

        Parameters
        ----------
        textureUnit:
        """
        GL.glActiveTexture(GL.GL_TEXTURE0 + textureUnit)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texID)

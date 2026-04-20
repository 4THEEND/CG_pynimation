import sys
import os
from typing import Optional, Tuple

from OpenGL import GL
import pygame as pg
import numpy
from PIL import Image

from pynimation.common import _Singleton
from pynimation.common import defaults
from .player import Player
from .camera import Camera


class Viewport(metaclass=_Singleton):
    """
    Class responsible for initializing and displaying the window

    Parameters
    ----------
    width: int:
        width of the window in pixels
    height: int:
        height of the window in pixels
    camera: Camera:
        camera through which the scene will be displayed
    fs: boolean:
        whether to set the window to full screen
    name: str:
        name displayed as the window title

    Attributes
    ----------
    width: int:
        width of the window in pixels
    height: int:
        height of the window in pixels
    camera: Camera:
        camera through which the scene will be displayed
    fullscreen: boolean:
        whether to set the window to full screen
    name: str:
        name displayed as the window title
    """

    def __init__(
        self,
        width: int = defaults.VIEWPORT_WIDTH,
        height: int = defaults.VIEWPORT_HEIGHT,
        camera: Optional[Camera] = None,
        name: str = defaults.VIEWPORT_NAME,
        fs: bool = False,
    ) -> None:
        self.name = name
        self.fullscreen = fs
        self.width = width
        self.height = height
        self.initialize()

        if camera is None:
            camera = Camera(self.width, self.height)
        self.mainCamera: Camera = camera
        self.isCameraRotating = False
        self._cameraTranslationalDirection = numpy.array([0, 0, 0])
        self.cameraTranslationSpeed = 5.0
        self.cameraRotationSpeed = 300.0

        self.lastMousePosition: Tuple[int, int] = (0, 0)

        self.isrecording = False
        self.recordingFramerate = 30
        self.player = Player()
        self.cameraData = {
            "proj": numpy.identity(4),
            "view": numpy.identity(4),
        }

    def startRecording(
        self,
        folder: Optional[str] = None,
        filename: Optional[str] = None,
        fps: int = 30,
    ) -> None:
        """
        Save a capture of the viewport at each frame, to :attr:`folder`, with
        prefix :attr:`filename`, record at :attr:`fps` frames per second

        Parameters
        ----------
        folder:
            folder in which to save the captures
        filename:
            prefix for the image files
        fps:
            framerate at which to record

        Note
        ----
        Capturing in will significantly slow down the render loop. Eventhough
        it appears slower, a constant framerate will be enforced and the
        animation will appear fluid when the captured images are put together.

        Note
        ----
        A video can be created from the set of captured images using
        :code:`ffmpeg`. `This page
        <https://www.ffmpeg.org/faq.html#How-do-I-encode-single-pictures-into-movies_003f>`_ contains examples
        """
        self.isrecording = True
        self.recordingFramerate = fps
        self.player.framerate = self.recordingFramerate
        self.player.accurate = True

        self.filenamebase = filename or "movie"
        self.filenameId = 0
        folderbase = folder or "./data/Screenshots/"
        folderbase += self.filenamebase
        self.folderRecording = folderbase
        id = 0
        while os.path.isdir(self.folderRecording):
            self.folderRecording = folderbase + "_" + str(id).zfill(3)
            id += 1
        os.mkdir(self.folderRecording)
        self.filenamebase += "_" + str(id - 1).zfill(3)

    def stopRecording(self) -> None:
        """
        Stop a recording
        """
        self.isrecording = False
        self.player.accurate = False
        self.player.framerate = 0

    def startStopRecording(self) -> None:
        """
        Toggle recording on and off
        """
        if self.isrecording:
            self.stopRecording()
        else:
            self.startRecording()

    def setMainCamera(self, camera: Camera) -> None:
        """
        Set main camera to :attr:`camera`

        Parameters
        ----------
        camera:
            camera to be set as main

        """
        self.mainCamera = camera

    def initialize(self) -> None:
        """
        Intialize the window, and the OpenGL context

        Note
        ----
        Must be called before any :class:`~pynimation.viewer.vbo.VBObject` is
        created, and any shader is compiled
        """
        if not pg.get_init():
            pg.init()
        pg.display.set_caption(self.name)
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        SCREEN = pg.display.set_mode(
            (self.width, self.height), pg.HWSURFACE | pg.OPENGL | pg.DOUBLEBUF
        )
        SCREEN.__hash__()  # stop complaining about variable not used
        self.reshape(self.width, self.height)

        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)

    def display(self) -> None:
        """
        Clear the viewport and display the next frame
        """
        GL.glClearColor(1, 1, 1, 1)
        # GL.glClearDepth(0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def reshape(self, width: int, height: int) -> None:
        """
        Change the size of the window

        Parameters
        ----------
        width:
            new width of the window

        height:
            new height of the window

        """
        GL.glViewport(0, 0, width, height)

    def updateCamera(self) -> None:
        """
        Update the view and projection matrices of the camera
        """
        trans = (
            self._cameraTranslationalDirection
            * self.cameraTranslationSpeed
            * self.player.deltaTime
        )
        if numpy.linalg.norm(trans):
            self.mainCamera.translate(trans[0], trans[1], trans[2])
        self.cameraData = {
            "proj": self.mainCamera.projectionMatrix.matrix,
            "view": numpy.linalg.inv(self.mainCamera.viewMatrix.matrix),
        }

    def _createUniqueScreenshot(
        self,
        folderName: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> None:
        folder = folderName or "./data/Screenshots/"
        filenamebase = filename or "screenshot"
        id = 0
        while os.path.isfile(folder + filenamebase + "_" + str(id) + ".png"):
            id += 1
        self.screenshot(folder + filenamebase + "_" + str(id) + ".png")
        # MISSING DIRECTORY CREATION IF DOES NOT EXIST

    def screenshot(self, filename: str) -> None:
        """
        Capture screenshot

        Parameters
        ----------
        filename:
            path of the captured image
        """
        buffer = (GL.GLubyte * (3 * self.width * self.width))(0)
        GL.glReadPixels(
            0,
            0,
            self.width,
            self.height,
            GL.GL_RGB,
            GL.GL_UNSIGNED_BYTE,
            buffer,
        )

        # Use PIL to convert raw RGB buffer and flip the right way up
        image = Image.frombytes("RGB", (self.width, self.height), buffer)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save(filename)

    def handleRecording(self) -> None:
        """
        Should be called at the end of the render loop to capture the frame
        """
        if self.isrecording:
            self.screenshot(
                self.folderRecording
                + "/"
                + self.filenamebase
                + "_"
                + str(self.filenameId).zfill(4)
                + ".png"
            )
            self.filenameId += 1

    def quit(self) -> None:
        """
        Exit the viewer
        """
        pg.quit()
        sys.exit(0)

    def setCameraTranslationalDirection(
        self, axis: int, direction: int
    ) -> None:
        """
        Set the translation direction of the :attr:`mainCamera` along :attr:`axis` in :attr:`direction`
        This information will be used by
        :func:`~pynimation.viewer.viewport.Viewport.updateCamera` to move the
        camera according to :attr:`cameraTranslationSpeed`

        Parameters
        ----------
        axis:
            axis to move the camera along
        direction:
            direction to move the camera in
        """

        self._cameraTranslationalDirection[axis] = direction

    def setCameraIsRotating(self, isRotating: bool) -> None:
        """
        Set wether the :attr:`mainCamera` is rotating according to mouse motion
        This information will be used by
        :func:`~pynimation.viewer.viewport.Viewport.updateCamera` to rotate the
        camera according to :attr:`cameraRotationSpeed` when the mouse moves

        Parameters
        ----------
        isRotating:
            wether the :attr:`mainCamera` should rotate when the mouse moves
        """
        self.isCameraRotating = isRotating

    def rotateCameraWithMouse(
        self, event: pg.event.Event = pg.event.Event(pg.KEYUP)
    ) -> None:
        if self.isCameraRotating:
            self.mainCamera.rotateYaw(
                event.rel[0] * self.cameraRotationSpeed / self.width
            )
            self.mainCamera.rotatePitch(
                event.rel[1] * self.cameraRotationSpeed / self.height
            )

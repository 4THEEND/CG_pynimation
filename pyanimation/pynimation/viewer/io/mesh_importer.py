import abc
from typing import List, TYPE_CHECKING, Optional
from pynimation.io.common import _ioFactory
from pynimation.io.common import _getExtension
from pynimation.io.importer import Importer
from pynimation.viewer import Character


if TYPE_CHECKING:
    from pynimation.viewer import SceneNode

# FIXME: all io modules need to be loaded for the introspection to work
from . import *  # noqa: F401,F403


class MeshImporter(abc.ABC):
    """
    Base mesh importer class. Subclasses each handle a particular
    mesh file format
    """

    @abc.abstractmethod
    def loadMeshes(self, filename: str) -> List["SceneNode"]:
        """
        Load meshes from :attr:`filename`

        Parameters
        ----------
        filename:
            file to load meshes from

        Returns
        -------
        List[SceneNode]
            meshes loaded from :attr:`filename`
        """
        pass

    @property
    @abc.abstractmethod
    def extension(self) -> str:
        """
        Property that subclasses must set to the file extension they will be
        instantiated for
        """
        raise NotImplementedError


def loadMeshes(filename: str) -> List["SceneNode"]:
    """
    Generic mesh import method
    Loads meshes from :attr:`filename`
    The format of the imported file will be determined by the extension of
    :attr:`filename`


    Parameters
    ----------
    filename:
        path of the file to meshes from

    Returns
    -------
    List[SceneNode]
        meshes loaded from :attr:`filename`
    """
    mesh_importer = _ioFactory(MeshImporter, _getExtension(filename))
    meshes = mesh_importer.loadMeshes(filename)
    return meshes


def loadCharacters(
    filename: str, modelFilename: Optional[str] = None
) -> List["Character"]:
    """
    Generic character import method
    Loads animations and meshes from :attr:`filename` or animations from
    :attr:`filename` and meshes from :attr:`modelFilename` if the second is
    provided
    If no meshes are found in :attr:`filename` and :attr:`modelFilename` is not
    provided, a :class:`~pynimation.viewer.stickfigure.StickFigure` mesh will
    be created and used as a mesh for the character

    Parameters
    ----------
    filename:
        file to load animations and meshes from

    modelFilename:
        different file to load meshes from, will have priority over meshes from
        :attr:`filename` if provided

    Returns
    -------
    List[Character]
        characters loaded from :attr:`filename` and :attr:`modelFilename`
    """
    if modelFilename is None:
        modelFilename = ""
    importer = _ioFactory(Importer, _getExtension(filename))
    animations = importer.load(filename)
    meshes = []
    if len(modelFilename) > 0:
        # modelFilename given, load meshes from it
        mesh_importer = _ioFactory(MeshImporter, _getExtension(modelFilename))
        meshes = mesh_importer.loadMeshes(modelFilename)
    else:
        # modelFilename not given, try to load meshes from filename
        try:
            mesh_importer = _ioFactory(MeshImporter, _getExtension(filename))
            meshes = mesh_importer.loadMeshes(filename)
        except NotImplementedError:
            # No MeshImporter for filename, create StickFigure mesh
            pass
    characters = []
    for animation in animations:
        characters.append(Character(animation, meshes))

    return characters

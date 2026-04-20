import abc
import functools
from typing import List, TYPE_CHECKING
from .common import _ioFactory
from .common import _getExtension

# FIXME: all io modules need to be loaded for the introspection to work
from . import *  # noqa: F401,F403

if TYPE_CHECKING:
    from pynimation.anim import Animation


class Importer(abc.ABC):
    """
    Base animation importer class. Subclasses each handle a particular
    animation file format
    """

    @abc.abstractmethod
    def load(self, filename: str) -> List["Animation"]:
        """
        Abstract animation load method.
        Overriding methods must return :class:`~pynimation.anim.Animation`
        objects obtained from :attr:`filename`

        Parameters
        ----------
        filename:
            file to import animations from

        Returns
        -------
        List[Animation]
            animations present in :attr:`filename`

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


_importerFactory = functools.partial(_ioFactory, Importer)


def load(filename: str) -> List["Animation"]:
    """
    Generic animation import method.
    Loads animations from :attr:`filename`.
    The format of the imported file will be determined by the extension of
    :attr:`filename`


    Parameters
    ----------
    filename:
        path of the file to load animations from

    Returns
    -------
    List[Animation]
        animations loaded from :attr:`filename`
    """
    extension = _getExtension(filename)
    importer = _ioFactory(Importer, extension)
    return importer.load(filename)

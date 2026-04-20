import abc
import functools

from typing import TYPE_CHECKING
from .common import _ioFactory
from .common import _getExtension

if TYPE_CHECKING:
    from pynimation.anim import Animation

# FIXME: all io modules need to be loaded for the introspection to work
from . import *  # noqa: F401,F403


class Exporter(abc.ABC):
    """
    Base animation exporter class. Subclasses each handle a particular
    animation file format
    """

    @abc.abstractmethod
    def save(self, animation: "Animation", filename: str) -> None:
        """
        Abstract save method
        Overidding methods should save :attr:`animation` to :attr:`filename`

        Parameters
        ----------
        animation:
            animation to save

        filename:
            path to save the animation to
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


_exporterFactory = functools.partial(_ioFactory, Exporter)


def save(animation: "Animation", filename: str) -> None:
    """
    Generic animation export method.
    Saves :attr:`animation` to :attr:`filename`.
    The format of the saved file will be determined by the extension of
    :attr:`filename`


    Parameters
    ----------
    animation:
        animation to save

    filename:
        path of the file to save the animation to
    """
    extension = _getExtension(filename)
    exporter = _ioFactory(Exporter, extension)
    exporter.save(animation, filename)

import abc

from pynimation.anim import Frame


class Animatable(abc.ABC):
    """
    Base class for animatable objects
    """

    @abc.abstractmethod
    def animate(self, frame: Frame) -> None:
        """
        Animate this object with the transforms from :attr:`frame`

        Parameters
        ----------
        frame:
            frame to animate this object with
        """
        pass

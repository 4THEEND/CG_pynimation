import abc


class Animated(abc.ABC):
    """
    Base class for animated objects
    """

    @abc.abstractmethod
    def animate(self) -> None:
        pass

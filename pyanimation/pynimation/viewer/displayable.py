import abc
from typing import Dict
import numpy


class Displayable(abc.ABC):
    """
    Base class for displayable objects
    """

    @abc.abstractmethod
    def display(self, uniformData: Dict[str, numpy.ndarray] = {}) -> None:
        pass

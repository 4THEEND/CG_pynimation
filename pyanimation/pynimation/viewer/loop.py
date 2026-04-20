import abc

from pynimation.viewer import Viewer


class CallableLoop(abc.ABC):
    """
    Base class for callable loop
    """

    def __init__(self, viewer: "Viewer", priority: int = 0) -> None:
        self.setPriority(priority)
        viewer.addCallback(
            self.beforeDisplay,
            Viewer.CallbackTime.BEFORE_DISPLAY,
            self.priority,
        )
        viewer.addCallback(
            self.afterDisplay,
            Viewer.CallbackTime.AFTER_DISPLAY,
            self.priority,
        )

    def getPriority(self) -> int:
        return self.priority

    def setPriority(self, priority: int) -> None:
        newPriority: int = priority
        if priority <= 0:
            newPriority = 0
        elif priority >= 100:
            newPriority = 100
        self.priority = newPriority

    @abc.abstractmethod
    def beforeDisplay(self) -> None:
        pass

    @abc.abstractmethod
    def afterDisplay(self) -> None:
        pass

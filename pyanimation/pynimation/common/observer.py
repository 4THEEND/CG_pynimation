from typing import List


class _Observable:
    """
    Observer pattern implementation
    """

    def __init__(self):
        self._observers: List[_Observer] = []

    def registerObserver(self, observer: "_Observer"):
        self._observers.append(observer)

    def unregisterObserver(self, observer: "_Observer"):
        self._observers.remove(observer)

    def notifyObservers(self, *args, **kwargs):
        for observer in self._observers:
            observer.notify(self)


class _Observer:
    """
    Observer pattern implementation
    """

    def notify(self, observable: _Observable, *args, **kwargs):
        pass

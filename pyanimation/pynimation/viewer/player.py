import pygame as pg
from pynimation.common import _Singleton


class Player(metaclass=_Singleton):
    """
    Singleton class managing time
    """

    def __init__(self, framerate: int = 0):
        self.clock = pg.time.Clock()
        self.accurate = False
        self.framerate = framerate
        self.deltaTime: float = 0
        self.time: float = 0

    def start(self) -> float:
        """
        Start the player
        """
        self.startTime = pg.time.get_ticks()
        self.deltaTime = 0
        self.time = 0
        return self.deltaTime

    def tick(self) -> float:
        """
        Should be called at the end of the main loop

        Returns
        -------
        float
            time elapsed since last call
        """
        if self.accurate:
            self.deltaTime = self.clock.tick_busy_loop(self.framerate) / 1000.0
        else:
            self.deltaTime = self.clock.tick(self.framerate) / 1000.0
        self.time += self.deltaTime
        return self.deltaTime

    def getDeltaTime(self) -> float:
        """
        Get the time difference between last call to :attr:`tick` and the one before
        """
        return self.deltaTime

    def getTime(self) -> float:
        """
        Get elalpsed time since :attr:`start` was called
        """
        return self.time
        # if self.accurate:
        #     self.time += self.deltaTime
        #     return self.time
        # else:
        #     return (pg.time.get_ticks() - self.startTime) / 1000.0 + self.time

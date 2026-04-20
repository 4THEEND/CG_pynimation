import numpy
from typing import Optional, Dict, TextIO, List

# import scipy
import time
from itertools import islice

from threading import Thread

from pynimation.anim import Skeleton
from pynimation.anim import Animation
from pynimation.io.importer import Importer
from pynimation.anim import Joint


class BVHImporter(Importer):
    """
    Import animations from BVH files
    """

    extension = "bvh"

    def __init__(self) -> None:
        self.clear()

    def clear(self) -> None:
        """ """
        self.skeleton: Optional[Skeleton] = None
        self.animation: Optional[Animation] = None
        self.frameRate: Optional[int] = None
        self.channelPositions: Dict["Joint", str] = dict()
        self.channelRotations: Dict["Joint", str] = dict()

    def load(self, filename: str) -> List["Animation"]:
        """

        Parameters
        ----------
        filename: str :


        Returns
        -------

        """
        self.clear()

        file_: TextIO = open(filename, "r")
        self.__skipBlankLines(file_)
        line = file_.readline()
        if "HIERARCHY" not in line:
            raise Exception('expected "HIERARCHY", got ' + line)

        line = file_.readline()
        tokens = line.split()
        if tokens[0] == "ROOT":
            jointname = tokens[1]

        self.__loadJoint(file_, jointname, None)

        self.__skipBlankLines(file_)

        line = file_.readline()
        if "MOTION" not in line:
            raise Exception('expected "MOTION", got ' + line)

        self.__loadAnimation(file_, None)

        file_.close()
        assert self.animation is not None
        return [self.animation]

    def __loadJoint(
        self, file: TextIO, jointName: str, parent: Optional["Joint"]
    ) -> None:

        joint = Joint(jointName, parent)
        if self.skeleton is None:
            self.skeleton = Skeleton(joint)
        else:
            self.skeleton.add(joint, parent=parent)

        line = file.readline()
        tokens = line.split()

        while tokens[0] != "}":

            line = file.readline()
            tokens = line.split()

            if tokens[0] in ["ROOT", "JOINT", "End"]:

                childName = tokens[1]
                self.__loadJoint(file, childName, joint)

            elif tokens[0] == "OFFSET":
                joint.transform.setPosition(
                    [float(tokens[1]), float(tokens[2]), float(tokens[3])]
                )
            elif tokens[0] == "CHANNELS":
                if int(tokens[1]) == 6:
                    self.channelPositions[joint] = (
                        tokens[2][0] + tokens[3][0] + tokens[4][0]
                    )
                    self.channelRotations[joint] = (
                        tokens[5][0] + tokens[6][0] + tokens[7][0]
                    )
                elif int(tokens[1]) == 3:
                    self.channelRotations[joint] = (
                        tokens[2][0] + tokens[3][0] + tokens[4][0]
                    )

    def __skipBlankLines(self, file: TextIO) -> None:
        if file is None:
            return
        line = ""
        while not line.strip():
            pos = file.tell()
            line = file.readline()
        file.seek(pos)

    def __loadAnimation(
        self, file: TextIO, numberOfFrames=Optional[int]
    ) -> None:

        self.__skipBlankLines(file)
        line = file.readline()
        tokens = line.split()
        if tokens[0] != "Frames:":
            raise Exception("Missing frame number in BVH file format")
        frameNumber = int(tokens[1])

        self.__skipBlankLines(file)
        line = file.readline()
        tokens = line.split()
        if (tokens[0] != "Frame") and (tokens[1] != "Time:"):
            raise Exception("Missing frame time in BVH file format")
        frameTime = float(tokens[2])
        self.frameRate = int(round(1.0 / frameTime))

        self.__skipBlankLines(file)
        if numberOfFrames is not None:
            frameNumber = numberOfFrames
        self.nextNLines = list(islice(file, frameNumber))

        assert self.skeleton is not None
        self.animation = Animation(self.frameRate, self.skeleton, frameNumber)
        t = time.perf_counter() * 1000
        for x in range(frameNumber):
            self.parseFrame(x)

        print("Finished: " + str(time.perf_counter() * 1000 - t))

    def parseFrame(self, frameID: int) -> None:
        """

        Parameters
        ----------
        frameID: int :


        Returns
        -------

        """
        assert self.animation is not None
        assert self.skeleton is not None
        assert frameID >= 0
        tokens = [float(a) for a in self.nextNLines[frameID].split()]
        tokens = numpy.asarray(tokens)

        if len(tokens) != 0:
            tokens = numpy.split(tokens, len(tokens) / 3)

            fr = self.animation.frames[frameID]
            i = 0
            for b in range(0, len(self.skeleton.joints)):
                j = self.skeleton.joints[b]

                if j in self.channelPositions:
                    fr.setBonePosition(b, tokens[i])
                    i += 1
                if j in self.channelRotations:
                    fr.setBoneLocalRotationEuler(
                        b, self.channelRotations[j], tokens[i], True
                    )
                    i += 1


class ThreadCreateFrame(Thread):
    """ """

    def __init__(self, bvhData):
        Thread.__init__(self)
        self.bvhData = bvhData

    def run(self):
        """ """
        running = True
        currentFrame = -1

        with self.bvhData.lock:
            if len(self.bvhData.dataToLoad) == 0:
                running = False
            else:
                currentFrame = self.bvhData.dataToLoad[0]
                del self.bvhData.dataToLoad[0]

        while running:
            self.bvhData.parseFrame(currentFrame)
            # tokens = [float(a) for a in self.bvhData.next_n_lines[currentFrame].split()]
            # tokens = numpy.asarray(tokens)
            # tokens = numpy.split(tokens, len(tokens) / 3)

            # i = 0
            # fr = Frame(self.bvhData.skeleton)
            # for b in range(0, len(fr.skeleton.joints)):
            #     j = fr.skeleton.joints[b]
            #     if j in self.bvhData.channelPositions:
            #         fr.setBonePosition(b, tokens[i])
            #         i += 1
            #     if j in self.bvhData.channelRotations:
            #         fr.setBoneLocalRotationEuler(b, self.bvhData.channelRotations[j], tokens[i], True)
            #         i += 1

            with self.bvhData.lock:
                # self.bvhData.frames[currentFrame] = fr
                if len(self.bvhData.dataToLoad) == 0:
                    running = False
                else:
                    currentFrame = self.bvhData.dataToLoad[0]
                    del self.bvhData.dataToLoad[0]

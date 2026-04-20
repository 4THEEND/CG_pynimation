import numpy
import math
from numpy import float64, ndarray
from typing import List, Union, Optional


class RotationTools:
    """
    Various methods to work with rotation transforms
    """

    @staticmethod
    def normalize(
        v: Union[ndarray, List[float], List[int], List[Union[float, int]]]
    ) -> ndarray:
        """
        Normalize vector :attr:`v`

        Parameters
        ----------
        v:
            vector to normalize

        Returns
        -------
        numpy.ndarray:
            normalized vector

        """
        norm = numpy.linalg.norm(v)
        if norm != 0:
            v = numpy.array(v) / norm
        return numpy.array(v)

    @staticmethod
    def unsignedAngleBetweenDeg(a: ndarray, b: ndarray) -> float64:
        """

        Parameters
        ----------
        a: ndarray :

        b: ndarray :


        Returns
        -------

        """
        na = RotationTools.normalize(a.copy())
        nb = RotationTools.normalize(b.copy())
        angle = numpy.clip(numpy.dot(na, nb), -1, 1)

        return numpy.degrees(math.acos(angle))

    @staticmethod
    def signedAngleBetweenDeg(a, b, rotAxis):
        """

        Parameters
        ----------
        a :

        b :

        rotAxis :


        Returns
        -------

        """
        na = RotationTools.normalize(a.copy())
        nb = RotationTools.normalize(b.copy())
        angle = numpy.clip(numpy.dot(na, nb), -1, 1)
        angle = math.acos(angle)

        axis = RotationTools.normalize(numpy.cross(na, nb))
        dAxis = numpy.dot(axis, rotAxis)
        if dAxis < 0:
            angle = -angle
        return numpy.degrees(angle)

    @staticmethod
    def getAxis(axisLetter: str) -> Optional[List[float]]:
        """

        Parameters
        ----------
        axisLetter: str :


        Returns
        -------

        """
        if axisLetter == "X":
            return [1.0, 0.0, 0.0]
        elif axisLetter == "Y":
            return [0.0, 1.0, 0.0]
        elif axisLetter == "Z":
            return [0.0, 0.0, 1.0]
        else:
            return None

    @staticmethod
    def getRadians(degree):
        """convert degree in radians

        Args:
            degree (number): The angle in degree
        Returns:
            (number): The angle in radians
        """
        return (degree * math.pi) / 180

    @staticmethod
    def getDegrees(radians):
        """convert degree in radians

        Args:
            radians (number): The angle in radians
        Returns:
            (number): The angle in degree
        """
        return (radians * 180) / math.pi

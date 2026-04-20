from typing import Tuple
import struct


class BinaryReader(object):
    """
    Reader class for binary files

    Parameters
    ----------
    filename: str
        path of the file to read

    Attributes
    ----------
    file: ByteIO
        file object of the open file
    """

    def __init__(self, filename: str):
        self.file = open(filename, mode="rb")

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.file.close()

    def readBool(self) -> bool:
        """
        Read boolean

        Returns
        -------
        bool:
            boolean value

        """

        return struct.unpack("<?", self.file.read(1))[0]

    def readUnsignedShortInt(self) -> int:
        """
        Read Unsigned Short

        Returns
        -------
        int:
            unsigned short value

        """

        return struct.unpack("<H", self.file.read(2))[0]

    def readShortInt(self) -> int:
        """
        Read Short

        Returns
        -------
        int:
            short value

        """

        return struct.unpack("<h", self.file.read(2))[0]

    def readInt(self) -> int:
        """
        Read int 32

        Returns
        -------
        int:
            int value

        """

        return struct.unpack("<i", self.file.read(4))[0]

    def readFloat(self) -> float:
        """
        Read float

        Returns
        -------
        float:
            float value

        """

        return struct.unpack("<f", self.file.read(4))[0]

    def readString(self) -> str:
        """
        Read string

        Returns
        -------
        str:
            string value

        """
        strLength = self.readUnsignedShortInt()
        return struct.unpack(
            "<{}s".format(strLength), self.file.read(strLength)
        )[0].decode("utf-8")

    def readVector(self, size) -> Tuple:
        """
        Read vector of size :attr:`size`

        Parameters
        ----------
        size: number of elements of the vector

        Returns
        -------
        Vector value

        """
        return struct.unpack("<%sf" % size, self.file.read(size * 4))

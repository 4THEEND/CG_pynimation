from typing import TYPE_CHECKING
import struct

if TYPE_CHECKING:
    import numpy as np


class BinaryWriter(object):
    """
    Writer class for binary files
    Parameters
    ----------
    filename: str
        path of the file to write

    Attributes
    ----------
    file: ByteIO
        file object of the open file
    """

    def __init__(self, filename: str):
        self.file = open(filename, mode="wb")

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.file.close()

    def writeBool(self, value: bool) -> None:
        """
        Write boolean :attr:`value` to binarywriter

        Parameters
        ----------
        value:
            boolean value to write

        """

        self.file.write(struct.pack("<?", value))

    def writeUnsignedShortInt(self, value: int) -> None:
        """
        Write unsigned short int :attr:`value` to binarywriter

        Parameters
        ----------
        value:
            Unsigned short int value to write

        """

        self.file.write(struct.pack("<H", value))

    def writeShortInt(self, value: int) -> None:
        """
        Write short int :attr:`value` to binarywriter

        Parameters
        ----------
        value:
            Short int value to write

        """

        self.file.write(struct.pack("<h", value))

    def writeInt(self, value: int) -> None:
        """
        Write int :attr:`value` to binarywriter

        Parameters
        ----------
        value:
            Int value to write

        """

        self.file.write(struct.pack("<i", value))

    def writeFloat(self, value: float) -> None:
        """
        Write float :attr:`value` to binarywriter

        Parameters
        ----------
        value:
            Float value to write

        """

        self.file.write(struct.pack("<f", value))

    def writeString(self, value: str) -> None:
        """
        Write string :attr:`value` to binarywriter

        Parameters
        ----------
        value:
            String value to write

        """

        self.writeUnsignedShortInt(len(value))
        self.file.write(
            struct.pack(
                "<{}s".format(len(value)),
                bytes(value, "utf-8"),
            )
        )

    def writeVector(self, value: "np.ndarray") -> None:
        """
        Write vector :attr:`value` to binarywriter

        Parameters
        ----------
        value:
            vector to write

        """

        self.file.write(struct.pack("<%sf" % value.size, *value.flatten("F")))

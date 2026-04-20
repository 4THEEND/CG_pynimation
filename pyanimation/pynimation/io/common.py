import typing
import os


def _ioFactory(ioClass: typing.Any, extension: str) -> typing.Any:
    """

    Parameters
    ----------
    ioClass: typing.Any :

    extension: str :


    Returns
    -------

    """

    def allSubclasses(cls):
        """ """
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in allSubclasses(c)]
        )

    ioImplementations = [
        class_
        for class_ in allSubclasses(ioClass)
        if class_.extension == extension
    ]

    if len(ioImplementations) > 0:
        return ioImplementations[0]()
    else:
        raise NotImplementedError(
            "No "
            + ioClass.__name__
            + "implementation was found for file extension "
            + extension
        )


def _getExtension(filename: str) -> str:
    """

    Parameters
    ----------
    filename: str :


    Returns
    -------

    """
    _, basename = os.path.splitext(filename)
    return basename.replace(".", "").lower()

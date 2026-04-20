import os
import sys


def getDataPath(relativePath: str) -> str:
    """
    Return the absolute path of a file or folder inside one of pynimation packages
    :code:`data` folder

    Parameters
    ----------
    path:
        path to the file or folder inside the data folder, relative to
        :code:`pynimation/data`

    Examples
    --------
    >>> from pynimation.common.data import data
    >>> data.getDataPath("data/shaders/diffuse_ps.glsl")
    '/home/user/src/pynimation/pynimation-viewer/pynimation/data/shaders/diffuse_ps.glsl'

    >>> from pynimation.common.data import data
    >>> data.getDataPath("data/shaders/")
    '/home/user/src/pynimation/pynimation-viewer/pynimation/data/shaders/'

    Returns
    -------
    str:
        the absolute path to the file or folderinside the package

    """
    module_paths = list(sys.modules["pynimation"].__path__)  # type: ignore
    for path in module_paths:
        data_path = path + "/" + relativePath
        if os.path.exists(data_path):
            return data_path
    raise Exception(
        "Could not find "
        + relativePath
        + " in modules paths "
        + str(module_paths)
    )

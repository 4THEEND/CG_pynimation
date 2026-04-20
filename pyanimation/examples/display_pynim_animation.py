from pynimation.io import load
from pynimation.viewer import Viewer
from pynimation.common import data as data_

pynim_file = data_.getDataPath("data/animations/ybot@IdleLoop.pynim")

[animation] = load(pynim_file)

Viewer().displayAnimation(animation)

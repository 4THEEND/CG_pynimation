from pynimation.io import load
from pynimation.viewer import Viewer
from pynimation.common import data as data_

mvnx_file = data_.getDataPath("data/animations/Benjamin_100_comfort.mvnx")

[animation] = load(mvnx_file)
Viewer().displayAnimation(animation)

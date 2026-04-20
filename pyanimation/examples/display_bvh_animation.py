from pynimation.io import load
from pynimation.viewer import Viewer
from pynimation.common import data as data_

bvh_file = data_.getDataPath("data/animations/Walk_loop.bvh")

[animation] = load(bvh_file)
Viewer().displayAnimation(animation)

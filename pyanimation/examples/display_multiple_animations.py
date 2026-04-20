from pynimation.io import load
from pynimation.viewer import Viewer
from pynimation.common import data as data_

bvh_file = data_.getDataPath("data/animations/Walk_loop.bvh")

animations = []
for f in [bvh_file] * 3:
    animations.append(load(f)[0])
Viewer().displayAnimations(animations)

from pynimation.io import load

from pynimation.viewer import Viewer
from pynimation.common import data as data_

fbx_file = data_.getDataPath("data/animations/ybot@IdleLoop.fbx")

[animation] = load(fbx_file)
Viewer().displayAnimation(animation)

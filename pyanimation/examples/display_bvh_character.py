from pynimation.viewer.io import mesh_importer as importer
from pynimation.viewer import Viewer
from pynimation.common import data as data_

bvh_file = data_.getDataPath("data/animations/Walk_loop.bvh")

[character] = importer.loadCharacters(bvh_file)
Viewer().display(character)

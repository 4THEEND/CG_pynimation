from pynimation.viewer.io import mesh_importer as importer
from pynimation.viewer import Viewer
from pynimation.common import data as data_

fbx_file = data_.getDataPath("data/animations/ybot@IdleLoop.fbx")
fbx_model_file = data_.getDataPath("data/models/ybot.fbx")

[character] = importer.loadCharacters(fbx_file, fbx_model_file)
Viewer().display(character)

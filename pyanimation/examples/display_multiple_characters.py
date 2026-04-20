from typing import List, cast
from pynimation.viewer.io import mesh_importer as importer
from pynimation.viewer import Viewer
from pynimation.viewer import Character
from pynimation.viewer import SceneNode
from pynimation.common import data as data_

fbx_file = data_.getDataPath("data/animations/ybot@IdleLoop.fbx")

characters: List[Character] = []
for f in [fbx_file] * 3:
    characters.append(importer.loadCharacters(f)[0])
viewer = Viewer()
scene = viewer.defaultScene()
scene.addInLine(cast(List[SceneNode], characters))
viewer.displayScene(scene)

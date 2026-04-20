from pynimation.viewer import Viewer
from pynimation.viewer.io import mesh_importer as importer
from pynimation.viewer import Scene
from pynimation.common import data as data_

bvh_file = data_.getDataPath("data/animations/Walk_loop.bvh")
fbx_file = data_.getDataPath("data/animations/ybot@IdleLoop.fbx")

scene = Scene()
plane = Viewer.defaultFloor()
scene.add(plane)
[fbx_character] = importer.loadCharacters(fbx_file)
[bvh_character] = importer.loadCharacters(bvh_file)
# characters and their descendants globalTransforms are invalidated
fbx_character.transform.translate([3, 0, 0])
bvh_character.transform.translate([-3, 0, 0])
scene.add(fbx_character)
scene.add(bvh_character)
# invalid globalTransforms are recomputed
Viewer().displayScene(scene)

from pynimation.viewer import Viewer
from pynimation.viewer.io import mesh_importer as importer
from pynimation.viewer import Scene
from pynimation.common import data as data_
from pynimation.viewer import CallableLoop

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


# callable loop
class Display(CallableLoop):
    # the default initialization is the scene
    def __init__(self, viewer: Viewer, scene: Scene, priority: int):
        self.scene: Scene = scene
        # initialization of the father, only the priority is needed
        CallableLoop.__init__(self, viewer, priority)

    # the before display
    def beforeDisplay(self):
        print("before")

    # the after display
    def afterDisplay(self):
        print("after")


v = Viewer()

display = Display(v, scene, priority=5)

# invalid globalTransforms are recomputed
v.displayScene(scene)

import math
import numpy
from numpy import ndarray
from pyquaternion import Quaternion
from pynimation.viewer import Viewer
from pynimation.viewer.io import mesh_importer as importer
from pynimation.viewer import Scene
from pynimation.common import data as data_
from pynimation.viewer import CallableLoop
from pynimation.viewer.objects import Plane
from pynimation.viewer.objects import Cylinder
from pynimation.viewer.objects import Sphere
from pynimation.viewer.objects import Cube
from pynimation.viewer.objects import Arrow
from pynimation.viewer.objects import ReferenceSystem
from pynimation.viewer.objects import Triangle


bvh_file = data_.getDataPath("data/animations/Walk_loop.bvh")
fbx_file = data_.getDataPath("data/animations/ybot@IdleLoop.fbx")

scene = Scene()
plane = Viewer.defaultFloor()
scene.add(plane)
[fbx_character] = importer.loadCharacters(fbx_file)
[bvh_character] = importer.loadCharacters(bvh_file)
# characters and their descendants globalTransforms are invalidated
fbx_character.transform.translate([1, 0, 0])
bvh_character.transform.translate([-0.5, 0, -1])
scene.add(fbx_character)
scene.add(bvh_character)


# callable loop
class Display(CallableLoop):
    # the default initialization is the scene
    def __init__(self, viewer: Viewer, scene: Scene, priority: int):
        self.numberOfLoops: int = 100
        self.loop_i: int = 0
        self.scene: Scene = scene
        # quad
        self.quad: Plane = Plane(
            width=0.5,
            height=0.5,
            normalDirectionAx="x",
            color=[50 / 250, 120 / 250, 120 / 250, 1],
            textureFilename="floor_blue.bmp",
            fromFloorPosition=0,
        )
        self.targetPos = [1, 1, -2]
        self.scene.add(self.quad)
        # cylinder
        self.cylinder: Cylinder = Cylinder(
            height=1.0,
            radiusBase=0.4,
            radiusTop=0.1,
            numberOfSectors=30,
            numberOfStacks=3,
            center=True,
            color=[1, 0.5, 0.4, 1],
            height_direction="y",
            phong=True,
        )
        self.scene.add(self.cylinder)
        # cube
        self.cube: Cube = Cube(1.0, color=[0.2, 0.5, 0.1])
        self.scene.add(self.cube)
        # arrow
        self.arrow1 = Arrow()
        scene.add(self.arrow1)
        self.arrow2 = Arrow(color=[0.9, 0.2, 0.3])
        scene.add(self.arrow2)
        self.arrow2.transform.setPosition(numpy.array([2, 2, 2]))
        # sphere
        self.sphere = Sphere(0.055, [1, 1, 1, 0.8])
        self.scene.add(self.sphere)
        # reference system
        self.referenceSystem1 = ReferenceSystem()
        self.referenceSystem2 = ReferenceSystem()
        self.scene.add(self.referenceSystem1)
        self.scene.add(self.referenceSystem2)
        # triangle
        self.triangle: Triangle = Triangle()
        self.scene.add(self.triangle)
        # initialization of the father, only the priority is needed
        CallableLoop.__init__(self, viewer, priority)

    # the before display
    def beforeDisplay(self):
        k = math.sin(self.loop_i * math.pi / self.numberOfLoops)
        self.loop_i = self.loop_i + 1
        # quad
        currentPose = numpy.array(self.targetPos) + numpy.array([0, k, 0])
        self.quad.globalTransform.setPosition(currentPose)
        quaternion: Quaternion = Quaternion(axis=[0, 1, 0], angle=k)
        self.quad.globalTransform.setQuaternion(quaternion)
        self.quad.setMixParameter(k)
        # cylinder
        currentPose = numpy.array(self.targetPos) + numpy.array([-0.6, 0, 0])
        self.cylinder.globalTransform.setPosition(currentPose)
        translatonVector: ndarray = numpy.array([0, k / 60, 0])
        self.cylinder.globalTransform.translate(translatonVector)
        quaternion2: Quaternion = Quaternion(axis=[0, 1, 0], angle=k)
        self.cylinder.globalTransform.setQuaternion(quaternion2)
        # cube
        currentPose = numpy.array(self.targetPos) + numpy.array([1, 0, -1])
        self.cube.globalTransform.setPosition(currentPose)
        translatonVector: ndarray = numpy.array([0, 0, k])
        self.cube.globalTransform.translate(translatonVector)
        # arrow
        direction: ndarray = numpy.array([1, 1 + k, 1])
        self.arrow1.pointAt(direction)
        self.arrow2.pointAt(direction)
        # sphere
        self.sphere.globalTransform.setPosition(direction)
        # reference system
        direction: ndarray = numpy.array([-1, 1 + k, 1])
        self.referenceSystem1.setPosition(direction)
        # triangle
        direction: ndarray = numpy.array([-1, 1.5 - k / 2, -1])
        quaternion2: Quaternion = Quaternion(axis=[1, 1, 0], angle=k)
        self.triangle.globalTransform.setQuaternion(quaternion2)
        self.triangle.transform.setPosition(direction)

    # if not used still need to be defined
    def afterDisplay(self):
        pass


v = Viewer()
display = Display(v, scene, priority=5)
v.displayScene(scene)

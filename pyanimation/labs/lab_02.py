import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./pynimation-viewer"))

import math
import numpy
from numpy import ndarray
from pyquaternion import Quaternion

from pynimation.io import load
from pynimation.common.transform import Transform
from pynimation.common import data as data_

from pynimation.viewer import Viewer
from pynimation.viewer import Scene
from pynimation.viewer import CallableLoop
from pynimation.viewer.objects import Plane
from pynimation.viewer.objects import Sphere
from pynimation.viewer.objects import ReferenceSystem
from pynimation.viewer.stickfigure import StickFigure

scene = Scene()
plane = Viewer.defaultFloor()
scene.add(plane)

fbx_file = "data/animations/ybot@IdleLoop.pynim"

# callable loop
class MyCharacter():

    def __init__(self, filename: str):
        """
        MyCharacter (see Character class for more complex, mesh-based example)
        Loads animations from :attr:`filename`
        A :class:`~pynimation.viewer.stickfigure.StickFigure` mesh will be created and used as a mesh for the character

        Parameters
        ----------0]
        filename:
            file to load animations from
        """
        self.animation = load(data_.getDataPath(filename))
        if(isinstance(self.animation, list)):
            self.animation = self.animation[0]
        self.animation.createRootProjectionProxy()    
        self.mesh = StickFigure(self.animation.skeleton)

        self.animation.skeleton.mapHumanoidSkeleton()

# callable loop
class Display(CallableLoop):
    # the default initialization is the scene
    def __init__(self, viewer: Viewer, scene: Scene, priority: int):
        self.scene: Scene = scene
        self.viewer = viewer

        #ANIMATION AND CHARACTER
        self.fbx_character = MyCharacter(fbx_file)
        self.scene.add(self.fbx_character.mesh)
        
        # SPHERE TO FOLLOW THE POSITION OF THE RIGHT/LEFT ANKLES
        self.sphereR: Sphere = Sphere(0.03, color=[1.0, 0.0, 0.0, 1])
        self.sphereL: Sphere = Sphere(0.03, color=[0.0, 1.0, 0.0, 1])
        self.scene.add(self.sphereL)
        self.scene.add(self.sphereR)
        
        # reference system
        self.referenceSystem1 = ReferenceSystem()
        self.scene.add(self.referenceSystem1)
        
        # initialization of the father, only the priority is needed
        CallableLoop.__init__(self, viewer, priority)

    # the before display
    def beforeDisplay(self):
        currentTime = self.viewer.player.time
        frame = self.fbx_character.animation.getFrameFromTime(currentTime)
        self.fbx_character.mesh.animate(frame)

        frame.globalTransforms[frame.skeleton.head.id]

        # TODO SPECIFY THE SPHERER and SPHEREL POSITION TO MATCH THE RIGHT AND LEFT ANKLE POSITIONS
        pass

    # if not used still need to be defined
    def afterDisplay(self):
        pass


v = Viewer()
display = Display(v, scene, priority=5)
v.displayScene(scene)

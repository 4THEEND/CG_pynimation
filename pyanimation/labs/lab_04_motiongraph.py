import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./pynimation-viewer"))

import pathlib
from pynimation.io import load
from pynimation.io import exporter
from pynimation.common import data as data_
from pynimation.anim.motiongraph.motiongraph import MotionGraph
from pynimation.anim.motiongraph.randomwalk import RandomWalk
from pynimation.anim.metrics.local_orientation_no_root import (
    LocalOrientationWithoutRootMetric as CurrentMetric,
)

from pynimation.viewer import Viewer
from pynimation.viewer import Scene
from pynimation.viewer import CallableLoop
from pynimation.viewer.objects import ReferenceSystem
from pynimation.viewer.stickfigure import StickFigure


mographFileName = data_.getDataPath("data/animations/") + "test_large.mograph"

def animFilesToPynim() -> None:
    animFilenames = [
        "ybot@WalkingForwardLoop",
        "ybot@WalkingForwardLoop",
        "ybot@IdleLoop",
        "ybot@WalkingBackwardLoop",
        "ybot@WalkingLeftTurnLoop",
        "ybot@WalkingRightTurnLoop",
    ]

    for fn in animFilenames:
        [anim_file] = load(data_.getDataPath("data/animations/") + fn + ".fbx")
        anim_file.setFramerate(30)
        exporter.save(
            anim_file,
            data_.getDataPath("data/animations/") + fn + ".pynim",
        )


def createMotionGraph(mographFilename: str) -> None:

    # example of how to include animation files for the motion graph creation.
    # These files are not included on the repository but can be downloaded from mixamo for isntance
    animFilenames = [
        "data/animations/ybot@WalkingForwardLoop.pynim",
        "data/animations/ybot@WalkingBackwardLoop.pynim",
        "data/animations/ybot@WalkingLeftTurnLoop.pynim",
        "data/animations/ybot@WalkingRightTurnLoop.pynim",
    ]

    anim_files = [load(data_.getDataPath(fn))[0] for fn in animFilenames]
    for anim in anim_files:
        anim.skeleton.mapHumanoidSkeleton()
    mograph = MotionGraph(
        CurrentMetric(),
        anim_files,
        skeletonMap=anim_files[0].skeleton.SkeletalPart.defaultSkeleton(),
        framerate=30,
        threshold=0.5,
    )
    mograph.save(mographFileName)


# callable loop
class MotionGraphCharacter:
    def __init__(self, filename: str):
        """
        MyCharacter (see Character class for more complex, mesh-based example)
        Loads animations from :attr:`filename`
        A :class:`~pynimation.viewer.stickfigure.StickFigure` mesh will be created and used as a mesh for the character

        Parameters
        ----------
        filename:
            file to load animations from
        """
        self.mograph = MotionGraph()
        self.mograph.load(filename)
        self.randomwalk = RandomWalk(self.mograph)

        self.mesh = StickFigure(self.mograph.nodes[0].frame.skeleton)

    def animate(self, deltaTime: float) -> None:
        self.randomwalk.update(deltaTime)
        self.mesh.animate(self.randomwalk.getCurrentFrame())


# callable loop
class Display(CallableLoop):
    # the default initialization is the scene
    def __init__(self, viewer: Viewer, scene: Scene, mographFile: str, priority: int):
        self.scene: Scene = scene
        self.viewer = viewer
        self.start_iteration = 2

        # ANIMATION AND CHARACTER
        self.mograph_character = MotionGraphCharacter(mographFile)
        self.scene.add(self.mograph_character.mesh)

        # reference system
        self.referenceSystem1 = ReferenceSystem()
        self.scene.add(self.referenceSystem1)

        # initialization of the father, only the viewer is needed
        # registers beforeDisplay and afterDisplay loop callbacks to the viewer
        CallableLoop.__init__(self, viewer, priority)

    # the before display
    def beforeDisplay(self):
        if self.start_iteration == 0:
            self.mograph_character.animate(self.viewer.player.getDeltaTime())
        else:
            self.start_iteration -= 1

    # if not used still need to be defined
    def afterDisplay(self):
        pass


def visualizeMotionGraph(mographFilename: str) -> None:

    scene = Viewer.defaultScene()
    v = Viewer()
    Display(v, scene, mographFilename, priority=5)
    v.displayScene(scene)


# Uncomment if you want to convert new fbxfiles to pyanim files (quicker to load afterwards)
#animFilesToPynim()

# If the MotionGraph file 'mographFileName' does not exist, then create it
if(not pathlib.Path(mographFileName).is_file()):
    createMotionGraph(mographFileName)


# Visualize animations using the motion graph
visualizeMotionGraph(mographFileName)

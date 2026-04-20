import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./pynimation-viewer"))

import pathlib
from pynimation.io import load
from pynimation.io import exporter
from pynimation.common import data as data_
from pynimation.anim.skeleton import Skeleton
from pynimation.anim.metrics.similarity import Similarity
from pynimation.anim.metrics.local_orientation_no_root import LocalOrientationWithoutRootMetric
from pynimation.anim.metrics.global_orientation import GlobalOrientationMetric
from pynimation.anim.metrics.local_orientation_velocity import LocalOrientationVelocity

from pynimation.viewer import Viewer
from pynimation.viewer import Scene
from pynimation.viewer import CallableLoop
from pynimation.viewer.objects import ReferenceSystem
from pynimation.viewer.stickfigure import StickFigure


animFilenames = [
    "data/animations/ybot@WalkingForwardLoop.pynim",
    "data/animations/ybot@WalkingBackwardLoop.pynim",
    "data/animations/ybot@WalkingLeftTurnLoop.pynim",
    "data/animations/ybot@WalkingRightTurnLoop.pynim",
]

id0 = 0
id1 = 1

anim0 = load(data_.getDataPath(animFilenames[id0]))[0]
anim0.skeleton.mapHumanoidSkeleton()

anim1 = load(data_.getDataPath(animFilenames[id1]))[0]
anim1.skeleton.mapHumanoidSkeleton()

"""sim = Similarity(LocalOrientationWithoutRootMetric(), anim1=anim0, skeletonMap=Skeleton.SkeletalPart.defaultSkeleton())
sim.toImage('./pynimation/data/similarity0.png')

sim = Similarity(LocalOrientationWithoutRootMetric(), anim1=anim0, anim2=anim1, skeletonMap=Skeleton.SkeletalPart.defaultSkeleton())
sim.toImage('./pynimation/data/similarity1.png')"""

sim = Similarity(GlobalOrientationMetric(), anim1=anim0, anim2=anim1, skeletonMap=Skeleton.SkeletalPart.defaultSkeleton())
sim.toImage('./pynimation/data/similarity2.png')

sim = Similarity(LocalOrientationVelocity(), anim1=anim0, anim2=anim1, skeletonMap=Skeleton.SkeletalPart.defaultSkeleton())
sim.toImage('./pynimation/data/similarity3.png')
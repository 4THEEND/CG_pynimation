import numpy as np
from pynimation.io import load
from pynimation.viewer import Viewer
from pynimation.viewer import Character
from pynimation.common import data as data_
from pynimation.anim.tools import ikFactory
from pynimation.viewer.objects import Sphere

bvh_file = data_.getDataPath("data/animations/Walk_loop.bvh")

[animation] = load(bvh_file)
target_id = 26
target = animation.skeleton.joints[target_id]
root = target.parent.parent
animation_orig = animation.copy()
ik = ikFactory(target, root)
for f in animation.frames:
    targetPos = f.globalTransforms[target.id].getPosition() + np.array(
        [0, 0.1, 0]
    )
    ik.solve(targetPos, f)

v = Viewer()
scene = Viewer.defaultScene()
characters = [Character(a) for a in [animation, animation_orig]]
for a in characters:
    scene.add(a)
target_sphere = Sphere(0.02, color=[0, 0.9, 0, 1])
print(scene.graph)
print(
    """To display a sphere on the target joint of the IK, we can parent it to
the mesh (called a Capsule) this joint corresponds to
Looking at the scene graph above, we can see that each character has a child
called StickFigure that holds all the Capsules
The Capsule we are interested in has the same id in the list of children of
StickFigure as the joint it corresponds to
So we write:
characters[0].children[0         # get StickFigure
    ].children[26                # get Capsule for joint 26
    ].addChild(target_sphere)    # add the sphere to its children
"""
)

characters[0].children[0].children[26].addChild(target_sphere)
v.displayScene(scene)

from pynimation.viewer import Viewer
from pynimation.io import load
from pynimation.common import Transform
from scipy.spatial.transform import Rotation
from pynimation.common import data as data_

bvh_file = data_.getDataPath("data/animations/Walk_loop.bvh")
fbx_file = data_.getDataPath("data/animations/ybot@IdleLoop.fbx")

[animation] = load(bvh_file)

r = Rotation.from_euler("xyz", [90, 0, 0], degrees=True).as_matrix()
t = Transform()
t.setRotation(r)
for f in animation.frames:
    # globalTransforms[24] and its descendants are invalidated
    f.localTransforms[25] = t

    # globalTransforms[25] and its descendants are invalidated
    # f.localTransforms[25].setRotation(r)

    # globalTransforms[25] and its descendants are invalidated
    # f.localTransforms[25].matrix = t.matrix

    # transforms = [Transform() for j in f.localTransforms]
    # all globalTransforms are invalidated
    # f.localTransforms = transforms

    # /!\ globalTransforms[25] is not invalidated
    # f.localTransforms[25].matrix[1][2] = 2
    # need to invalidate ourselves
    # f._invalidateRecursive(25)

# invalid globalTransforms are recomputed
Viewer().displayAnimation(animation)

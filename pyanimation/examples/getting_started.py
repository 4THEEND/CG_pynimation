from pynimation.io import load
from pynimation.io import save
from pynimation.viewer import Viewer
from pynimation.common import data
from scipy.spatial.transform import Rotation
from copy import deepcopy

# obtain path to provided example BVH animation file
bvh_file = data.getDataPath("data/animations/Walk_loop.bvh")

# load the animation
[animation] = load(bvh_file)

# keep the original untouched
animationPost = deepcopy(animation)

# process the animation

# get the id of the joint to be modified
knee_joint_id = animation.skeleton.jointsNames.index("RightKnee")

# access the frames
for i in range(10, 200):
    frame = animationPost.frames[i]
    # access joint transform
    kneeTransform = frame.localTransforms[knee_joint_id]
    # modify joint transform
    r = Rotation.from_euler("xyz", [90, 0, 0], degrees=True).as_matrix()
    kneeTransform.rotate(r)

# export the modified animation
save(animationPost, "modified.fbx")

# display original and modified animations side by side
Viewer().displayAnimations([animation, animationPost])

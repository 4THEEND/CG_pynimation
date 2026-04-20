from typing import TYPE_CHECKING, List, Optional

from pyquaternion import Quaternion

from pynimation.anim.metrics.metric import Metric

if TYPE_CHECKING:
    from pynimation.anim import Animation
    from pynimation.anim import Skeleton


import numpy

class LocalOrientationVelocity(Metric):
    """Similarity metric based on joints local orientation excluding the root joint and with velocity"""


    def compute_velocity(
        self, 
        frameID: int,
        anim: "Animation",
        skelID: int
    ) -> List:
        previousFrame = None
        currentFrame = None 

        dt = 1 / anim.framerate

        if frameID == 0:
            previousFrame = anim.frames[frameID]
            currentFrame = anim.frames[1]
        else:
            previousFrame = anim.frames[frameID - 1]
            currentFrame = anim.frames[frameID]

        return (currentFrame.globalTransforms[skelID].getPosition() - previousFrame.globalTransforms[skelID].getPosition()) / dt
    

    def prepareFrame(
        self,
        frameID: int,
        anim: "Animation",
        skeletonMap: Optional[List["Skeleton.SkeletalPart"]] = None,
    ) -> List:

        frame = anim.frames[frameID]
        subSkel = frame.skeleton.getSubSkeleton(skeletonMap)

        # Append positions
        dataFramePrepared = []
        T = frame.globalTransforms[frame.skeleton.root.id].inverse()

        for j in range(len(subSkel)):
            if subSkel[j] != frame.skeleton.root.id:
                
                dataFramePrepared.append(
                    (T * frame.globalTransforms[subSkel[j]]).getPosition()
                )

        
        # Append velocities
        for j in range(len(subSkel)):
            if subSkel[j] != frame.skeleton.root.id:
                dataFramePrepared.append(
                    self.compute_velocity(frameID, anim, subSkel[j])
                )
        

        return dataFramePrepared

    def evaluate(
        self, dataFrame1: List[Quaternion], dataFrame2: List[Quaternion]
    ) -> float:
        assert len(dataFrame1) == len(dataFrame2)

        similarity = 0
        for j in range(len(dataFrame1)):
            p1 = dataFrame1[j]
            p2 = dataFrame2[j]
            similarity += numpy.linalg.norm(p2 - p1)

        return similarity

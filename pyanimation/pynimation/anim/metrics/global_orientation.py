from typing import TYPE_CHECKING, List, Optional

from pyquaternion import Quaternion

import numpy

from pynimation.anim.metrics.metric import Metric

if TYPE_CHECKING:
    from pynimation.anim import Animation
    from pynimation.anim import Skeleton


class GlobalOrientationMetric(Metric):
    """Similarity metric based on joints local orientation excluding the root joint"""

    def prepareFrame(
        self,
        frameID: int,
        anim: "Animation",
        skeletonMap: Optional[List["Skeleton.SkeletalPart"]] = None,
    ) -> List:

        frame = anim.frames[frameID]
        subSkel = frame.skeleton.getSubSkeleton(skeletonMap)


        dataFramePrepared = []
        T = frame.globalTransforms[frame.skeleton.root.id].inverse()

        for j in range(len(subSkel)):
            if subSkel[j] != frame.skeleton.root.id:
                
                dataFramePrepared.append(
                    (T * frame.globalTransforms[subSkel[j]]).getPosition()
                )

        return dataFramePrepared

    def evaluate(
        self, dataFrame1: List[numpy.ndarray], dataFrame2: List[numpy.ndarray]
    ) -> float:
        assert len(dataFrame1) == len(dataFrame2)

        similarity = 0
        for j in range(len(dataFrame1)):
            p1 = dataFrame1[j]
            p2 = dataFrame2[j]
            similarity += numpy.linalg.norm(p2 - p1)

        return float(similarity)

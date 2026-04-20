from typing import TYPE_CHECKING, List, Optional

from pyquaternion import Quaternion

from pynimation.anim.metrics.metric import Metric

if TYPE_CHECKING:
    from pynimation.anim import Animation
    from pynimation.anim import Skeleton


class LocalOrientationWithoutRootMetric(Metric):
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
        for j in range(len(subSkel)):
            if subSkel[j] != frame.skeleton.root.id:
                dataFramePrepared.append(
                    frame.localTransforms[subSkel[j]].getQuaternion()
                )

        return dataFramePrepared

    def evaluate(
        self, dataFrame1: List[Quaternion], dataFrame2: List[Quaternion]
    ) -> float:
        assert len(dataFrame1) == len(dataFrame2)

        similarity = 0
        for j in range(len(dataFrame1)):
            q1 = dataFrame1[j]
            q2 = dataFrame2[j]
            similarity += min(
                Quaternion.log(q1.inverse * q2).norm,
                Quaternion.log(q1.inverse * (-q2)).norm,
            )

        return similarity

import abc

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from pynimation.anim import Animation
    from pynimation.anim import Skeleton


class Metric(abc.ABC):
    """
    Base class for similarity metrics. Can be given to
    :class:`~pynimation.similarity.similarity.Similarity` to compute the
    similarity of two animations according to this metric
    """

    def prepareFrame(
        self,
        frameID: int,
        anim: "Animation",
        skeletonMap: Optional[List["Skeleton.SkeletalPart"]] = None,
    ) -> List:
        """
        Prepare the data to be evaluated for frame :arg:`frameID` of :arg:`anim`

        Parameters
        ----------
        frameID :
            index of the frame to prepare in :arg:`anim`

        anim :
            animation to prepare

        skeletonMap :
            Parts of the skeleton that should be included in the comparison
            If :code:`None`, all the joitns of the skeleton will be included

        Returns
        -------
        The data to be used in the evaluate function of this metric for frame :arg:`frameID` of :arg:`anim`

        """
        pass

    def prepareAnimation(
        self,
        anim: "Animation",
        skeletonMap: Optional[List["Skeleton.SkeletalPart"]] = None,
    ) -> List:
        """
        Prepare the data to be evaluated for :arg:`anim`

        Parameters
        ----------
        anim :
            animation to prepare

        skeletonMap :
            Parts of the skeleton that should be included in the comparison
            If :code:`None`, all the joitns of the skeleton will be included

        Returns
        -------
        The data to be used in the evaluate function of this metric for :arg:`anim`

        """
        return [
            self.prepareFrame(id, anim, skeletonMap)
            for id in range(anim.getFrameNumber())
        ]

    def evaluate(
        self, dataFrame1: List, dataFrame2: List
    ) -> float:
        """
        Evaluate this metric on data from frame :arg:`dataFrame1` and :arg:`dataFrame2`

        Parameters
        ----------
        dataFrame1 :
            data of the first frame to compare

        dataFrame2 :
            data of the second frame to compare

        Returns
        -------
        The value of this metric for data of the frame :arg:`dataFrame1` and :arg:`dataFrame2`

        """
        pass

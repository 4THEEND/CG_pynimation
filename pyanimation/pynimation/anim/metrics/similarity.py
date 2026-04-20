from typing import TYPE_CHECKING, List, Optional, Union

import numpy as np
import math
from scipy.ndimage import gaussian_filter
import scipy.ndimage.filters as filters
import scipy.ndimage.morphology as morphology

from PIL import Image, ImageDraw

from pynimation.anim.metrics.metric import Metric

if TYPE_CHECKING:
    from pynimation.anim import Animation
    from pynimation.anim import Skeleton


class Similarity:
    """
    Uses implementations of :class:`~pynimation.similarity.metric.Metric` to
    compute a similarity metric between :arg:`anim1` and :arg:`anim2`


    Parameters
    ----------

    metric: Metric
        Implementation of :class:`~pynimation.similarity.metric.Metric` that
        will be used to compare animations

    anim1: Animation
        First animation to compare

    anim2: Optional[Animation]
        Second animation to compare. If None, :arg:`anim1` will be compared to
        itself

    skeletonMap: Optional[List["Skeleton.SkeletalPart"]]
        Parts of the skeleton that should be included in the comparison
        If :code:`None`, all the joitns of the skeleton will be included
        This is passed to :arg:`metric`'s
        :function:`~pynimation.similarity.metric.Metric.evaluate` function

    Attributes
    ----------

    metric: Metric
        Implementation of :class:`~pynimation.similarity.metric.Metric` that
        will be used to compare animations

    anim1: Animation
        First animation to compare

    anim2: Optional[Animation]
        Second animation to compare. If None, :arg:`anim1` will be compared to
        itself

    skeletonMap: Optional[List["Skeleton.SkeletalPart"]]
        Parts of the skeleton that should be included in the comparison
        If :code:`None`, all the joitns of the skeleton will be included
        This is passed to :arg:`metric`'s
        :function:`~pynimation.similarity.metric.Metric.evaluate` function

    similarities: np.ndarray
        Similarity matrix computed by :arg:`computeSimilarity()`

    selfSimilarity: bool
        Does this Similarity instance compare an animation to itself
    """

    def __init__(
        self,
        metric: Metric,
        anim1: "Animation",
        anim2: Optional["Animation"] = None,
        dataAnim1: Optional[List] = None,
        dataAnim2: Optional[List] = None,
        skeletonMap: Optional[List["Skeleton.SkeletalPart"]] = None,
    ):
        self.metric = metric
        self.anim1 = anim1
        self.anim2 = anim2
        dataAnim1 = dataAnim1 or metric.prepareAnimation(anim1, skeletonMap)
        self._dataAnim1 = dataAnim1
        self._nbFramesAnim1 = self.anim1.getFrameNumber()

        # Are we computing self-similarity
        self.selfSimilarity = self.anim2 is None
        if self.selfSimilarity:
            self.anim2 = self.anim1
            dataAnim2 = self._dataAnim1
        elif dataAnim2 is None:
            dataAnim2 = metric.prepareAnimation(anim2, skeletonMap)
        self._dataAnim2 = dataAnim2

        assert self.anim2 is not None

        self._nbFramesAnim2 = self.anim2.getFrameNumber()
        self.skeletonMap = skeletonMap

        self.similarities = np.zeros(
            (self._nbFramesAnim1, self._nbFramesAnim2), dtype="float32"
        )
        self.computeSimilarity()

        self.localMinima: Optional[np.ndarray] = None

    def computeSimilarity(self) -> None:
        """
        Compute similarity matrix between :arg:`anim1` and :arg:`anim2`
        according to :arg:`metric`. The resulting matrix is stored in the
        :arg:`similarities` attribute
        """
        if self.selfSimilarity:
            nbSimilarities = self._nbFramesAnim1 * (self._nbFramesAnim1 + 1) / 2
            id = 0
            for i in range(self._nbFramesAnim1):
                for j in range(i, self._nbFramesAnim2):
                    pc = int(float(id) / float(nbSimilarities) * 100)
                    print('\rComputing Similarity: {}/{} ({}%)'.format(id,nbSimilarities,pc), end='')    
                    self.similarities[i][j] = self.similarities[j][i] = self.metric.evaluate(
                        self._dataAnim1[i], self._dataAnim2[j]
                    )
                    id = id + 1
        else:
            nbSimilarities = self._nbFramesAnim1 * self._nbFramesAnim2
            for i in range(self._nbFramesAnim1):
                for j in range(self._nbFramesAnim2):
                    id = i * self._nbFramesAnim2 + j
                    pc = int(float(id) / float(nbSimilarities) * 100)
                    print('\rComputing Similarity: {}/{} ({}%)'.format(id,nbSimilarities,pc), end='')
                    self.similarities[i][j] = self.metric.evaluate(
                        self._dataAnim1[i], self._dataAnim2[j]
                    )

    def gaussianSmooth(self, sigma: Union[int, np.ndarray] = 3) -> None:
        """
        Apply a Gaussian filter to the similarity matrix

        Parameters
        ----------
        sigma:
            sigma parameter of the filter
        """
        self.similarities = gaussian_filter(self.similarities, sigma=sigma)

    def computeLocalMinima(self):
        """
        Compute the local minima of the similarity matrix
        """
        # localMinimaX = np.transpose(argrelmin(self.similarities, axis=0))
        # localMinimaY = np.transpose(argrelmin(self.similarities, axis=1))

        # FROM https://stackoverflow.com/questions/3684484/peak-detection-in-a-2d-array/3689710#3689710

        # define a connected neighborhood
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#generate_binary_structure
        neighborhood = morphology.generate_binary_structure(
            len(self.similarities.shape), 2
        )

        # apply the local minimum filter; all locations of minimum value
        # in their neighborhood are set to 1
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.filters.html#minimum_filter
        local_min = (
            filters.minimum_filter(
                self.similarities, footprint=neighborhood, mode="constant"
            )
            == self.similarities
        )

        # local_min is a mask that contains the peaks we are looking for, but also the background.
        # In order to isolate the peaks we must remove the background from the mask.
        # we create the mask of the background
        background = self.similarities == 0

        # a little technicality: we must erode the background in order to
        # successfully subtract it from local_min, otherwise a line will
        # appear along the background border (artifact of the local minimum filter)
        # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#binary_erosion
        eroded_background = morphology.binary_erosion(
            background, structure=neighborhood, border_value=1
        )

        # we obtain the final mask, containing only peaks,
        # by removing the background from the local_min mask
        detected_minima = local_min ^ eroded_background
        self.localMinima = np.where(detected_minima)

    def getLocalMinima(self, threshold: float = 1.0) -> np.ndarray:
        """
        Return the local minima for a given threshold

        Parameters
        ----------
        threshold:
            threshold above which local minima are returned. Must be inside
            [0;1] range, corresponding the to [0;max(similarities)] range

        Returns
        -------
        np.ndarray:
            local minima of the similarity matrix above :attr:`threshold`
        """

        if self.localMinima is None:
            self.computeLocalMinima()

        assert self.localMinima is not None

        localMinValues = (
            self.similarities[self.localMinima] / self.similarities.max()
        )
        th = np.argwhere(localMinValues < threshold)

        return np.transpose(self.localMinima)[np.transpose(th)[0]]

    def toImage(
        self, imageFileName: str, threshold=1.0, dotPercentSize=0.002
    ) -> None:
        """
        Use PIL to convert similarity matrix to image

        Parameters
        ----------
        imageFileName :
            name of the file the image will be saved to
        """
        #
        I8 = (self.similarities / self.similarities.max() * 255).astype(
            np.uint8
        )
        img = Image.fromarray(I8)

        if self.localMinima is not None:
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)
            ellipseRadiusX = math.floor(
                len(self.similarities) * dotPercentSize
            )
            ellipseRadiusY = math.floor(
                len(self.similarities[0]) * dotPercentSize
            )
            for lMin in self.getLocalMinima(threshold):
                if ellipseRadiusX == 0 or ellipseRadiusY == 0:
                    draw.point((lMin[1], lMin[0]), "red")
                else:
                    draw.ellipse(
                        [
                            lMin[1] - ellipseRadiusY,
                            lMin[0] - ellipseRadiusX,
                            lMin[1] + ellipseRadiusY,
                            lMin[0] + ellipseRadiusX,
                        ],
                        fill="red",
                    )

        img.save(imageFileName)
        img.close()

from typing import TYPE_CHECKING, List, Optional, Dict

import numpy
from pyquaternion import Quaternion
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from pynimation.anim.metrics import Similarity
from pynimation.anim.metrics import Metric

from pynimation.io import BinaryReader
from pynimation.io import BinaryWriter
from pynimation.io import PynimImporter
from pynimation.io import PynimExporter
from pynimation.common import Transform

if TYPE_CHECKING:
    from pynimation.anim import Animation
    from pynimation.anim import Skeleton
    from pynimation.anim import Frame


class MotionGraph:
    """A basic Motion Graph Implementation

    Parameters
    ----------

    metric: Metric
        Implementation of :class:`~pynimation.similarity.metric.Metric` that
        will be used to compare animations to create the motion graph

    anims: Optional["List[Animation]"]
        List of animations to use to create the motion graph (animations can also be added to the motion graph afterwards)

    skeletonMap: Optional[List["Skeleton.SkeletalPart"]]
        Parts of the skeleton that should be included in the comparison
        If :code:`None`, all the joints of the skeleton will be included
        This is passed to :arg:`metric`'s
        :function:`~pynimation.similarity.metric.Metric.evaluate` function

    framerate: int
        Framerate at which all the animations will be played

    Attributes
    ----------

    metric: Metric
        Implementation of :class:`~pynimation.similarity.metric.Metric` that
        will be used to compare animations to create the motion graph

    anims: List of animations to use to create the motion graph (animations can also be added to the motion graph afterwards)

    skeletonMap: Optional[List["Skeleton.SkeletalPart"]]
        Parts of the skeleton that should be included in the comparison
        If :code:`None`, all the joints of the skeleton will be included
        This is passed to :arg:`metric`'s
        :function:`~pynimation.similarity.metric.Metric.evaluate` function

    framerate: int
        Framerate at which all the animations will be played

    threshold: float
        Threshold used to detect local minima in the similarity matrix between
        animations

    nodes: List[MotionGraph.MotionGraphNode]
        Nodes of the graph
    """

    class _AnimationData:
        def __init__(
            self, anim: "Animation", dataAnim: List[Quaternion], startIdx: int
        ):
            self.anim = anim
            self.dataAnim = dataAnim
            self.startidx = startIdx

    class MotionGraphNode:
        """
        A Node of :class:`~pynimation.motiongraph.motiongraph.MotionGraph`.
        References the frame of an animation and transitions to other nodes


        Parameters
        ----------

        frame: Frame
            frame referenced by this node

        id: int
            id of the node

        Attributes
        ----------

        frame: Frame
            frame referenced by this node

        id: int
            id of the node

        transitions: Dict[int, Transform]
            dictionary indexing the global transform of the root for each child
            to its id
        """

        def __init__(self, frame: "Frame", id: int):
            self.frame = frame
            self.transitions: Dict[int, Transform] = dict()
            self.id = id

        def addTransition(self, nodeidx: int, deltaTrans: Transform) -> None:
            """
            Add a transition to this node
            """
            self.transitions[nodeidx] = deltaTrans

    def __init__(
        self,
        metric: Metric = None,
        anims: Optional["List[Animation]"] = None,
        skeletonMap: Optional[List["Skeleton.SkeletalPart"]] = None,
        framerate: int = 30,
        threshold: float = 0.2,
    ):
        self.metric: Metric = metric
        self.anims: List["Animation"] = []
        self.skeletonMap: Optional[List["Skeleton.SkeletalPart"]] = skeletonMap

        self.nodes: List[MotionGraph.MotionGraphNode] = []
        self._pruning: List[int] = []

        self.framerate: int = framerate

        self.threshold = threshold

        if anims is None:
            return

        for anim in anims:
            self._addMotion(anim)

        self._prune()

    def _addMotion(self, anim: "Animation") -> None:

        anim.setFramerate(self.framerate)
        anim.createRootProjectionProxy()
        anim.setRelativeRootGlobalTransform()

        animData: MotionGraph._AnimationData = MotionGraph._AnimationData(
            anim,
            self.metric.prepareAnimation(anim, self.skeletonMap),
            len(self.nodes),
        )

        # TODO Function to add a new animation to the motion graph
        return

    def _addMotionNodes(self, anim: "Animation") -> None:

        # TODO Add all the frames as MotionGraph.MotionGraphNode to the current graph

        # TODO Add original transitions between the frames (using the addTransition method)
        
        # TODO Handle the last transition in case the animation is cyclic
        return    

    def _addNewTransitions(
        self,
        animData1: "MotionGraph._AnimationData",
        animData2: Optional["MotionGraph._AnimationData"] = None,
    ) -> None:

        #TODO Function to add the new transitions between two animations (based on their prepared animData)
        return 

    def _prune(self) -> None:
        # TODO Remove connected components of the graph that are not part of the largest connected component.
        # More specifically, it should store in the variable self._pruning the indexes that should be kept (these are then used by the function save to only export the frame indexed by the variable self._pruning)
        return        

    def save(
        self,
        filename: str,
    ) -> None:
        """
        Export motion graph to mograph file :attr:`filename`

        Parameters
        ----------
        filename:
            file to save motion graph to

        """

        print("MotionGraph: Exporting")

        with BinaryWriter(filename) as bn:

            bn.writeUnsignedShortInt(self.framerate)

            PynimExporter.saveSkeleton(self.nodes[0].frame.skeleton, bn)

            bn.writeInt(len(self._pruning))
            for idx in range(len(self._pruning)):
                node = self.nodes[self._pruning[idx]]
                PynimExporter.saveFrame(node.frame, bn)
                bn.writeInt(idx)

                newTrans = dict()
                for t in node.transitions.keys():
                    newTransId = list(
                        filter(
                            lambda x: self._pruning[x] == t,
                            range(len(self._pruning)),
                        )
                    )
                    if len(newTransId) > 0:
                        newTrans[newTransId[0]] = node.transitions[t]

                bn.writeInt(len(newTrans))
                for t in newTrans.keys():
                    bn.writeInt(t)
                    bn.writeVector(newTrans[t].getPosition())
                    bn.writeVector(newTrans[t].getQuaternion().elements)

    def load(
        self,
        filename: str,
    ) -> None:
        """
        Load motion graph from mograph file :attr:`filename`

        Parameters
        ----------
        filename:
            mograph file to load

        """

        with BinaryReader(filename) as bn:

            self.framerate = bn.readUnsignedShortInt()
            skeleton = PynimImporter.loadSkeleton(bn)

            nbNodes = bn.readInt()  # len(self.nodes)
            self.nodes = []
            for n in range(nbNodes):
                fr = PynimImporter.loadFrame(bn, skeleton)
                id = bn.readInt()
                self.nodes.append(MotionGraph.MotionGraphNode(fr, id))
                for t in range(bn.readInt()):
                    tIdx = bn.readInt()
                    deltaPos = bn.readVector(3)
                    deltaQuat = bn.readVector(4)
                    trans = Transform()
                    trans.setRotation(Quaternion(deltaQuat).rotation_matrix)
                    trans.setPosition(deltaPos)
                    self.nodes[n].addTransition(tIdx, trans)

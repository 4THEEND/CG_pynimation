from pynimation.viewer import Viewer
from pynimation.viewer.objects import Cube

cube = Cube()
# cube and its descendants globalTransforms are invalidated
cube.transform.translate([0, 1, 0])
# invalid globalTransforms are recomputed
Viewer().display(cube)

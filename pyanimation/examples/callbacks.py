from pynimation.viewer import Viewer
from pynimation.viewer.objects import Cube

cube = Cube()


# define callback function
def moveCube(cube: Cube):
    position = cube.globalTransform.getPosition()
    position[1] = (position[1] + 0.001) % 2
    cube.globalTransform.setPosition(position)


v = Viewer()

# register callback function
v.addCallback(moveCube, Viewer.CallbackTime.BEFORE_DISPLAY, args=[cube])

s = Viewer.defaultScene()
s.add(cube)

v.displayScene(s)

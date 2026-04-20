import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("./pynimation-viewer"))

import time
import math
import numpy
from numpy import ndarray
from pyquaternion import Quaternion

from pynimation.common.transform import Transform

from pynimation.viewer import Viewer
from pynimation.viewer import Scene
from pynimation.viewer import CallableLoop
from pynimation.viewer.objects import Arrow
from pynimation.viewer.objects import Cube
from pynimation.viewer.objects import Sphere
from pynimation.viewer.objects import ReferenceSystem

from pynimation.viewer.objects import intersect_objects
from pynimation.common.vec3 import Vec3
import random

scene = Scene()

'''
Here each node is represented by a number and the graph by list.
The coordinated associated to a node can be found in the self.node_convert variable.
'''
class RRTGraph:
    def __init__(self, beginpoint, endpoint = None, delta_q = 1/2, bound=20, debug=False, benchmark=True, color = [0.5, 0.5, 0.5, 1]):
        self.continue_rrt = True
        self.benchmark = benchmark
        self.debug = debug
        self.node_color = color


        self.begining = time.time()

        self.node_coordinates: list[Vec3] = []
        self.adj_matrix = []

        # Used to know if we need to end the algorithm
    
        self.comps: list[list[int]] = [[0], [1]] if endpoint is not None else [[0], []]

        self.edges = []

        self.lst_spheres = []

        self.bound = bound
        self.delta_q = delta_q

        self.__add_correspondance(beginpoint, 1, [0, 1, 1, 1])
        if endpoint is  not None:
            self.__add_correspondance(endpoint, 1, [0, 1, 1, 1])
        print(f"Begin: {beginpoint} End: {endpoint}")


    def add_node(self, placed_objects):
        if self.continue_rrt:
            x = self.bound * random.random()
            y = self.bound * random.random()
            z = self.bound * random.random()

            if self.debug:
                print(f"Created point ({x, y, z})")

            nearest_point, nearest_point_ind = self.__find_nearest(Vec3(x, y, z))
            if self.debug:
                print(f"Nearest point: {nearest_point}")

            new_conf = self.__compute_new_conf(nearest_point, Vec3(x, y, z), placed_objects)

            if self.debug:
                print(f"Adding node at {new_conf}")
            self.__add_corres_vec3(new_conf)

            if self.debug:
                print("Adding edge")
            self.__add_arrow(nearest_point, new_conf, ind_origin=len(self.node_coordinates) - 1, ind_target=nearest_point_ind)

            if(nearest_point_ind in self.comps[0]):
                if self.debug:
                    print("New point connected to begin point")
                comp = 0
            else:
                if self.debug:
                    print("New point connected to end point")
                comp = 1
            
            self.comps[comp].append(len(self.node_coordinates) - 1)
            can_be_connected, target = self.__can_be_connected(new_conf, comp, placed_objects)
            
            if can_be_connected and target is not None:
                self.continue_rrt = False
                ind_target = self.node_coordinates.index(target)
                self.__add_arrow(new_conf, target, ind_origin=(len(self.node_coordinates) - 1), ind_target=ind_target)

                if self.benchmark:
                    print(f"Number of nodes {len(self.node_coordinates)} time elapsed: {time.time() - self.begining}")
                    print(self.find_path())
                    # exit(0)
            
            
        else:
            if self.debug:
                print("RRT already connected the two points")


    def get_spheres(self):
        return self.lst_spheres
    

    def get_edges(self):
        return self.edges
    

    def get_nodes(self):
        return self.node_coordinates
    

    def try_connect_other_rtt(self, targets: list[Vec3], placed_objects):
        origin = self.node_coordinates[-1]
        is_connected, target = self.__try_connect_to_list(origin, targets, placed_objects)
        if is_connected and target is not None:
            print("Double RRT is finished")
            self.__add_arrow(origin, target)
            self.continue_rrt = False
            return True
        return False


    def __can_be_connected(self, origin: Vec3, comp: int, placed_objects):
        targets = [self.node_coordinates[i] for i in self.comps[1 - comp]]
        return self.__try_connect_to_list(origin, targets, placed_objects)
    

    def __try_connect_to_list(self, origin: Vec3, targets: list[Vec3], placed_objects):
        for target in targets:
            if intersect_objects(origin, target, placed_objects) is None:
                return True, target
        return False, None


    @staticmethod
    def __compute_distance(vect1: Vec3, vect2: Vec3):
        return (vect2 - vect1).length()


    def __find_nearest(self, vect: Vec3):
        ind_min = 0
        vec_min = self.node_coordinates[0]
        dist_min = self.__compute_distance(vect, self.node_coordinates[0])

        for i in range(1, len(self.node_coordinates)):
            new_dist = self.__compute_distance(vect, self.node_coordinates[i])
            if new_dist < dist_min:
                ind_min = i
                dist_min = new_dist
                vec_min = self.node_coordinates[i]

        return vec_min, ind_min
    

    def __compute_new_conf(self, origin: Vec3, end: Vec3, placed_objects):
        mid = Vec3(
            origin.x * (1 - self.delta_q)  + end.x * self.delta_q,
            origin.y * (1 - self.delta_q)  + end.y * self.delta_q,
            origin.z * (1 - self.delta_q)  + end.z * self.delta_q
        )
        intersection = intersect_objects(origin, mid, placed_objects)
        if self.debug:
            print(f"intersection: {intersection}")
        if intersection is not None:
            return self.__compute_new_conf(origin, intersection, placed_objects)
        return mid

        
    def __add_corres_vec3(self, node: Vec3):
        node_bis = [node.x, node.y, node.z]
        self.__add_correspondance(node_bis, color=self.node_color)


    def __add_correspondance(self, node, size = 0.5, color = [0.5, 0.5, 0.5, 1]):
        self.node_coordinates.append(Vec3(node[0], node[1], node[2]))

        self.lst_spheres.append(Sphere(size, color))
        self.lst_spheres[-1].globalTransform.setPosition(node)
        self.adj_matrix.append([])


    def __add_arrow(self, origin, target: Vec3, ind_origin=None, ind_target=None):
        dist = self.__compute_distance(origin, target)

        self.edges.append(Arrow(length=dist))

        self.edges[-1].setPosition(numpy.array([origin.x, origin.y, origin.z]))
        self.edges[-1].pointAt(numpy.array([target.x, target.y, target.z]))

        if ind_origin is not None and ind_target is not None:
            self.adj_matrix[ind_origin].append(ind_target)
            self.adj_matrix[ind_target].append(ind_origin)


    # Use only with single RRT
    def find_path(self):
        if self.continue_rrt:
            print("Fisrt finish the RRT before calling this function")
            return
        
        return self.__walkthrough(0, 1, [0], [0])


    
    def __walkthrough(self, current_point, target_point, seen_list, path: list[int]):
        if current_point == target_point:
            return True, path
        
        for v in self.adj_matrix[current_point]:
            if v not in seen_list:
                seen_list.append(v)

                path_copy = path.copy()
                path_copy.append(v)

                res, new_path = self.__walkthrough(v, target_point, seen_list, path_copy)
                if res:
                    return True, new_path
        return False, path

        
        




# callable loop
class Display(CallableLoop):
    # the default initialization is the scene
    def __init__(self, viewer: Viewer, scene: Scene, priority: int):
        self.scene: Scene = scene
        self.viewer = viewer
        
        # CUBE
        self.nb_cubes = 100
        self.bound_space = 25
        self.liste_cubes = [[[self.bound_space * random.random(), self.bound_space * random.random(), self.bound_space * random.random()], Cube(2.5)] for _ in range(self.nb_cubes)]

        for i in range(len(self.liste_cubes)):
            self.scene.add(self.liste_cubes[i][1])
            self.liste_cubes[i][1].globalTransform.setPosition(self.liste_cubes[i][0])
        
        # reference system
        self.referenceSystem = ReferenceSystem()
        self.scene.add(self.referenceSystem)
        
        # initialization of the father, only the priority is needed
        CallableLoop.__init__(self, viewer, priority)

        #Init RRT double
        '''
        self.rrt_graph_begin = RRTGraph([self.bound_space, 0, 0])
        self.rrt_graph_end = RRTGraph([0, self.bound_space, self.bound_space], color=[0, 0, 0, 1])
        '''
        self.rrt_graph = RRTGraph([self.bound_space, 0, 0], [0, self.bound_space, self.bound_space])
        self.i = 0

    # the before display
    def beforeDisplay(self):

        currentTime = self.viewer.player.time

        for i in range(len(self.liste_cubes)):
            self.scene.add(self.liste_cubes[i][1])
            self.liste_cubes[i][1].globalTransform.setPosition(self.liste_cubes[i][0])


        # if self.i % 5 == 0:
        lst_objs = [(obj[1], obj[1].transform) for obj in self.liste_cubes]

        '''
        If we need to use the double rrt
        self.rrt_graph_begin.add_node(lst_objs)
        self.rrt_graph_end.add_node(lst_objs)

        if  self.rrt_graph_begin.continue_rrt and  self.rrt_graph_begin.try_connect_other_rtt(self.rrt_graph_end.get_nodes(), lst_objs):
            self.rrt_graph_end.continue_rrt = False


        for sp in self.rrt_graph_begin.get_spheres():
            self.scene.add(sp)

        for sp in self.rrt_graph_end.get_spheres():
            self.scene.add(sp)



        for edge in self.rrt_graph_begin.get_edges():
            self.scene.add(edge)

        for edge in self.rrt_graph_end.get_edges():
            self.scene.add(edge)
        '''
        self.rrt_graph.add_node(lst_objs)

        for sp in self.rrt_graph.get_spheres():
            self.scene.add(sp)



        for edge in self.rrt_graph.get_edges():
            self.scene.add(edge)

        self.i  += 1


    # if not used still need to be defined
    def afterDisplay(self):
        pass



v = Viewer()
display = Display(v, scene, priority=5)
v.displayScene(scene)

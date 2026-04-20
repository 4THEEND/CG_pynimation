

import math
import random

class Vec3(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    # classmethod with a vector
    @classmethod
    def init(cls,v):
        return cls(v[0],v[1],v[2])

    def __sub__(self, v):
        return Vec3(self.x - v.x,
                    self.y - v.y,
                    self.z - v.z)

    def sub(self, v):
        return Vec3(self.x - v.x,
                    self.y - v.y,
                    self.z - v.z)

    def __add__(self, v):
        return Vec3(self.x + v.x,
                    self.y + v.y,
                    self.z + v.z)

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z


    def __mod__(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z


    def __mul__(self, v):
        return Vec3(self.y * v.z - self.z * v.y,
                    self.z * v.x - self.x * v.z,
                    self.x * v.y - self.y * v.x)


    def cross(self, v):
        return Vec3(self.y * v.z - self.z * v.y,
                    self.z * v.x - self.x * v.z,
                    self.x * v.y - self.y * v.x)

    def length(self):
        return math.sqrt(self.x * self.x +
                         self.y * self.y +
                         self.z * self.z)

    def normalize(self):
        l = self.length()
        return Vec3(self.x / l, self.y / l, self.z / l)

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __str__(self):
        return "Vec3({}, {}, {})".format(self.x, self.y, self.z)

    @staticmethod
    def DivVec3(k, v):
        return Vec3.init([v.x / k, v.y / k, v.z / k])

    @staticmethod
    def MultVec3(k, v):
        return Vec3.init([k * v.x, k * v.y, k * v.z])

    @staticmethod
    def AddVec3(k, v):
        return Vec3.init([k + v.x, k + v.y, k + v.z])

    @staticmethod
    def SubVec3(k, v):
        return Vec3.init([k - v.x, k - v.y, k - v.z])

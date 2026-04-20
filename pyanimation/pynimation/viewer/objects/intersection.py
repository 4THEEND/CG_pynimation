from pynimation.common.vec3 import *
from pynimation.viewer.objects import *

import sys

def intersect_objects (source, target, objects):
  '''
  Calcule le point d'intersection entre un segment [source, target] et un
  ensemble d'objets.
  @param source <Vec3>
  @param target <Vec3>
  @param objects <(VBObject, Transform)[]>, Liste de couple associant un
  VBObject et le Transform qui définit sa position dans la scène.
  '''
  # Calcule les points d'intersection avec l'ensemble des objets de la scène
  intersect_points = []
  for (object, transform) in objects:
    intersectPoint = intersect_object (source, target, object, transform)
    if intersectPoint is not None:
      intersect_points.append(intersectPoint)

  # Récupère le point d'intersection le plus proche de la source.
  closest_dist = sys.maxsize
  closest_point = None
  for p in intersect_points:
    dist = (p - source).length()
    if dist < closest_dist:
      closest_dist = dist
      closest_point = p

  # Retourne le point d'intersection le plus proche de la source
  return closest_point

def __matrix_translation (v, matrix):
    '''
    Fonction privée transposant un vecteur v selon la matrice matrix.
    @param v <float[3]>
    @param matrix <Matrix>
    '''
    v0 = matrix.item((0, 0)) * v[0] + matrix.item((0, 1)) * v[1] + matrix.item((0, 2)) * v[2] + matrix.item((0, 3))
    v1 = matrix.item((1, 0)) * v[0] + matrix.item((1, 1)) * v[1] + matrix.item((1, 2)) * v[2] + matrix.item((1, 3))
    v2 = matrix.item((2, 0)) * v[0] + matrix.item((2, 1)) * v[1] + matrix.item((2, 2)) * v[2] + matrix.item((2, 3))
    return [v0, v1, v2]

def intersect_object (source, target, object, transform):
  '''
  Calcule le point d'intersection entre un segment [source, target] et un objet.
  @param source <Vec3>
  @param target <Vec3>
  @param object <VBObject>
  @param transform <Transform>
  '''
  i = 0
  # Récupère la position des points définissant l'objet
  indexBuffer = object.indexBuffer
  vertices = object.data["vPosition"]
  intersect_points = []
  # On parcourt les points 3-par-3 (les triangles) et on calcule l'intersection
  while (i < len(vertices)):
    # Translate les points selon la matrice de transformation de l'objet
    v0 = __matrix_translation(vertices[i], transform.matrix)
    v1 = __matrix_translation(vertices[i + 1], transform.matrix)
    v2 = __matrix_translation(vertices[i + 2], transform.matrix)
    i = i + 3
    triangle = [v0, v1, v2]
    # Calcule l'intersection entre l'objet et le triangle courant
    intersectPoint = intersect_segment_triangle (source, target, triangle)
    if intersectPoint is not None:
      intersect_points.append(intersectPoint)

  # Détermine le point d'intersection le plus proche de la source
  closest_dist = sys.maxsize
  closest_point = None
  for p in intersect_points:
    dist = (p - source).length()
    if dist < closest_dist:
      closest_dist = dist
      closest_point = p
  # Retourne le point d'intersection
  return closest_point

def intersect_segment_triangle (source, target, triangle):
  ray = target - source
  # ray = ray.normalize()
  P = intersect_ray_triangle(source, ray, triangle)
  if P is not None:
    source2P = P - source
    source2target = target - source
    if source2P.length() <= source2target.length():
      return P
  return None

def intersect_ray_triangle (source, ray, triangle):
  '''
  Calcule le point d'intersection entre un segment et un triangle.
  @param source <Vec3>
  @param ray <Vec3>
  @param triangle <float[3][3]>
  '''
  epsilon = 1e-12

  v0 = Vec3.init(triangle[0])
  v1 = Vec3.init(triangle[1])
  v2 = Vec3.init(triangle[2])

  edge1 = v1 - v0
  edge2 = v2 - v0

  h = ray * edge2
  a = edge1 % h

  if (abs(a) < epsilon):
    return None

  f = 1. / a
  s = source - v0
  u = f * (s % h)
  if (u < 0 or u > 1):
    return None

  q = s * edge1
  v = f * (ray % q)
  if (v < 0 or u + v > 1):
    return None

  t = f * (edge2 % q)
  if (t > epsilon):
    temp = Vec3(ray.x * t, ray.y * t, ray.z * t)
    P = source + temp
    return P
  else:
   return None

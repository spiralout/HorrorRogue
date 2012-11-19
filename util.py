import math
import libtcodpy as T

def distance(object1, object2):
   return math.sqrt(((object2.x - object1.x) ** 2) + ((object2.y - object1.y) ** 2))

def roll(max, add = 0):
   return T.random_get_int(0, 1, max) + add


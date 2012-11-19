import libtcodpy as T
import tiles   
from transform import *
from config import *
from util import *

def random_orientation():
   return T.random_get_int(0, 0, 1)

def random_direction():
   return T.random_get_int(0, 0, 3)

class Coord(object):
   def __init__(self, x, y):
      self.x = x
      self.y = y

class Box(object):
   def __init__(self, x, y, w, h):
      self.x = x
      self.y = y
      self.w = w
      self.h = h



class Room(object):
   def __init__(self, w, h): 
      self.w = w
      self.h = h
      self.map = [[tiles.FLOOR for j in range(w)] for i in range(h)]

   def render(self):
      pass
   
class Composite(Room):
   def __init__(self):
      Room.__init__(self, 0, 0)
      self.parts = []

   def add_part(self, part, x, y, fuse = False):
      self.parts.append(part)
      self.resize_map(self.get_new_dimensions(part, x, y))

      x = 0 if x < 0 else x
      y = 0 if y < 0 else y

      for y1 in range(part.h):
         for x1 in range(part.w):
            # do not overwrite existing tiles that are not walls
            if fuse and self.map[y1 + y][x1 + x] in [tiles.WALL, tiles.FLOOR]:
               self.map[y1 + y][x1 + x] = part.map[y1][x1]
            elif not fuse:
               self.map[y1 + y][x1 + x] = part.map[y1][x1]

   def resize_map(self, box):
      new_map = [['.' for x in range(box.w)] for y in range(box.h)]

      for y1 in range(self.h):
         for x1 in range(self.w):
            new_map[y1 + box.y][x1 + box.x] = self.map[y1][x1]

      self.map = new_map
      self.w = box.w
      self.h = box.h

   def get_new_dimensions(self, part, x, y):
      box = Box(0, 0, self.w, self.h)
      
      if x < 0:
         box.x += abs(x)
         box.w += abs(x)
      if y < 0:
         box.y += abs(y)
         box.h += abs(y)
      if x + part.w > box.w - 1:
         box.w += (x + part.w) - box.w
      if y + part.h > box.h - 1:
         box.h += (y + part.h) - box.h

      # box.x, box.y = new origin of old map
      # box.w, box.h = new width, height of map
      return box



   


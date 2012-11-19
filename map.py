import libtcodpy as T
from config import *
import tiles

class Map(object):
   def __init__(self, width, height, template = ''):
      self.width = width
      self.height = height
      self.map = []
      self.template = template
      self.fov_map = T.map_new(width, height)

   def construct(self):
      for y in range(self.height):
         self.map.append([])

         for x in range(self.width):
            if self.template[y][x] == tiles.WALL:
               self.map[y].append(Wall())
            elif self.template[y][x] == tiles.DARKWALL:
               self.map[y].append(DarkWall())
            elif self.template[y][x] == tiles.DOOR:
               self.map[y].append(Door())
            elif self.template[y][x] == tiles.OPENDOOR:
               d = Door()
               d.open()
               self.map[y].append(d)
            elif self.template[y][x] == tiles.STAIRSUP:
               self.map[y].append(StairsUp())
            elif self.template[y][x] == tiles.STAIRSDOWN:
               self.map[y].append(StairsDown())
            elif self.template[y][x] in [tiles.FLOOR, tiles.OPENFLOOR]:
               self.map[y].append(Floor())

      self.construct_fov()

   def construct_fov(self):
      for y in range(self.height):
         for x in range(self.width):
            T.map_set_properties(self.fov_map, x, y, not self.map[y][x].blocked, self.map[y][x].walkable)

   def set_properties(self, x, y, blocked, walkable):
      T.map_set_properties(self.fov_map, x, y, not blocked, walkable)

   def blocked_at(self, x, y):
      return self.map[y][x].blocked

   def recompute_fov(self, x, y, radius):
      T.map_compute_fov(self.fov_map, x, y, radius, FOV_LIGHT_WALLS, FOV_ALGO)

   def visible(self, x, y):
      return T.map_is_in_fov(self.fov_map, x, y)

   def get_string(self):
      rows = []

      for y in range(self.height):
         rows.append(''.join(self.visible_chars(self.map[y], y)))

      return "\n".join(rows)

   def visible_chars(self, map_row, y):
      row = []

      for x in range(len(map_row)):
         if T.map_is_in_fov(self.fov_map, x, y):
            map_row[x].explored = True
            row.append("%c%c%c%c%s%c" % (T.COLCTRL_FORE_RGB, 255, 255, 255, map_row[x].char, T.COLCTRL_STOP))
         elif map_row[x].explored:
            row.append("%c%c%c%c%s%c" % (T.COLCTRL_FORE_RGB, 80, 80, 80, map_row[x].char, T.COLCTRL_STOP))
         else:
            row.append(' ')

      return row


class Tile(object):
   def __init__(self, char, blocked, walkable):
      self.char = char
      self.blocked = blocked
      self.walkable = walkable                                 
      self.explored = False

class Floor(Tile):
   def __init__(self):
      Tile.__init__(self, tiles.FLOOR, False, True)

class DarkWall(Tile):
   def __init__(self):
      Tile.__init__(self, tiles.DARKWALL, True, False)

class Wall(Tile):
   def __init__(self):
      Tile.__init__(self, tiles.WALL, True, False)

class Door(Tile):
   def __init__(self):
      Tile.__init__(self, tiles.DOOR, True, False)
      self.ajar = False

   def open(self):
      self.ajar = True
      self.char = tiles.OPENDOOR
      self.walkable = True
      self.blocked = False

   def close(self):
      self.ajar = False
      self.char = tiles.DOOR
      self.walkable = False
      self.blocked = True

class StairsUp(Tile):
   def __init__(self):
      Tile.__init__(self, tiles.STAIRSUP, False, True)

class StairsDown(Tile):
   def __init__(self):
      Tile.__init__(self, tiles.STAIRSDOWN, False, True)



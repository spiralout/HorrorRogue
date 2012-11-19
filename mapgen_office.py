from mapgen import *

class BuildingCore(Composite):
   def __init__(self, orientation):
      Composite.__init__(self)
      self.orientation = orientation
      self.render()

   def render(self):
      self.render_elevators()
      self.render_stairs()
      self.render_bathrooms()

   def render_elevators(self):
      self.num_elevator_banks = T.random_get_int(0, 1, 2)
      num_elevators = T.random_get_int(0, 1, 3)
      self.elevator_facing = T.random_get_int(0, 0, 3)

      if self.num_elevator_banks == 2:
         if self.orientation == VERTICAL:
            self.elevator_facing = NORTH
            self.add_part(ElevatorBank(num_elevators, SOUTH), 0, 0)
            self.add_part(ElevatorBank(num_elevators, NORTH), 0, 5)
         else:
            self.elevator_facing = WEST
            self.add_part(ElevatorBank(num_elevators, EAST), 0, 0)
            self.add_part(ElevatorBank(num_elevators, WEST), 5, 0)
      else:
         self.add_part(ElevatorBank(num_elevators, self.elevator_facing), 0, 0)

   def render_stairs(self):
      num_staircases = T.random_get_int(0, 1, self.num_elevator_banks)

      if num_staircases == 2:
         if self.orientation == VERTICAL:
            self.add_part(StairCase(NORTH), 0, -2, True)
            self.add_part(StairCase(SOUTH), 0, self.h - 1, True)
         else:
            self.add_part(StairCase(EAST), self.w - 1, 0, True)
            self.add_part(StairCase(WEST), -2, 0, True)
      else:
         if self.elevator_facing == NORTH:
            self.add_part(StairCase(SOUTH), 0, self.h - 1, True)
         elif self.elevator_facing == SOUTH:
            self.add_part(StairCase(NORTH), 0, -2, True)
         elif self.elevator_facing == EAST:
            self.add_part(StairCase(WEST), -2, 0, True)
         elif self.elevator_facing == WEST:
            self.add_part(StairCase(EAST), self.w - 1, 0, True)

   def render_bathrooms(self):
      if self.orientation == HORIZONTAL:
         self.add_part(Bathroom(WEST, 3), self.w + 1, 0, False)
         self.add_part(Bathroom(EAST, 3), -4, 0, False)
      elif self.orientation == VERTICAL:
         self.add_part(Bathroom(NORTH, 3), 0, self.h + 1, False)
         self.add_part(Bathroom(SOUTH, 3), 0, -4, False)


class RoomBlock(Composite):
   def __init__(self, total_width, total_height, min_width, min_height):
      Composite.__init__(self)
      self.total_width = total_width
      self.total_height = total_height
      self.min_width = min_width
      self.min_height = min_height
      self.render()

   def render(self):
      bsp = T.bsp_new_with_size(0, 0, self.total_width, self.total_height)
      T.bsp_split_recursive(bsp, 0, 4, self.min_width, self.min_height, 1.5, 1.5)
      T.bsp_traverse_post_order(bsp, self.bsp_render)

   def bsp_render(self, node, data):
      if T.bsp_is_leaf(node):
         self.add_part(Office(NORTH, node.w, node.h), node.x, node.y)

      return True


class Bathroom(Room):
   def __init__(self, facing, stalls):
      if facing == NORTH or facing == SOUTH:
         width = stalls + 3
         height = 3
      else:
         width = 3
         height = stalls + 3

      Room.__init__(self, width, height)
      self.stalls = stalls
      self.facing = facing
      self.render()

   def render(self):
      for y in range(self.h):
         for x in range(self.w):
            if x == 0 or y == 0 or x == self.w - 1 or y == self.h - 1:
               self.map[y][x] = tiles.WALL
            elif (self.facing == NORTH or self.facing == SOUTH) and y == 1:
               self.map[y][x] = tiles.FLOOR
            elif (self.facing == WEST or self.facing == EAST) and x == 1:
               self.map[y][x] = tiles.FLOOR
      
      if self.facing == NORTH:
         self.map[0][self.w - 2] = tiles.DOOR
      elif self.facing == SOUTH:
         self.map[2][self.w - 2] = tiles.DOOR
      elif self.facing == EAST:
         self.map[self.h - 2][2] = tiles.DOOR
      elif self.facing == WEST:
         self.map[self.h - 2][0] = tiles.DOOR


class ElevatorBank(Composite):
   def __init__(self, num_elevators, facing):
      Composite.__init__(self)
      self.num_elevators = num_elevators
      self.facing = facing
      self.render()

   def render(self):
      for i in range(self.num_elevators):
         if self.facing == NORTH or self.facing == SOUTH:
            self.add_part(Elevator(self.facing), (i * 2), 0, True)
         else:
            self.add_part(Elevator(self.facing), 0, (i * 2), True)
      
class StairCase(Room):
   def __init__(self, facing):
      width = (4 if facing == NORTH or facing == SOUTH else 3)
      height = (4 if facing == EAST or facing == WEST else 3)
      Room.__init__(self, width, height)
      self.facing = facing
      self.render()

   def render(self):
      if self.facing == NORTH or self.facing == SOUTH:
         self.map = [[tiles.WALL for j in range(4)] for i in range(3)]
         self.map[1][1] = tiles.STAIRSDOWN
         self.map[1][2] = tiles.STAIRSUP

         if self.facing == NORTH:
            self.map[0][1] = tiles.DOOR
         else:
            self.map[2][1] = tiles.DOOR
      else:
         self.map = [[tiles.WALL for j in range(3)] for i in range(4)]
         self.map[1][1] = tiles.STAIRSDOWN
         self.map[2][1] = tiles.STAIRSUP

         if self.facing == EAST:
            self.map[1][2] = tiles.DOOR
         else:
            self.map[1][0] = tiles.DOOR


class Elevator(Room):
   DOOR_LOCATIONS = {
      NORTH: Coord(1, 0),
      SOUTH: Coord(1, 2),
      EAST: Coord(2,  1),
      WEST: Coord(0, 1)}

   def __init__(self, facing):
      Room.__init__(self, 3, 3)
      self.facing = facing
      self.render()

   def render(self):
      self.map = [[tiles.WALL for j in range(3)] for i in range(3)]
      self.map[1][1] = tiles.FLOOR
      loc = Elevator.DOOR_LOCATIONS[self.facing]
      self.map[loc.y][loc.x] = tiles.DOOR


class Office(Room):
   REGULAR = 0
   OPEN_WALL = 1
   OPEN_DOOR = 2

   def __init__(self, facing, width, height, avoid_doors_at = None, door_type = None):
      Room.__init__(self, width, height)
      self.facing = facing
      self.door_type = door_type
      self.avoid_doors_at = avoid_doors_at
      self.render()
      
   def render(self):
      for y in range(self.h):
         for x in range(self.w):
            if x == 0 or y == 0 or x == self.w - 1 or y == self.h - 1:
               self.map[y][x] = tiles.WALL
            else:
               self.map[y][x] = tiles.FLOOR

      self.render_door(self.door_type)

   def render_door(self, door_type):
      dice = roll(10)

      # regular door
      if door_type == Office.REGULAR or dice <= 5:
         (door_x, door_y) = self.get_door_location()
#         print "Regular door: (%s, %s)" % (door_x, door_y)
         self.map[door_y][door_x] = tiles.DOOR 
      # open wall
      elif dice <= 8:
#         print "Open wall facing: %s" % ['NORTH', 'EAST', 'SOUTH', 'WEST'][self.facing]
         if self.facing == NORTH:
            for i in range(1, self.w - 1):
               self.map[0][i] = tiles.OPENFLOOR
         elif self.facing == SOUTH:
            for i in range(1, self.w - 1):
               self.map[self.h- 1][i] = tiles.OPENFLOOR
         elif self.facing == EAST:
            for i in range(1, self.h - 1):
               self.map[i][self.w - 1] = tiles.OPENFLOOR
         elif self.facing == WEST:
            for i in range(1, self.h - 1):
               self.map[i][0] = tiles.OPENFLOOR
      # open door
      elif dice <= 10:
         (door_x, door_y) = self.get_door_location()
#         print "Open door: (%s, %s)" % (door_x, door_y)
         self.map[door_y][door_x] = tiles.OPENFLOOR

   def get_door_location(self):
      while True:
         if self.facing == NORTH:
            coords = (T.random_get_int(0, 1, self.w - 2), 0)
         elif self.facing == SOUTH:
            coords = (T.random_get_int(0, 1, self.w - 2), self.h - 1)
         elif self.facing == EAST:
            coords = (self.w -1, T.random_get_int(0, 1, self.h- 2))
         elif self.facing == WEST:
            coords = (0, T.random_get_int(0, 1, self.h - 2))

         if self.avoid_doors_at == None:
            return coords
         
         if coords not in self.avoid_doors_at:
            return coords


class OfficeStrip(Composite):
   def __init__(self, orientation, facing, strip_length, office_width, office_height):
      Composite.__init__(self)
      self.orientation = orientation
      self.facing = facing
      self.strip_length = strip_length
      self.office_width = office_width
      self.office_height = office_height
      self.determinate_dim = (self.office_width if self.orientation == HORIZONTAL else self.office_height)

   def get_num_offices(self):
      return self.strip_length / (self.determinate_dim - 1)

   def get_entrance(self, num_offices):
      return T.random_get_int(0, 0, num_offices - 1)

   def get_oddball(self, num_offices):
      if self.strip_length % (self.determinate_dim - 1) != 0:
         oddball_dim = self.strip_length % (self.determinate_dim - 1) + self.determinate_dim
         oddball_position = T.random_get_int(0, 0, num_offices - 1)
         return (oddball_dim, oddball_position)

      return (None, None)

   def get_office_facing(self, entrance, index):
      if index == entrance:
         return self.facing
      elif index < entrance:
         return EAST if self.orientation == HORIZONTAL else SOUTH
      else:
         return WEST if self.orientation == HORIZONTAL else NORTH

   def get_door_type(self, entrance, index):
      return Office.REGULAR if index == entrance else None
      

class HorizontalOfficeStrip(OfficeStrip):
   def __init__(self, facing, strip_length, office_width, office_height):
      OfficeStrip.__init__(self, HORIZONTAL, facing, strip_length, office_width, office_height)
      self.render()

   def render(self):
      num_offices = self.get_num_offices()
      entrance = self.get_entrance(num_offices)
      (oddball_dim, oddball_position) = self.get_oddball(num_offices)

      for i in range(num_offices):
         facing = self.get_office_facing(entrance, i)
         door_type = self.get_door_type(entrance, i)

         if oddball_position == i:
            self.add_part(Office(facing, oddball_dim, self.office_height, None, door_type), (i * (self.determinate_dim - 1)), 0, True)
         elif oddball_position != None and oddball_position < i:
            self.add_part(Office(facing, self.office_width, self.office_height, None, door_type), ((i - 1) * (self.determinate_dim - 1)) + (oddball_dim - 1), 0, True)
         else:
            self.add_part(Office(facing, self.office_width, self.office_height, None, door_type), (i * (self.determinate_dim - 1)), 0, True)


class VerticalOfficeStrip(OfficeStrip):
   def __init__(self, facing, strip_length, office_width, office_height):
      OfficeStrip.__init__(self, VERTICAL, facing, strip_length, office_width, office_height)
      self.render()

   def render(self):
      num_offices = self.get_num_offices()
      entrance = self.get_entrance(num_offices)
      (oddball_dim, oddball_position) = self.get_oddball(num_offices)

      for i in range(num_offices):
         facing = self.get_office_facing(entrance, i)
         door_type = self.get_door_type(entrance, i)

         if oddball_position == i:
            self.add_part(Office(facing, self.office_width, oddball_dim, None, door_type), 0, (i * (self.determinate_dim - 1)), True)
         elif oddball_position != None and oddball_position < i:
            self.add_part(Office(facing, self.office_width, self.office_height, None, door_type), 0, ((i - 1) * (self.determinate_dim - 1)) + (oddball_dim - 1), True)
         else:
            self.add_part(Office(facing, self.office_width, self.office_height, None, door_type), 0, (i * (self.determinate_dim - 1)), True)


class OfficeBuilding(object):
   def __init__(self, orientation, floors):
      self.orientation = orientation
      self.floors = floors

   def get_core(self):
      self.core = BuildingCore(self.orientation)



class OfficeFloor(Composite):
   TOP_LEFT = 0
   TOP_RIGHT = 1
   BOTTOM_LEFT = 2
   BOTTOM_RIGHT = 3

   CORNER_OFFICE_FACINGS = {
      TOP_LEFT: {HORIZONTAL: SOUTH, VERTICAL: EAST},
      TOP_RIGHT: {HORIZONTAL: SOUTH, VERTICAL: WEST},
      BOTTOM_LEFT: {HORIZONTAL: NORTH, VERTICAL: EAST},
      BOTTOM_RIGHT: {HORIZONTAL: NORTH, VERTICAL: WEST}}

   def __init__(self):
      Composite.__init__(self)
      self.orientation = random_orientation()
      self.render()

   def render(self):
      self.render_core()
      self.render_interior_offices()
      self.render_offices()
      self.render_outer_wall()

   def render_core(self):
      self.core = BuildingCore(self.orientation)
      self.add_part(self.core, 0, 0, False)

   def render_interior_offices(self):
      if self.orientation == HORIZONTAL:
         if T.random_get_int(0, 0, 1) == 0:
            self.add_part(RoomBlock(self.core.h, self.core.h, 4, 4), (0 - self.core.h - 1), 0)
         else:
            self.add_part(RoomBlock(self.core.h, self.core.h, 4, 4), self.core.w + 1, 0)

         if T.random_get_int(0, 0, 1) == 0:
            self.add_part(HorizontalOfficeStrip(NORTH, ((self.w - 1) / 2) - 1, 5, 5), 0, -6)
            self.add_part(HorizontalOfficeStrip(NORTH, ((self.w - 1) / 2) - 1, 5, 5), (self.w / 2) + 1, 0)
         else:
            self.add_part(HorizontalOfficeStrip(SOUTH, ((self.w - 1) / 2) - 1, 5, 5), 0, self.h + 1)
            self.add_part(HorizontalOfficeStrip(SOUTH, ((self.w - 1) / 2) - 1, 5, 5), (self.w / 2) + 1, self.core.h + 1)
      else:
         if T.random_get_int(0, 0, 1) == 0:
            self.add_part(RoomBlock(self.core.w, self.core.w, 4, 4), 0, (0 - self.core.w - 1))
         else:
            self.add_part(RoomBlock(self.core.w, self.core.w, 4, 4), 0, self.core.h + 1)

         if T.random_get_int(0, 0, 1) == 0:
            self.add_part(VerticalOfficeStrip(EAST, ((self.h - 1) / 2) - 1, 5, 5), self.w + 1, 0)
            self.add_part(VerticalOfficeStrip(EAST, ((self.h - 1) / 2) - 1, 5, 5), self.core.w + 1, ((self.h - 1) / 2) + 1)
         else:
            self.add_part(VerticalOfficeStrip(WEST, ((self.h - 1) / 2) - 1, 5, 5), -6, 0)
            self.add_part(VerticalOfficeStrip(WEST, ((self.h - 1) / 2) - 1, 5, 5), 0, ((self.h - 1) / 2) + 1)

   def render_outer_wall(self):
      for y in range(self.h):
         for x in range(self.w):
            if x == 0 or y == 0 or x == self.w - 1 or y == self.h - 1:
               self.map[y][x] = tiles.WALL
   
   def render_offices(self):
      corner_width = T.random_get_int(0, 6, 9)
      corner_height = T.random_get_int(0, 6, 9)
      inner_width = T.random_get_int(0, corner_width - 2, corner_width - 1)
      inner_height = T.random_get_int(0, corner_height - 2, corner_height - 1)

      # corners
      self.add_part(self.get_corner_office(OfficeFloor.TOP_LEFT, corner_width, corner_height, inner_width, inner_height), 0 - corner_width - 1, 0 - corner_height - 1, True)
      self.add_part(self.get_corner_office(OfficeFloor.TOP_RIGHT, corner_width, corner_height, inner_width, inner_height), self.w + 1, 0, True)
      self.add_part(self.get_corner_office(OfficeFloor.BOTTOM_LEFT, corner_width, corner_height, inner_width, inner_height), 0, self.h + 1, True)
      self.add_part(self.get_corner_office(OfficeFloor.BOTTOM_RIGHT, corner_width, corner_height, inner_width, inner_height), self.w - corner_width, self.h - corner_height, True)

      top_width_left = self.w + 1 - corner_width * 2
      left_height_left = self.h + 1 - corner_height * 2
      bottom_width_left = self.w + 1 - corner_width * 2
      right_height_left = self.h + 1 - corner_height * 2

      # strips
      self.add_part(HorizontalOfficeStrip(SOUTH, top_width_left, inner_width, inner_height), corner_width - 1, 0, True)
      self.add_part(HorizontalOfficeStrip(NORTH, bottom_width_left, inner_width, inner_height), corner_width - 1, self.h - inner_height, True)
      self.add_part(VerticalOfficeStrip(EAST, left_height_left, inner_width, inner_height), 0, corner_height - 1, True)
      self.add_part(VerticalOfficeStrip(WEST, right_height_left, inner_width, inner_height), self.w - inner_width, corner_height - 1, True)

   def get_corner_office(self, position, corner_width, corner_height, inner_width, inner_height):
      facing = OfficeFloor.CORNER_OFFICE_FACINGS[position][self.orientation]

      if position == OfficeFloor.TOP_LEFT:
         avoid_doors_at = [(corner_width - 1, inner_height - 1), (inner_width - 1, corner_height - 1)]
      elif position == OfficeFloor.TOP_RIGHT:
         avoid_doors_at = [(0, inner_height - 1), (corner_width - inner_width, corner_height - 1)]
      elif position == OfficeFloor.BOTTOM_LEFT:
         avoid_doors_at = [(corner_width - 1, corner_height - inner_height), (inner_width - 1, 0)]
      elif position == OfficeFloor.BOTTOM_RIGHT:
         avoid_doors_at = [(0, corner_height - inner_height), (corner_width - inner_width, 0)]

      return Office(facing, corner_width, corner_height, avoid_doors_at, Office.REGULAR)


class MapGenerator(object):
   def __init__(self, w, h):
      self.w = w
      self.h = h

   def generate(self, width, height):
      c = OfficeFloor()

      padding_left = (width - c.w) / 2
      padding_top = (height - c.h) / 2

      c.resize_map(Box(padding_left, padding_top, width, height))
      c.render_outer_wall()

      c.map = self.run_transforms(c.map, TRANSFORMS)

      return c.map

   def run_transforms(self, map, transforms):
      new_map = map[:]

      for t in transforms:
         new_map = t.execute(new_map)

      return new_map

if __name__ == '__main__':
   mg = MapGenerator(55, 44)
   map = mg.generate(55, 44)

   for y in range(len(map)):
      print ''.join(map[y])

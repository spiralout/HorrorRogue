
class Transform(object):
   def __init__(self, w, h, match, replace, chance = 1000):
      self.w = w
      self.h = h
      self.match = match
      self.replace = replace
      self.chance = chance


   def execute(self, map):
      new_map = map[:]

      for y in range(len(new_map) - self.h):
         for x in range(len(new_map[0]) - self.w):
            match = True

            for j in range(self.h):
               for i in range(self.w):
                  if new_map[y + j][x + i] != self.match[j][i]:
                     match = False
                     break

            if match:
               for j in range(self.h):
                  for i in range(self.w):
                     if self.chance < 1000 and T.random_get_int(0, 1, 1000) < self.chance:
                        new_map[y + j][x + i] = self.replace[j][i]
                     else:
                        new_map[y + j][x + i] = self.replace[j][i]

      return new_map


TRANSFORMS = []

# convert open floor to plain floor
TRANSFORMS.append(Transform(1, 1, [[',']], [['.']]))

# remove unintentional diagonal openings
TRANSFORMS.append(Transform(2, 2, [['.', '#'], ['#', '.']], [['.', '#'], ['#', '#']]))
TRANSFORMS.append(Transform(2, 2, [['#', '.'], ['.', '#']], [['#', '#'], ['.', '#']]))


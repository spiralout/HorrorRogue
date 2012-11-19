from character import *

class Darkness(Actor):
   def __init__(self, screen, max, chance, speed, torch_radius):
      Actor.__init__(self, speed)
      self.screen = screen
      self.max = max
      self.chance = chance
      self.speed = speed
      self.torch_radius = torch_radius
      self.darkness = 0
      self.darkness_left = 0

   def light_radius(self):
      return self.torch_radius - self.darkness

   def in_darkness(self):
      return self.darkness > (self.max / 2)

   def update(self, player):
      if not self.can_act(TURN_COST):
         return

      # darkness coming up
      if self.darkness > 0 and self.darkness < self.max and self.darkness_left > 0:
         self.darkness += 1
         self.screen.add_message("The darkness closes in.")
      # darkness fading down
      elif self.darkness > 1 and self.darkness < self.max and self.darkness_left == 0:
         self.darkness -= 1
         self.screen.add_message("The darkness continues to fade.")
      # darkness over
      elif self.darkness == 1 and self.darkness_left == 0:
         self.darkness -= 1
         self.screen.add_message("The darkness is gone.")
      # darkness continues
      elif self.darkness == self.max and self.darkness_left > 0:
         self.darkness_left -= 1
         player.fear += 2
      # darkness starts to fade down
      elif self.darkness == self.max and self.darkness_left == 0:
         self.darkness -= 1
         self.screen.add_message("The darkness begins to recede.")
      # darkness begins
      elif T.random_get_int(0, 1, 1000) <= self.chance:
         self.darkness = 1
         self.darkness_left = T.random_get_int(0, 50, 200)
         self.screen.add_message("You feel a chill as the shadows creep in closer.")

      self.acted(TURN_COST)


class World(object):
   def __init__(self, screen):
      self.screen = screen
      self.darkness = Darkness(screen, MAX_DARKNESS, DARKNESS_CHANCE, DARKNESS_SPEED, TORCH_RADIUS)

   def tick(self):
      self.darkness.tick()

   def update(self, player):
      self.darkness.update(player)



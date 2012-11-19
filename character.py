import libtcodpy as T
from gameobject import *
from config import *

def random_walk():
   dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

   return dirs[T.random_get_int(0, 0, 7)]

def direct_path(ox, oy, dx, dy, map):
   path = T.path_new_using_map(map)
   T.path_compute(path, ox, oy, dx, dy)
   (nx, ny) = T.path_walk(path, False)

   return (nx - ox, ny - oy)
   

class Actor(object):
   def __init__(self, speed):
      self.speed = speed
      self.mp = 0

   def tick(self):
      self.mp += self.speed

   def acted(self, turn_cost):
      self.mp -= turn_cost

   def can_act(self, turn_cost):
      return self.mp >= turn_cost


class Character(GameObject, Actor):
   def __init__(self, x, y, dlevel, char, descr, speed):
      GameObject.__init__(self, x, y, dlevel, char, descr)
      Actor.__init__(self, speed)
      self.inv = []
      self.last_attacker = None
      self.encountered = False
      
   def can_move(self, dx, dy, map):
      if map.blocked_at(self.x + dx, self.y + dy):
         return False

      return True

   def update(self, map, npcs):
      self.move(0, 0)

   def next_to(self, x, y):
      return (abs(self.x - x) <= 1 and abs(self.y - y) <= 1)


class Monster(Character):
   def __init__(self, x, y, dlevel, char, descr, speed, exp, fear, health):
      Character.__init__(self, x, y, dlevel, char, descr, speed)
      self.exp = exp
      self.health = health
      self.fear = fear
      self.aggro = False
   

class Zombie(Monster):
   def __init__(self, x, y, dlevel):
      Monster.__init__(self, x, y, dlevel, 'Z', 'a zombie', 9, 10, 10, 20)

   def update(self, map, screen, player, npcs):
      blocked = False

      # if next to player and has aggro, attack
      if self.next_to(player.x, player.y) and self.aggro:
         damage = roll(6)
         player.health -= damage
         player.last_attacker = self
         self.acted(TURN_COST)
         screen.add_message("Zombie hits you for %s damage" % damage)
      # move randomly unless aggro'd then move directly to player
      else:
         if self.aggro:
            (dx, dy) = direct_path(self.x, self.y, player.x, player.y, map.fov_map)
         else:
            (dx, dy) = random_walk()

         # don't walk into other NPCs
         for n in npcs:
            if n.x == self.x + dx and n.y == self.y + dy:
               blocked = True

         # don't walk into player
         if player.x == self.x + dx and player.y == self.y + dy:
            blocked = True

         # move if not blocked by map
         if not blocked and not map.blocked_at(self.x + dx, self.y + dy):
            self.acted(TURN_COST)
            self.move(dx, dy)


class Player(Character):
   def __init__(self, x, y, level):
      Character.__init__(self, x, y, level, '@', 'the player', 12)
      self.health = self.max_health = 100
      self.weapon = None
      self.turns = 0
      self.last_target = None
      self.exp = 0
      self.fear = 0
      self.panicked = False

   def acted(self, turn_cost):
      self.mp -= turn_cost
      self.turns += 1

   def get_weapons(self):
      return filter(lambda i: isinstance(i, Weapon), self.inv)

   def can_pick_up(self, item):
      return self.x == item.x and self.y == item.y

   def get_ammo(self):
      for i in self.inv:
         if isinstance(i, Ammo) and i.weapon_class == self.weapon.__class__:
            return i.count

      return 0
      
   def update(self):
      # fade fear
      if self.turns % 2 == 0 and self.fear > 0:
         self.fear -= 1

      self.panicked = True if self.fear > 100 else False
      

   def encounter(self, monster):
      if not monster.encountered:
         monster.encountered = True
         self.fear += monster.fear

   def use_ammo(self, weapon_class, count):
      for i in self.inv:
         if isinstance(i, Ammo) and i.weapon_class == weapon_class:
            i.count -= (count if count <= i.count else i.count)
            return

   def pick_up(self, item):
      item.x = item.y = -1

      if isinstance(item, Stackable):
         stacked = False

         for i in self.inv:
            if isinstance(i, item.__class__):
               i.count += item.count
               stacked = True

         if not stacked:
            self.inv.append(item)
      else:
         self.inv.append(item)

   def wield(self, item):
      try:
         i = self.inv.index(item)
      except ValueError:
         return False

      self.weapon = item

   def in_range(self, npcs):
      if not isinstance(self.weapon, RangedWeapon):
         return []

      results = []

      for n in npcs:
         if distance(self, n) <= self.weapon.range:
            results.append(n)

      return results


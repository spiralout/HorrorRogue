import sys
from util import *
from gameobject import *
from screen import *
from map import *
from config import *


class Command(object):
   def __init__(self, screen, player):
      self.player = player
      self.screen = screen

   def execute(self):
      pass

class Quit(Command):
   def execute(self):
      answer = Prompter(self.screen, 'Quit? [yn]', [ord('y'), ord('n')]).get_option()

      if answer == ord('y'):
         sys.exit()

      return

class Wait(Command):
   def execute(self):
      self.player.acted(TURN_COST)
   

class Move(Command):
   def __init__(self, screen, player, map, dx, dy):
      Command.__init__(self, screen, player)
      self.dx = dx
      self.dy = dy
      self.map = map

   def execute(self):
      if self.player.can_move(self.dx, self.dy, self.map):
         self.player.move(self.dx, self.dy)
         self.player.acted(TURN_COST)
         return True
      else:
         return False
   

class Up(Command):
   def __init__(self, screen, player, map, current_level):
      Command.__init__(self, screen, player)
      self.current_level = current_level
      self.map = map

   def execute(self):
      if isinstance(self.map.map[self.player.y][self.player.x], StairsUp):
         self.player.acted(TURN_COST)
         return self.current_level - 1
      else:
         self.screen.add_message("There are no stairs up here.")
         return self.current_level


class Down(Command):
   def __init__(self, screen, player, map, current_level):
      Command.__init__(self, screen, player)
      self.current_level = current_level
      self.map = map

   def execute(self):
      if isinstance(self.map.map[self.player.y][self.player.x], StairsDown):
         self.player.acted(TURN_COST)
         return self.current_level + 1
      else:
         self.screen.add_message("There are no stairs down here.")
         return self.current_level


class Attack(Command):
   def __init__(self, screen, player, target):
      Command.__init__(self, screen, player)
      self.target = target

   def execute(self):
      if not isinstance(self.player.weapon, MeleeWeapon):
         self.screen.add_message("You are not wielding a melee weapon")
         return

      if self.target == None:
         self.screen.add_message("No enemy in that direction")
         return

      damage = self.player.weapon.get_damage()
      self.target.health -= damage
      self.target.aggro = True
      self.player.acted(TURN_COST)

      self.screen.add_message("You hit %s for %s damage" % (self.target.describe(), damage))

      if self.target.health <= 0:
         self.screen.add_message("You kill %s" % self.target.describe())
         self.player.last_target = None
         self.player.exp += self.target.exp
         return self.target


class Fire(Command):
   def __init__(self, screen, player, npcs):
      Command.__init__(self, screen, player)
      self.npcs = npcs

   def execute(self):
      if not isinstance(self.player.weapon, RangedWeapon):
         self.screen.add_message("You are not wielding a ranged weapon")
         return

      if self.player.get_ammo() < 1:
         self.screen.add_message("Out of ammo")
         return
      
      target = Targeter(self.screen, self.player, self.player.in_range(self.npcs)).get_target()

      if target == False:
         return

      if target == None:
         self.screen.add_message("No enemies in range")
         return 

      if distance(self.player, target) > self.player.weapon.range:
         self.screen.add_message("Target out of range")
         return

      damage = self.player.weapon.get_damage()
      self.player.use_ammo(self.player.weapon.__class__, self.player.weapon.burst)
      self.player.acted(TURN_COST)
      target.health -= damage
      target.aggro = True

      self.screen.add_message("You hit %s for %s damage" % (target.describe(), damage))

      if target.health <= 0:
         self.screen.add_message("You kill %s" % target.describe())
         self.player.last_target = None
         self.player.exp += target.exp
         return target
      

class Wield(Command):
   def execute(self):
      weapon = Chooser(self.screen, self.player.get_weapons()).get_choice("What do you want to wield?")
      
      if weapon == None:
         self.screen.add_message("You have no weapons")
      elif weapon:
         self.player.wield(weapon)
         self.screen.add_message("You are now wielding %s" % weapon.describe())
         self.player.acted(TURN_COST)


class Inventory(Command):
   def execute(self):
      rows = []

      for item in self.player.inv:
         rows.append(item.describe())

      info = InfoShower(self.screen, rows).show("You are carrying")

      

class Pickup(Command):
   def __init__(self, screen, player, items):
      Command.__init__(self, screen, player)
      self.items = items
   
   def execute(self):
      for i in self.items:
         if self.player.can_pick_up(i):
            self.player.pick_up(i)
            self.screen.add_message("You picked up %s" % i.describe())
            self.player.acted(TURN_COST)


class Drop(Command):
   def execute(self):
      item = Chooser(self.screen, self.player.inv).get_choice("What do you want to drop?")

      if item == None:
         self.screen.add_message("Nothing to drop")
      elif item:
         self.player.inv.remove(item)
         item.x = self.player.x
         item.y = self.player.y
         self.player.acted(TURN_COST)
         self.screen.add_message("You dropped %s" % item.describe())


class Open(Command):
   def __init__(self, screen, player, map):
      Command.__init__(self, screen, player)
      self.map = map

   def execute(self):
      ds = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
      direction = Prompter(self.screen, "Which direction?", DIR_KEYS).get_option()

      if direction == None:
         return

      (dx, dy) = ds[DIR_KEYS.index(direction)]
      x = self.player.x + dx
      y = self.player.y + dy

      if not isinstance(self.map.map[y][x], Door):
         self.screen.add_message('There is no door there')
         return

      if self.map.map[y][x].ajar:
         self.screen.add_message('That door is already open')
         return

      self.map.map[y][x].open()
      self.map.set_properties(x, y, False, True)
      self.player.acted(TURN_COST)
      self.screen.add_message('Door opened')

      return True


class Close(Command):
   def __init__(self, screen, player, map):
      Command.__init__(self, screen, player)
      self.map = map

   def execute(self):
      ds = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
      direction = Prompter(self.screen, "Which direction?", DIR_KEYS).get_option()

      if direction == None:
         return

      (dx, dy) = ds[DIR_KEYS.index(direction)]
      x = self.player.x + dx
      y = self.player.y + dy

      if not isinstance(self.map.map[y][x], Door):
         self.screen.add_message("There is no door there")
         return

      if not self.map.map[y][x].ajar:
         self.screen.add_message("That door is already closed")
         return

      self.map.map[y][x].close()
      self.map.set_properties(x, y, True, False)
      self.player.acted(TURN_COST)
      self.screen.add_message("Door closed")

      return True


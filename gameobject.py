import libtcodpy as T
from util import *

class GameObject(object):
   def __init__(self, x, y, dlevel, char, descr):
      self.x = x
      self.y = y
      self.dlevel = dlevel
      self.char = char
      self.descr = descr

   def move(self, dx, dy):
      self.x += dx
      self.y += dy

   def describe(self):
      return self.descr


class Item(GameObject):
   def __init__(self, x, y, dlevel, char, descr):
      GameObject.__init__(self, x, y, dlevel, char, descr)
      
class Stackable(GameObject):
   def __init__(self, x, y, dlevel, char, descr, count):
      GameObject.__init__(self, x, y, dlevel, char, descr)
      self.count = count


class Weapon(Item):
   def __init__(self, x, y, dlevel, char, descr):
      Item.__init__(self, x, y, dlevel, char, descr)
      self.wielded = False

   def get_damage(self):
      return 0

class MeleeWeapon(Weapon):
   def __init__(self, x, y, dlevel, descr):
      Weapon.__init__(self, x, y, dlevel, '[', descr)

class Crowbar(MeleeWeapon):
   def __init__(self, x, y, dlevel):
      MeleeWeapon.__init__(self, x, y, dlevel, 'a crowbar')
      
   def get_damage(self):
      return roll(6)


class RangedWeapon(Weapon):
   def __init__(self, x, y, dlevel, descr, range):
      Weapon.__init__(self, x, y, dlevel, ']', descr)
      self.range = range
      self.ammo = 0
      self.burst = 1


class MachineGun(RangedWeapon):
   def __init__(self, x, y, dlevel):
      RangedWeapon.__init__(self, x, y, dlevel, 'a machinegun', 6)
      self.burst = 3

   def get_damage(self):
      return roll(10)      


class Ammo(Stackable):
   def __init__(self, x, y, dlevel, char, descr, count):
      Stackable.__init__(self, x, y, dlevel, char, descr, count)
      self.weapon_class = None


class MachineGunAmmo(Ammo):
   def __init__(self, x, y, dlevel, count):
     Ammo.__init__(self, x, y, dlevel, '"', 'machinegun ammo', count)
     self.weapon_class = MachineGun

   def describe(self):
      return self.descr + " (%s)" % self.count
      


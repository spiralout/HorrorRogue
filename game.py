import sys
import libtcodpy as T
from gameobject import *
from character import *
from screen import *
from world import *
from map import *
import command
import tiles

class Game(object):
   def __init__(self, screen, levels, dark_levels):
      self.screen = screen
      self.levels = levels
      self.dark_levels = dark_levels
      self.npcs = []
      self.items = []
      self.current_level = 0
      self.first_frame = True
      self.player_moved = False

   def prepare(self):
      self.world = World(self.screen)
      self.screen.init_window()
      
      [l.construct() for l in self.levels]
      [l.construct() for l in self.dark_levels]

      (x, y) = self.get_starting_location()
      self.player = Player(x, y, 0)
      self.npcs.append(Zombie(30, 30, 0))
      self.npcs.append(Zombie(32, 32, 0))
      self.npcs.append(Zombie(34, 34, 0))
      self.npcs.append(Zombie(36, 36, 0))

      self.player.pick_up(MachineGun(-1, -1, 0))
      self.player.pick_up(MachineGunAmmo(-1, -1, 0, 22))
      self.player.pick_up(Crowbar(-1, -1, 0))

   def get_starting_location(self):
      x = self.get_current_level().width / 2
      y = self.get_current_level().height / 2

      while not isinstance(self.get_current_level().map[y][x], Floor):
         x += 1
         y += 1

      return (x, y)

   def get_current_level(self):
      if self.world.darkness.in_darkness():
         try:
            if isinstance(self.dark_levels[self.current_level], Map):
               return self.dark_levels[self.current_level]
         except:
            pass

      return self.levels[self.current_level]

   def tick(self):
      self.world.tick()
      self.player.tick()
      [n.tick() for n in self.npcs_on_current_level()]

   def handle_input(self, key):
      dx = dy = 0

      # QUIT
      if key.c == ord('q'):
         command.Quit(self.screen, self.player).execute()
         return

      # PICK UP
      elif key.c == ord('g'):
         command.Pickup(self.screen, self.player, self.items_on_current_level()).execute()
         return 

      # OPEN
      elif key.c == ord('o'):
         if command.Open(self.screen, self.player, self.get_current_level()).execute():
            self.player_moved = True
         return

      # CLOSE
      elif key.c == ord('c'):
         if command.Close(self.screen, self.player, self.get_current_level()).execute():
            self.player_moved = True
         return

      # DROP
      elif key.c == ord('d'):
         command.Drop(self.screen, self.player).execute()
         return

      # FIRE
      elif key.c == ord('f'):
         target = command.Fire(self.screen, self.player, self.npcs_on_current_level()).execute()
         if target:
            self.npcs.remove(target)
         return

      # INVENTORY
      elif key.c == ord('i'):
         command.Inventory(self.screen, self.player).execute()
         return

      # WIELD
      elif key.c == ord('w'):
         command.Wield(self.screen, self.player).execute()
         return

      # DOWN
      elif key.c == ord('>'):
         self.current_level = command.Down(self.screen, self.player, self.get_current_level(), self.current_level).execute()
         return

      # UP
      elif key.c == ord('<'):
         self.current_level = command.Up(self.screen, self.player, self.get_current_level(), self.current_level).execute()
         return
   
      # WAIT
      elif key.c == ord('.'):
         command.Wait(self.screen, self.player).execute()
         return

      # MOVE / ATTACK
      elif key.vk == T.KEY_UP or key.vk == T.KEY_KP8:
         dy = -1
      elif key.vk == T.KEY_DOWN or key.vk == T.KEY_KP2:
         dy = 1
      elif key.vk == T.KEY_LEFT or key.vk == T.KEY_KP4:
         dx = -1
      elif key.vk == T.KEY_RIGHT or key.vk == T.KEY_KP6:
         dx = 1
      elif key.vk == T.KEY_KP7:
         dx = dy = -1
      elif key.vk == T.KEY_KP9:
         dx = 1
         dy = -1
      elif key.vk == T.KEY_KP1:
         dx = -1
         dy = 1
      elif key.vk == T.KEY_KP3:
         dx = dy = 1

      if dx != 0 or dy != 0:
         target = self.npc_at_location(self.player.x + dx, self.player.y + dy)

         if target:
            if command.Attack(self.screen, self.player, target).execute():
               self.npcs.remove(target)
         else:
            self.player_moved = command.Move(self.screen, self.player, self.get_current_level(), dx, dy).execute()


   def npcs_on_current_level(self):
      return filter(self.on_current_level, self.npcs)
      
   def items_on_current_level(self):
      return filter(self.on_current_level, self.items)
      
   def npc_at_location(self, x, y):
      for n in self.npcs_on_current_level():
         if n.x == x and n.y == y:
            return n

   def on_current_level(self, object):
      return object.dlevel == self.current_level

   def show_death(self):
      lines = [
         "You are dead. You were killed by %s." % self.player.last_attacker.describe(),
         "",
         "Press ESC to quit"]

      self.screen.show_curtain("\n".join(lines))

      while True:
         key = T.console_wait_for_keypress(True)

         if key.vk == T.KEY_ESCAPE:
            return
   
   def loop(self):
      self.screen.add_info("Welcome!")

      while not T.console_is_window_closed():
         if SHOW_MEMORY: print HEAPY.heap()

         if not self.first_frame:
            # check if player is dead
            if self.player.health <= 0:
               self.show_death()
               sys.exit()
         
            # update darkness 
            self.world.update(self.player)

            # update movement points for current level
            self.tick()

            # handle player turn
            if self.player.can_act(TURN_COST):
               key = T.console_wait_for_keypress(True)
               self.handle_input(key)

            # handle all NPCs on level
            for o in self.npcs_on_current_level():
               if o.can_act(TURN_COST):
                  o.update(self.get_current_level(), self.screen, self.player, self.npcs_on_current_level())

         for i in self.items_on_current_level():
            if i.x == self.player.x and i.y == self.player.y:
               self.screen.add_info("There is %s here." % i.descr)

         if self.player_moved or self.first_frame:
            self.get_current_level().recompute_fov(self.player.x, self.player.y, self.world.darkness.light_radius())

         self.first_frame = False
         self.player.update()
         self.screen.render_and_update(self.get_current_level(), self.player, self.items_on_current_level(), self.npcs_on_current_level(), self.current_level)


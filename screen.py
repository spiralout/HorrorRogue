import libtcodpy as T
from gameobject import *
from config import *
from character import *

class Frame(object):
   def __init__(self, x, y, w, h):
      self.x = x
      self.y = y
      self.width = w
      self.height = h
      self.con = T.console_new(self.width, self.height)

   def clear(self):
      T.console_clear(self.con)

   def blit(self, console = 0):
      T.console_blit(self.con, 0, 0, self.width, self.height, console, self.x, self.y)
      

class InfoFrame(Frame):
   def __init__(self, x, y, w, h):
      Frame.__init__(self, x, y, w, h)
      self.info = ''

   def add_message(self, text):
      self.info += text + ' '

   def render(self):
      T.console_print_left(self.con, 0, 0, T.BKGND_NONE, self.info)

   def wipe(self):
      self.info = ''


class PromptFrame(Frame):
   def render(self, prompt, options):
      T.console_print_left(self.con, 0, 0, T.BKGND_NONE, prompt)


class MapFrame(Frame):
   def render(self, map, items, npcs, player):
      T.console_print_left(self.con, 0, 0, T.BKGND_NONE, map.get_string())
      self.render_objects(items, map, player)
      self.render_objects(npcs, map, player)
      self.render_objects([player], map, player)

   def render_objects(self, objects, map, player):
      for object in objects:
         if object.x >= 0 and object.y >= 0 and map.visible(object.x, object.y):
            if isinstance(object, Monster):
               player.encounter(object)
            T.console_put_char(self.con, object.x, object.y, object.char, T.BKGND_NONE) 

class AuxFrame(Frame):
   def render(self, text):
      T.console_print_left(self.con, 0, 0, T.BKGND_NONE, text)


class MessageLog(Frame):
   def __init__(self, x, y, w, h):
      Frame.__init__(self, x, y, w, h)
      self.messages = []

   def add_message(self, text):
      self.messages.append(text)

   def render(self):
      T.console_print_left(self.con, 0, 0, T.BKGND_NONE, "\n".join(self.messages[-self.height:]))
      
class StatusFrame(Frame):
   def __init__(self, x, y, w, h):
      Frame.__init__(self, x, y, w, h)
   
   def render(self, current_level, player):
      lines = []
      lines.append("Dlvl: %s" % current_level)
      lines.append("")
      lines.append("HP: %s/%s" % (player.health, player.max_health))
      lines.append("Wpn: %s" % (player.weapon.describe() + (" (" + str(player.get_ammo()) + ")" if isinstance(player.weapon, RangedWeapon) else "") if player.weapon else "None"))
      lines.append("Fear: %s" % player.fear)
      lines.append("Exp: %s" % player.exp)
      lines.append("Turns: %s" % player.turns)
      lines.append("")
      
      if player.panicked:
         lines.append("-- PANICKED --")

      T.console_print_left(self.con, 0, 0, T.BKGND_NONE, "\n".join(lines))

class TargetingFrame(Frame):
   def render(self, x, y):
      T.console_put_char(self.con, x - 1, y - 1, '+', T.BKGND_NONE)
      T.console_put_char(self.con, x - 1, y + 1, '+', T.BKGND_NONE)
      T.console_put_char(self.con, x + 1, y - 1, '+', T.BKGND_NONE)
      T.console_put_char(self.con, x + 1, y + 1, '+', T.BKGND_NONE)

   def blit(self, console = 0):
      T.console_blit(self.con, 0, 0, self.width, self.height, console, self.x, self.y, 1.0, 0.0)

   
class Screen(object):
   def __init__(self, width, height, title):
      self.width = width
      self.height = height
      self.title = title
      self.frames = []

   def init_window(self):
      T.console_init_root(self.width, self.height, self.title, False)
      self.messages = MessageLog(0, 45, 55, 5)
      self.info = InfoFrame(0, 0, 80, 1)
      self.map = MapFrame(0, 1, 55, 44)
      self.stats = StatusFrame(55, 1, 25, 79)
      self.aux = AuxFrame(0, 0, 55, 45)
      self.curtain = AuxFrame(0, 0, 80, 50)
      self.targeting = TargetingFrame(0, 1, 55, 44)
      self.prompt = PromptFrame(0, 0, 80, 1)
      self.frames = [self.info, self.messages, self.map, self.stats]
                                           
   def add_message(self, text):
      self.messages.add_message(text)

   def add_info(self, text):
      self.info.add_message(text)

   def show_aux(self, text):
      self.aux.clear()
      self.aux.render(text)
      self.aux.blit()
      T.console_flush()

   def show_targeting(self, x, y):
      self.targeting.clear()
      self.targeting.render(x, y)
      self.map.blit()
      self.targeting.blit()
      T.console_flush()

   def show_curtain(self, text):
      self.curtain.clear()
      self.curtain.render(text)
      self.curtain.blit()
      T.console_flush()

   def show_prompt(self, prompt, options):
      self.prompt.clear()
      self.prompt.render(prompt, options)
      self.prompt.blit()
      T.console_flush()

   def render_and_update(self, map, player, items, npcs, current_level):
      [f.clear() for f in self.frames]

      self.map.render(map, items, npcs, player)
      self.stats.render(current_level, player)
      self.info.render()
      self.messages.render()
      
      [f.blit() for f in self.frames]
      
      self.info.wipe()
      T.console_flush()
      
class Targeter(object):
   def __init__(self, screen, player, npcs):
      self.screen = screen
      self.player = player
      self.npcs = npcs

   def get_target(self):
      if not self.npcs:
         return None

      target = (self.player.last_target if self.player.last_target else self.npcs[0])
      x = target.x
      y = target.y
      self.screen.show_targeting(x, y)

      while True:
         key = T.console_wait_for_keypress(True)

         if key.vk == T.KEY_ESCAPE:
            return False
         elif key.vk == T.KEY_ENTER or key.vk == T.KEY_KPENTER:
            for n in self.npcs:
               if n.x == x and n.y == y:
                  self.player.last_target = n
                  return n
            return None
         elif key.vk == T.KEY_UP or key.vk == T.KEY_KP8:
            y -= 1
         elif key.vk == T.KEY_DOWN or key.vk == T.KEY_KP2:
            y += 1
         elif key.vk == T.KEY_LEFT or key.vk == T.KEY_KP4:
            x -= 1
         elif key.vk == T.KEY_RIGHT or key.vk == T.KEY_KP6:
            x += 1
         elif key.vk == T.KEY_KP7:
            x -= 1
            y -= 1
         elif key.vk == T.KEY_KP9:
            x += 1
            y -= 1
         elif key.vk == T.KEY_KP1:
            x -= 1
            y += 1
         elif key.vk == T.KEY_KP3:
            x += 1
            y += 1

         self.screen.show_targeting(x, y)

class Prompter(object):
   def __init__(self, screen, prompt, options):
      self.screen = screen
      self.prompt = prompt
      self.options = options

   def get_option(self):
      self.screen.show_prompt(self.prompt, self.options)

      while True:
         key = T.console_wait_for_keypress(True)

         if key.vk == T.KEY_ESCAPE:
            return False
         elif key.vk == T.KEY_CHAR and key.c in self.options:
            return key.c
         elif key.vk in self.options:
            return key.vk


class Chooser(object):
   def __init__(self, screen, items):
      self.screen = screen
      self.items = items

   def get_choice(self, title = ''):
      if not self.items:
         return None

      rows = ([title, ''] if title else [])
      char = ord('a')

      for i in self.items:
         rows.append("%s - %s" % (chr(char), i.describe()))
         char += 1

      rows.append('')
      rows.append("ESC to abort")

      self.screen.show_aux("\n".join(rows))
      key = T.console_wait_for_keypress(True)

      if key.vk == T.KEY_ESCAPE:
         return False

      if key.c < ord('a') or key.c > (char - 1):
         self.screen.add_message("Invalid choice %s" % chr(key.c))
         return False

      return self.items[(key.c - ord('a'))]

class InfoShower(object):
   def __init__(self, screen, lines):
      self.screen = screen
      self.lines = lines

   def show(self, title = ''):
      rows = ([title, ''] if title else [])

      for line in self.lines:
         rows.append(line)

      rows.append('')
      rows.append("Press SPACE to continue")

      self.screen.show_aux("\n".join(rows))

      while True:
         key = T.console_wait_for_keypress(True)

         if key.vk == T.KEY_SPACE:
            return 
      

      



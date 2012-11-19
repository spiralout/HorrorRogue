#!/usr/bin/python

from screen import *
from game import *
from map import *
from config import *
from mapgen_office import *


def run():
   mg = MapGenerator(55, 44)
   m1 = mg.generate(55, 44)
   s = Screen(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)

   g = Game(s, [Map(55, 44, m1)], [])
   g.prepare()
   g.loop()

if __name__ == '__main__':
   run()




import libtcodpy as T
import pprint
#from guppy import hpy

SHOW_MEMORY = False
#HEAPY = hpy()
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MESSAGES_HEIGHT = 5
STATUS_WIDTH = 25
INFO_HEIGHT = 1
MESSAGES_WIDTH = SCREEN_WIDTH - STATUS_WIDTH
STATUS_HEIGHT = SCREEN_HEIGHT - MESSAGES_HEIGHT
MAP_WIDTH = SCREEN_WIDTH - STATUS_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT - MESSAGES_HEIGHT - INFO_HEIGHT
INFO_WIDTH = MAP_WIDTH
TITLE = 'Title'
FONT = 'terminal.png'
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 9
MAX_DARKNESS = 5
DARKNESS_CHANCE = 10
DARKNESS_SPEED = 6
TURN_COST = 24
ARROW_KEYS = [T.KEY_UP, T.KEY_DOWN, T.KEY_LEFT, T.KEY_RIGHT]
KEYPAD_KEYS = [T.KEY_KP8, T.KEY_KP9, T.KEY_KP6, T.KEY_KP3, T.KEY_KP2, T.KEY_KP1, T.KEY_KP4, T.KEY_KP7]
DIR_KEYS = ARROW_KEYS + KEYPAD_KEYS
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
HORIZONTAL = 0
VERTICAL = 1

pp = pprint.PrettyPrinter()

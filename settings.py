# GAME OPTIONS / SETTINGS

# DISPLAY
TITLE = "GRAVIT8"
WIDTH = 1600
HEIGHT = 900
FPS = 60
FONT_NAME = 'papyrus'
FUEL_BAR_LENGTH = 300  # Pixels
FUEL_BAR_HEIGHT = 20

# FILENAMES
HIGH_SCORE_FILE = 'highscore.txt'
PLAYER_FILE = 'p1_jump.png'
JUMP_SND_FILE = 'Jump3.wav'
JUMP_SECTOR_SND_FILE = 'jump_sector.wav'
CRASH_SND_FILE = 'crash2.wav'
MOON_CRASH_SND_FILE = 'moon_crash.wav'
PLAYER_CRASH_SND_FILE = 'player_crash.wav'
JETPACK_SND_FILE = 'jetpack_on.wav'
LEVEL_1_MUSIC = 'The last adventure game.mp3'
START_MUSIC = 'Underwater.mp3'
ARROW_FILE = 'ornamented_arrow.png'
SUN_FILE = 'sun-png-5467.png'

FUEL_FILE = 'tanks_barrelGreen.png'
START_SCREEN_FILE = 'redplanet_0.png'
BACKGROUND_FILE = 'starsBackground.png'

# GAME PROPERTIES
GRAVITATIONAL_CONSTANT = .1
MAX_FUEL = 3

# PLAYER PROPERTIES
PLAYER_ACC = 0.5
JETPACK_ACC = 0.1
START_FUEL = 30
FUEL_CONSUMPTION_RATE = .1
PLAYER_ANGULAR_ACC = 0.5  # Rotate while freeflying or around planet
PLAYER_FRICTION = -0.12
LAUNCH_FORCE = 3
JUMP_CUT_SPEED = 8

# PLANET PROPERTIES
PLANETS = 12
PLANET_START_VEL_LIMIT = 50
PLANET_MIN_SIZE = 50
PLANET_MAX_SIZE = 100
COLLISION_POST_COUNT_MAX = 2

# MOON PROPERTIES
MAX_MOONS = 3
MOON_START_VEL_LIMIT = 50
MOON_MIN_SIZE = 8
MOON_MAX_SIZE = 11

# LAYERS
PLAYER_LAYER = 6
MOON_LAYER = 5
ARROW_LAYER = 4
EXPLOSION_LAYER = 3
PLANET_LAYER = 2
SUN_LAYER = 1
BACKGROUND = 0

# DEFINE COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (0, 155, 155)
DARK_BLUE = (50, 80, 90)
BG_COLOR = DARK_BLUE

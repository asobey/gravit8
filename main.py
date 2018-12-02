#!python3
# GRAVIT8 - Physics Game

# --- ATTRIBUTIONS / CREDITS ---
# Music By: his work is licensed under the Creative Commons Namensnennung - Weitergabe unter gleichen Bedingungen 3.0
#   Unported License Author: sofamusik
# Sprites By: Kenney.nl
# Sounds Using: bfxr.net
# Planets By: Viktor.Hahn@web.de
# Background By: Bart K. https://opengameart.org/content/red-planet

# --- IMPORTS ---
import pygame as pg
from sprites import *
from os import path, environ
from random import choice, randrange


# noinspection PyArgumentList
class Game:
    def __init__(self):  # initialize game window, ect
        environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()  # initialize pygame
        pg.mixer.init()  # initialize sound
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # creates the display
        pg.display.set_caption(TITLE)  # sets the top caption
        self.clock = pg.time.Clock()  # to control FPS
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        """Load Data from files in source folder"""
        # Get Paths Setup
        self.dir = path.dirname(__file__)
        self.img_dir = path.join(self.dir, 'img')
        self.snd_dir = path.join(self.dir, 'snd')

        # Load High Score
        try:
            with open(path.join(self.dir, HIGH_SCORE_FILE), 'r') as f:
                self.highscore = int(f.read())
        except FileNotFoundError:
            self.highscore = 0

        # Load Images / Background
        self.player_image = pg.image.load(path.join(self.img_dir, PLAYER_FILE))
        self.planet_images = []
        for i in range(1, 11):
            self.planet_images.append(pg.image.load(path.join(self.img_dir, 'planets', 'p{}shaded.png'.format(i)))
                                      .convert())
        self.moon_images = []
        for i in range(1, 4):
            self.moon_images.append(pg.image.load(path.join(self.img_dir, 'moons', 'Moon{}.png'.format(i))).convert())

        self.fuel_image = pg.image.load(path.join(self.img_dir, 'pickups', FUEL_FILE)).convert()
        self.arrow_image = pg.image.load(path.join(self.img_dir, ARROW_FILE)).convert()
        self.background = pg.image.load(path.join(self.img_dir, BACKGROUND_FILE)).convert()
        self.background_rect = self.background.get_rect()
        print(f'BACKGROUND WIDTH, HEIGHT: {self.background_rect.width}, {self.background_rect.height}')
        self.loadscreen = pg.image.load(path.join(self.img_dir, START_SCREEN_FILE)).convert()
        self.loadscreen_rect = self.loadscreen.get_rect()

        # BUILDING EXPLOSION ANIMATIONS
        self.explosion_animation = {'lg': [], 'sm': [], 'tiny': [], 'player': []}
        for i in range(0, 9):
            filename = 'tank_explosion{}.png'.format(i)
            img = pg.image.load(path.join(self.img_dir, 'explosions', filename)).convert()
            img.set_colorkey(BLACK)
            img_lg = pg.transform.scale(img, (50, 50))
            self.explosion_animation['lg'].append(img_lg)
            img_sm = pg.transform.scale(img, (10, 10))
            self.explosion_animation['sm'].append(img_sm)
            img_tiny = pg.transform.scale(img, (6, 6))
            self.explosion_animation['tiny'].append(img_tiny)
            filename = 'sonicExplosion0{}.png'.format(i)
            img_pl = pg.image.load(path.join(self.img_dir, 'explosions', filename)).convert()
            img = pg.transform.scale(img_pl, (80, 80))
            self.explosion_animation['player'].append(img)

        # Load Sounds / Music
        self.crash_sound = pg.mixer.Sound(path.join(self.snd_dir, CRASH_SND_FILE))
        self.crash_sound.set_volume(.4)
        self.moon_crash_sound = pg.mixer.Sound(path.join(self.snd_dir, MOON_CRASH_SND_FILE))
        self.moon_crash_sound.set_volume(.03)
        self.player_crash_sound = pg.mixer.Sound(path.join(self.snd_dir, PLAYER_CRASH_SND_FILE))
        self.player_crash_sound.set_volume(.9)
        self.launch_sound = pg.mixer.Sound(path.join(self.snd_dir, JUMP_SND_FILE))
        self.launch_sound.set_volume(.8)
        self.jetpack_sound = pg.mixer.Sound(path.join(self.snd_dir, JETPACK_SND_FILE))
        self.jetpack_sound.set_volume(.3)

    def new(self):
        """New Game / Reset Game"""
        self.playing = True
        self.score = 0
        # GROUPS AND LAYERS
        self.all_sprites = pg.sprite.LayeredUpdates()  # Lets you assign layer to group to render in correct order
        self.planets = pg.sprite.Group()
        self.moons = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.stars = pg.sprite.Group()
        self.pickups = pg.sprite.Group()
        self.arrows = pg.sprite.Group()
        # SCREEN
        self.frame_coordinates = vec(0, 0)
        self.first_planet = Planet(self)  # Add 1st Planet
        self.player = Player(self, self.first_planet)  # Add Player on First Planet
        self.added_planets = 0
        self.spawn_planets(PLANETS + self.added_planets)
        self.arrow = Arrow(self)

        # Messages
        self.corner_msg = 'Traverse & Score!'
        self.corner_msg_flag = False
        self.corner_msg_start_time = pg.time.get_ticks()

        self.arrow_msg = False

        # Play Music
        pg.mixer.music.load(path.join(self.snd_dir, LEVEL_1_MUSIC))

        # Start Game Loop
        self.run()
        print("GOT TO END OF NEW()")

    def run(self):
        """ Game Loop """
        pg.mixer.music.play(loops=-1)
        self.start_level_screen('This sector in no longer stable...')
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        """ Game Loop - Updates """
        self.all_sprites.update()

    def events(self):  # game loop - events
        for event in pg.event.get():
            if event.type == pg.QUIT:  # check for closing the window
                self.running = False
                self.playing = False
                print('Thank you for playing!')
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.added_planets += 1
                    self.spawn_planets(1 + self.added_planets)
                    # self.player.jump()
                if event.key == pg.K_j:
                    self.jump()
                if event.key == pg.K_l:
                    self.playing = False
                if event.key == pg.K_ESCAPE:
                    self.running = False
                    self.playing = False
                    print('Thank you for playing!')
                if event.key == pg.K_n:
                    self.playing = False
                    print('==============')
                    print('---NEW GAME---')
                    print('==============')
            # if event.type == pg.KEYUP:
            #     if event.key == pg.K_SPACE:
            #         self.player.jump_cut ()

    # --- DRAW RENDER ---
    def draw(self):  # game loop - draw / render
        self.screen.fill(BG_COLOR)
        self.screen.blit(self.background, self.frame_coordinates)
        self.all_sprites.draw(self.screen)  # All sprites group takes care of layers
        self.draw_corner_msg()
        self.draw_arrow_msg()
        self.draw_text(f'Highscore: {self.highscore}', 20, WHITE, WIDTH / 2, 10)
        self.draw_text(self.score, 25, WHITE, WIDTH / 2, 30)
        self.draw_fuel_bar(self.screen, 5, 5, self.player.fuel_level)
        pg.display.flip()  # after everything is drawn, flip display

    def draw_text(self, text, size, color, x, y, font_name=FONT_NAME, alpha=255):
        font = pg.font.Font(pg.font.match_font(font_name), size)
        text_surface = font.render(str(text), True, color)
        text_surface.set_alpha(alpha)  # the alpha thing does not appear to be working
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_arrow_msg(self):
        if self.arrow_msg:
            self.draw_text(self.player.distance_from_center, 100, WHITE, WIDTH / 2, HEIGHT / 2 + 50)

    def draw_corner_msg(self):
        if self.corner_msg is not None:
            if self.corner_msg_flag is False:
                self.corner_msg_start_time = pg.time.get_ticks()
                self.corner_msg_flag = True
                self.red = 255
            else:
                if pg.time.get_ticks() - self.corner_msg_start_time < 2000:
                    self.draw_text(self.corner_msg, 35, (self.red, 0, 0), WIDTH - 220, 15)
                    if self.red > 0:
                        self.red -= 1.5
                else:
                    self.corner_msg = None
                    self.corner_msg_flag = False

    def draw_fuel_bar(self, surface, x, y, percent):
        if percent < 0:
            percent = 0
        fill = (percent / 150) * FUEL_BAR_LENGTH
        outline_rect = pg.Rect(x, y, FUEL_BAR_LENGTH, FUEL_BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, FUEL_BAR_HEIGHT)
        if percent > 100:
            pg.draw.rect(surface, GREEN, fill_rect)
        else:
            pg.draw.rect(surface, YELLOW, fill_rect)
        pg.draw.rect(surface, WHITE, outline_rect, 2)
        outline_rect2 = pg.Rect(x, y, 1/1.5 * FUEL_BAR_LENGTH, FUEL_BAR_HEIGHT)
        pg.draw.rect(surface, WHITE, outline_rect2, 2)
        self.draw_text('FUEL', 25, YELLOW, 20, 25, 'playbill')
        self.draw_text('TO JUMP', 25, GREEN, 235, 25, 'playbill')

    # def draw_lives(self, surface, x, y, lives, img):
    #     for i in range(lives):
    #         img_rect = img.get_rect()
    #         img_rect.x = x + 30 * i
    #         img_rect.y = y
    #         surface.blit(img, img_rect)

    def jump(self):
        pass

    def spawn_planets(self, n):  # This is used with spawn_planet so that
        while len(self.planets) < n:
            self.spawn_planet()

    def spawn_planet(self):
        new_planet = Planet(self)
        for planet in self.planets:
            if planet is not new_planet:
                if new_planet.pos.distance_to(planet.pos) < (new_planet.radius + planet.radius + 5):
                    for moon in new_planet.moons:
                        moon.kill()
                    for fuel in new_planet.fuels:
                        fuel.kill()
                    new_planet.kill()

    def show_start_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, START_MUSIC))
        pg.mixer.music.play(loops=-1)
        self.screen.blit(self.loadscreen, self.loadscreen_rect)
        self.draw_text("HIGH SCORE: " + str(self.highscore), 22, WHITE, WIDTH / 2, 30)
        self.draw_text(TITLE, 120, WHITE, WIDTH * 1 / 4, HEIGHT / 4)
        self.draw_text("[A] & [D] to Move/Rotate, [W] to launch, [Arrows] for Jetpack Control", 30, BLACK, WIDTH * 4 / 6, HEIGHT * 3 / 5)
        self.draw_text("Press any key to play...", 30, WHITE, WIDTH * 3 / 5, HEIGHT * 7/8)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def start_level_screen(self, message):
        self.screen.fill(BLACK)
        start_time = pg.time.get_ticks()
        color_alpha = 255
        while pg.time.get_ticks() - start_time < 1000:
            color = (int(color_alpha), int(color_alpha), int(color_alpha), int(color_alpha))
            self.draw_text(message, 48, color, WIDTH / 2, HEIGHT / 2 - 48)
            if color_alpha > 0:
                color_alpha -= .4
            pg.display.flip()
        return

    def show_game_over_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, START_MUSIC))
        pg.mixer.music.play(loops=-1)
        if self.running:
            self.screen.blit(self.loadscreen, self.loadscreen_rect)
            self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
            self.draw_text("Score: " + str(self.score), 22, BLACK, WIDTH / 2, HEIGHT / 2)
            self.draw_text("Press any key to play again...", 22, WHITE, WIDTH / 2, HEIGHT * 3/4)
            if self.score > self.highscore:
                self.highscore = self.score
                self.draw_text("NEW HIGH SCORE!", 30, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
                with open(path.join(self.dir, HIGH_SCORE_FILE), 'w') as f:
                    f.write(str(self.score))
            else:
                self.draw_text("HIGH SCORE: " + str(self.highscore), 25, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            pg.display.flip()
            self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False


if __name__ == '__main__':
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new()
        g.show_game_over_screen()
    pg.quit()

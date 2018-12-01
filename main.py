#!python3
#GRAVIT8 - Physics game

# --- ATTRIBUTIONS / CREDITS ---
# Music By: his work is licensed under the Creative Commons Namensnennung - Weitergabe unter gleichen Bedingungen 3.0 Unported License Author: sofamusik
# Sprites By: Kenney.nl
# Sounds Using: bfxr.net
# Planets By: Viktor.Hahn@web.de

# --- IMPORTS ---
import pygame as pg
from settings import *
from sprites import *
from os import path
from random import choice, randrange
import time


class Game:
    def __init__(self):  # initialize game window, ect
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
            self.planet_images.append(pg.image.load(path.join(self.img_dir, 'planets', 'p{}shaded.png'.format(i))).convert())
        self.moon_images = []
        for i in range(1, 4):
            self.moon_images.append(pg.image.load(path.join(self.img_dir, 'moons', 'Moon{}.png'.format(i))).convert())
        self.background = pg.image.load(path.join(self.img_dir, "starsBackground.png")).convert()
        self.background_rect = self.background.get_rect()

        # BUILDING EXPLOSION ANIMATIONS
        self.explosion_animation = {}
        self.explosion_animation['lg'] = []
        self.explosion_animation['sm'] = []
        self.explosion_animation['player'] = []
        for i in range(0, 9):
            filename = 'tank_explosion{}.png'.format(i)
            img = pg.image.load(path.join(self.img_dir, 'explosions', filename)).convert()
            img.set_colorkey(BLACK)
            img_lg = pg.transform.scale(img, (50, 50))
            self.explosion_animation['lg'].append(img_lg)
            img_sm = pg.transform.scale(img, (10, 10))
            self.explosion_animation['sm'].append(img_sm)
            filename = 'sonicExplosion0{}.png'.format(i)
            img = pg.image.load(path.join(self.img_dir, 'explosions', filename)).convert()
            self.explosion_animation['player'].append(img)

        # Load Sounds / Music
        self.crash_sound = pg.mixer.Sound(path.join(self.snd_dir, CRASH_SND_FILE))
        self.crash_sound.set_volume(.4)
        self.moon_crash_sound = pg.mixer.Sound(path.join(self.snd_dir, MOON_CRASH_SND_FILE))
        self.moon_crash_sound.set_volume(.03)
        self.launch_sound = pg.mixer.Sound(path.join(self.snd_dir, JUMP_SND_FILE))
        self.launch_sound.set_volume(1)

    def new(self):
        """New Game / Reset Game"""
        self.playing = True
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()  # Lets you assign layer to group to render in correct order
        self.planets = pg.sprite.Group()
        self.moons = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.stars = pg.sprite.Group()

        self.first_planet = Planet(self)  # Add 1st Planet
        self.player = Player(self, self.first_planet) # Add Player on First Planet
        self.added_planets = 0

        # TODO: self.something_timer = 0
        # Play Music
        pg.mixer.music.load(path.join(self.snd_dir, START_MUSIC))

        # Start Game Loop
        self.run()

    def run(self):
        """ Game Loop """
        pg.mixer.music.play(loops=-1)
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
                    self.spawn_planets(PLANETS + self.added_planets)
                    # self.player.jump()
                if event.key == pg.K_m:
                    Moon(self)
                if event.key == pg.K_ESCAPE:
                    self.running = False
                    self.playing = False
                    print('Thank you for playing!')
                if event.key == pg.K_n:
                    self.playing = False
            # if event.type == pg.KEYUP:
            #     if event.key == pg.K_SPACE:
            #         self.player.jump_cut ()

    def draw(self):  # game loop - draw / render
        self.screen.fill(BG_COLOR)
        self.screen.blit(self.background, self.background_rect)
        self.all_sprites.draw(self.screen)  # All sprites group takes care of layers
        self.draw_text(self.score, 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()  # after everything is drawn, flip display

    def show_start_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, LEVEL_1_MUSIC))
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BG_COLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows (or W-A-S-D) to move & Spacebar to Jump", 22, BLACK, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to play...", 22, WHITE, WIDTH / 2, HEIGHT * 3/4)
        self.draw_text("HIGH SCORE: " + str(self.highscore), 18, BLACK, WIDTH / 2, 5)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_game_over_screen(self):
        if self.running:
            self.screen.fill(BG_COLOR)
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

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def spawn_planets(self, n):
        while len(self.planets) < n:
            self.spawn_planet()

    def spawn_planet(self):
        new_planet = Planet(self)
        for planet in self.planets:
            if planet is not new_planet:
                if new_planet.pos.distance_to(planet.pos) < (new_planet.radius + planet.radius + 5):
                    for moon in new_planet.moons:
                        moon.kill()
                    new_planet.kill()



if __name__ == '__main__':
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new()
        g.show_game_over_screen()
    pg.quit()

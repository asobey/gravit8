#!python3
# Sprite Classes for GRAVIT8

# --- IMPORTS ---
import pygame as pg
from settings import *
from random import choice, randrange
vec = pg.math.Vector2

# --- CLASSES ---
class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((50, 40))
        self.image = self.game.player_image  # scale image b/c original is too big
        self.image.set_colorkey(BLACK)  # This removes the black image outline and makes it background
        self.rect = self.image.get_rect()
        self.scale = 2
        self.image = pg.transform.scale(self.image, (int(self.rect.width / self.scale), int(self.rect.height / self.scale)))
        self.rect = self.image.get_rect()
        self.radius = 20
        pg.draw.circle(self.image, RED, self.rect.center, self.radius, 2)  # Used to see collision circle
        # Start Position / Speed
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def update(self):
        self.speedx = 0  # to keep from having to start and stop sprite, make default 0 speed unless key pressed
        keystate = pg.key.get_pressed()
        if keystate[pg.K_LEFT]:
            self.speedx = -5
        if keystate[pg.K_RIGHT]:
            self.speedx = 5
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0


class Planet(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLANET_LAYER
        self.groups = game.all_sprites, game.planets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.planet_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = randrange(25, 101) / 50
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        self.rect = self.image.get_rect()
        self.rect.x = randrange(0 + int(self.rect.width / 2), WIDTH - int(self.rect.width / 2))
        self.rect.y = randrange(0 + int(self.rect.height / 2), int(HEIGHT - self.rect.height / 2))
        self.radius = self.rect.width / 2
        self.pos = vec(self.rect.x, self.rect.y)
        self.vel = vec(randrange(-3, 3), randrange(-3, 3))
        self.acc = vec(0, 0)

    def update(self):
        self.wall_check()
        self.planet_collision()
        self.pos += self.vel + 0.5 * self.acc
        self.rect.center = self.pos

    def wall_check(self):
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.vel.x *= -1
        if self.rect.bottom > HEIGHT or self.rect.top < 0:
            self.vel.y *= -1

    def planet_collision(self):
        for planet in self.game.planets:
            print(planet.__repr__)
            # if planet.__repr__ not self.__repr__:
            #     # if ((self.pos.x-planet.pos.x)**2 + (self.pos.y-planet.pos.y)**2)**.5 < (self.radius + planet.radius):
            #     if self.pos.distance_to(planet.pos) < (self.radius + planet.radius):
            #         print('COLLIDE!')

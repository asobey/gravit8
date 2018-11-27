#!python3
# Sprite Classes for GRAVIT8

# --- IMPORTS ---
import pygame as pg
vec = pg.math.Vector2
from settings import *
from random import choice, randrange


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
        scale = randrange(PLANET_MIN_SIZE, PLANET_MAX_SIZE + 1) / 50
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        self.rect = self.image.get_rect()
        self.rect.x = randrange(0 + int(self.rect.width / 2), WIDTH - int(self.rect.width / 2))
        self.rect.y = randrange(0 + int(self.rect.height / 2), int(HEIGHT - self.rect.height / 2))
        self.radius = self.rect.width / 2
        self.mass = self.radius ** 2
        self.pos = vec(self.rect.x, self.rect.y)
        self.vel = vec(randrange(-PLANET_START_VEL_LIMIT, PLANET_START_VEL_LIMIT)/50,\
                       randrange(-PLANET_START_VEL_LIMIT, PLANET_START_VEL_LIMIT)/50)
        self.acc = vec(0, 0)
        self.collision_post_count = 0
        self.moons = pg.sprite.Group()
        self.spawn_moons()

    def spawn_moons(self):
        last_orbital_radius = self.radius
        for i in range(randrange(MAX_MOONS) + 1):
            orbital_radius = last_orbital_radius + randrange(10, 15)
            new_moon = Moon(self, orbital_radius)
            self.moons.add(new_moon)
            last_orbital_radius = orbital_radius

    def update(self):
        self.pos += self.vel + 0.5 * self.acc
        self.rect.center = self.pos
        if self.collision_post_count is not 0:
            if self.collision_post_count is COLLISION_POST_COUNT_MAX:
                self.collision_post_count = 0
            else:
                self.collision_post_count += 1
        self.wall_check()
        self.planet_collision()
        for moon in self.moons:
            moon.update()
        #     moon.update_fix_lost_planet(self.pos)

    def wall_check(self):
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.vel.x *= -1
        if self.rect.bottom > HEIGHT or self.rect.top < 0:
            self.vel.y *= -1

    def planet_collision(self):
        for planet in self.game.planets:
            if planet is not self and (self.collision_post_count is 0 or planet.collision_post_count is 0):
                if self.pos.distance_to(planet.pos) < (self.radius + planet.radius):
                    self.game.crash_sound.play()
                    pos_explosion = self.collision_point(self.pos, planet.pos, self.radius, planet.radius)
                    Explosion(self.game, pos_explosion, 'lg')
                    self.vel, planet.vel = self.collision_new_vel(self.vel, planet.vel, self.mass, planet.mass)
                    self.collision_post_count += 1
                    planet.collision_post_count += 1

    @staticmethod
    def collision_point(pos_a, pos_b, radius_a, radius_b):
        collision_point_x = ((pos_a.x * radius_b) + (pos_b.x * radius_a)) / (radius_a + radius_b);
        collision_point_y = ((pos_a.y * radius_b) + (pos_b.y * radius_a)) / (radius_a + radius_b);
        return vec(collision_point_x, collision_point_y)

    @staticmethod
    def collision_new_vel(vel_a, vel_b, mass_a, mass_b):
        new_vel_a_x = (vel_a.x * (mass_a - mass_b) + 2 * mass_b * vel_b.x) / (mass_a + mass_b)
        new_vel_a_y = (vel_a.y * (mass_a - mass_b) + 2 * mass_b * vel_b.y) / (mass_a + mass_b)
        new_vel_b_x = (vel_b.x * (mass_b - mass_a) + 2 * mass_a * vel_a.x) / (mass_a + mass_b)
        new_vel_b_y = (vel_b.y * (mass_b - mass_a) + 2 * mass_a * vel_a.y) / (mass_a + mass_b)
        return vec(new_vel_a_x, new_vel_a_y), vec(new_vel_b_x, new_vel_b_y)


class Moon(pg.sprite.Sprite):
    def __init__(self, planet, orbit_radius):
        self._layer = MOON_LAYER
        self.planet = planet
        self.game = planet.game
        self.groups = self.game.moons, self.game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = choice(self.game.moon_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = randrange(MOON_MIN_SIZE, MOON_MAX_SIZE + 1) / 50
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2
        self.mass = self.radius ** 2

        self.angle = randrange(360)
        self.orbital_radius = orbit_radius

        self.pos_from_planet = vec()
        self.pos_from_planet.from_polar((self.orbital_radius, self.angle))
        self.pos = vec(self.planet.pos + self.pos_from_planet)
        self.vel = randrange(-MOON_START_VEL_LIMIT, MOON_START_VEL_LIMIT) / 50

    def update(self):
        self.angle += self.vel
        self.pos_from_planet.from_polar((self.orbital_radius, self.angle))
        self.pos = vec(self.planet.pos + self.pos_from_planet)
        self.rect.center = self.pos
        self.planet_collision()

    # def update_fix_lost_planet(self, planet_pos):
    #     self.planet.pos = planet_pos

    def planet_collision(self):
        for planet in self.game.planets:
            if self.pos.distance_to(planet.pos) < (self.radius + planet.radius):
                self.game.crash_sound.play()
                pos_explosion = self.collision_point(self.pos, planet.pos, self.radius, planet.radius)
                Explosion(self.game, pos_explosion, 'sm')
                #self.vel, planet.vel = self.collision_new_vel(self.vel, planet.vel, self.mass, planet.mass)
                # Change to have new planet steel moon

    @staticmethod
    def collision_point(pos_a, pos_b, radius_a, radius_b):
        collision_point_x = ((pos_a.x * radius_b) + (pos_b.x * radius_a)) / (radius_a + radius_b);
        collision_point_y = ((pos_a.y * radius_b) + (pos_b.y * radius_a)) / (radius_a + radius_b);
        return vec(collision_point_x, collision_point_y)


class Explosion(pg.sprite.Sprite):
    def __init__(self, game, center, size):
        self._layer = EXPLOSION_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.size = size
        self.image = self.game.explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 25

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.explosion_animation[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.game.explosion_animation[self.size][self.frame]
                self.rect.center = center

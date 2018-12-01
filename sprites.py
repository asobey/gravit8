#!python3
# Sprite Classes for GRAVIT8

# --- IMPORTS ---
import pygame as pg
vec = pg.math.Vector2
from math import cos, sin, atan, radians
from settings import *
from random import choice, randrange


# --- CLASSES ---
class Player(pg.sprite.Sprite):
    def __init__(self, game, on_planet):
        self._layer = PLAYER_LAYER
        pg.sprite.Sprite.__init__(self, game.all_sprites)
        self.game = game
        self.image = self.game.player_image  # scale image b/c original is too big
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)  # This removes the black image outline and makes it background
        self.scale = 1/4
        self.image = pg.transform.scale(self.image, (int(self.rect.width * self.scale), int(self.rect.height *
                                                                                            self.scale)))
        self.image_original = self.image  # need so that you do not ruin image over time
        self.image_original.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        pg.draw.circle(self.image, RED, self.rect.center, self.radius, 2)  # Used to see collision circle
        # Start Position / Speed
        self.pos = vec()
        self.on_planet = on_planet
        self.angle = -90  # puts player at top of planet
        self.image_angle = (self.angle + 90) % 360  # player image standing straight up
        self.pos_from_planet = vec()
        self.pos_from_planet.from_polar((self.on_planet.radius, self.angle))
        self.pos = vec(self.on_planet.pos + self.pos_from_planet)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def update(self):
        if self.on_planet is not None:
            keys = pg.key.get_pressed()
            if keys[pg.K_w]:  # LAUNCH OFF PLANET
                self.mobility_launch()
            else:
                self.mobility_on_planet()

        else:
            self.mobility_freeflier()

    def mobility_on_planet(self):
        #print('On Planet!')  # todo: keep until figured jump
        # LOOK FOR KEYS
        self.acc.x = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            print('-----left')
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            print('-----right!')
            self.acc.x = PLAYER_ACC
        # APPLY FRICTION
        self.acc.x += self.vel.x * PLAYER_FRICTION  # applies friction to the player
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:  # otherwise vel.x never returns to '0', just gets infinitesimally small
            self.vel.x = 0
        self.angle += self.vel.x + 0.5 * self.acc.x
        self.pos_from_planet.from_polar((self.on_planet.radius + self.rect.height / 4, self.angle))
        self.pos = vec(self.on_planet.pos + self.pos_from_planet)
        self.rect.center = self.pos

        if self.vel.x != 0:
            self.image_angle = -(self.angle + 90) % 360
            self.image, self.rect = rotate_image_about_center(self.image_original, self.rect, self.image_angle)

    def mobility_freeflier(self):
        self.apply_gravity_field()
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        print('self.acc = ', self.acc)
        print('self.vel = ', self.vel)
        print('self.pos = ', self.pos)
        self.rect.center = self.pos


    def mobility_launch(self):
        """Launch from planet"""
        self.game.launch_sound.play()
        self.vel.y = -LAUNCH_FORCE + self.on_planet.vel.y  # Launch Power / Velocity
        self.on_planet = None

    def twist_in_space(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            print('-----twist counter')
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            print('-----twist clockwise!')


    def apply_gravity_field(self):
        self.acc = vec(0, 0)
        for planet in self.game.planets:
            if self.pos.distance_to(planet.pos) > planet.radius: # No gravity inside the radius of the planet. todo: might not need at end
                try:
                    acc_magnitude = GRAVITATIONAL_CONSTANT * planet.mass / (self.pos.distance_to(planet.pos) ** 2)
                except ZeroDivisionError:
                    acc_magnitude = 0
                up = vec(0, 1)
                planet_to_player_angle = up.angle_to(self.pos - planet.pos)
                self.acc.y += acc_magnitude * -cos(radians(planet_to_player_angle))
                self.acc.x += acc_magnitude * sin(radians(planet_to_player_angle))


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
        if len(self.game.planets) < 2:  # This is only true for first planet with player start in bottom left
            self.rect.x = randrange(0 + int(self.rect.width / 2), WIDTH // 3 - int(self.rect.width / 2))
            self.rect.y = randrange(0 + int(self.rect.height / 2 + HEIGHT * 2 // 3), int(HEIGHT - self.rect.height / 2))
            self.vel = vec(randrange(-PLANET_START_VEL_LIMIT, PLANET_START_VEL_LIMIT) // 500,
                           randrange(-PLANET_START_VEL_LIMIT, PLANET_START_VEL_LIMIT) // 500)
        else:
            self.rect.x = randrange(0 + int(self.rect.width / 2), WIDTH - int(self.rect.width / 2))
            self.rect.y = randrange(0 + int(self.rect.height / 2), int(HEIGHT - self.rect.height / 2))
            self.vel = vec(randrange(-PLANET_START_VEL_LIMIT, PLANET_START_VEL_LIMIT) // 50,
                           randrange(-PLANET_START_VEL_LIMIT, PLANET_START_VEL_LIMIT) // 50)
        self.radius = self.rect.width / 2
        self.mass = self.radius ** 2
        self.pos = vec(self.rect.x, self.rect.y)
        self.pos_last = self.pos
        self.acc = vec(0, 0)
        self.collision_flag = False
        self.collision_post_count = 0
        self.moons = pg.sprite.Group()
        self.spawn_moons()

    def spawn_moons(self):
        last_orbital_radius = self.radius + 5
        self.moons = pg.sprite.Group()  # create moon group at the planet level
        for _ in range(randrange(MAX_MOONS + 1)):
            orbital_radius = last_orbital_radius + randrange(10, 15)
            new_moon = Moon(self, orbital_radius)  # todo: combine two lines
            self.moons.add(new_moon)  # with this line
            last_orbital_radius = orbital_radius
        self.game.all_sprites.add(self.moons)

    def update(self):
        self.pos_last = self.pos
        self.pos += self.vel + 0.5 * self.acc
        self.rect.center = self.pos
        self.wall_bounce()
        if not self.collision_flag:  # if collision already handled by previous planet, then ignore
            self.planet_collision_check()
        self.collision_flag = False

    def wall_bounce(self):
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.vel.x *= -1
        if self.rect.bottom > HEIGHT or self.rect.top < 0:
            self.vel.y *= -1

    def planet_collision_check(self):
        for planet in self.game.planets:
            if planet is not self:  # and (self.collision_post_count is 0 or planet.collision_post_count is 0):
                if self.pos.distance_to(planet.pos) < (self.radius + planet.radius):
                    print(self.pos.distance_to(planet.pos))
                    self.game.crash_sound.play()
                    pos_explosion = collision_point(self.pos, planet.pos, self.radius, planet.radius)
                    Explosion(self.game, pos_explosion, 'lg')
                    self.pos, planet.pos = self.pos_last, planet.pos_last
                    self.vel, planet.vel = collision_new_velocity(self.vel, planet.vel, self.mass, planet.mass)
                    planet.collision_flag = True  # flag to skip 2nd planet collision check


class Moon(pg.sprite.Sprite):
    def __init__(self, planet, orbit_radius):
        self._layer = MOON_LAYER
        self.planet = planet
        self.game = planet.game
        self.groups = self.game.all_sprites, self.game.moons
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

    def planet_collision(self):
        for planet in self.game.planets:
            if self.pos.distance_to(planet.pos) < (self.radius + planet.radius):
                self.game.moon_crash_sound.play()
                pos_explosion = collision_point(self.pos, planet.pos, self.radius, planet.radius)
                Explosion(self.game, pos_explosion, 'sm')
                # ToDo: Change to have new planet steel moon


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


# SPRITE FUNCTIONS
def collision_point(pos_a, pos_b, radius_a, radius_b):
    collision_point_x = ((pos_a.x * radius_b) + (pos_b.x * radius_a)) / (radius_a + radius_b)
    collision_point_y = ((pos_a.y * radius_b) + (pos_b.y * radius_a)) / (radius_a + radius_b)
    return vec(collision_point_x, collision_point_y)


def collision_new_velocity(vel_a, vel_b, mass_a, mass_b):
    new_vel_a_x = (vel_a.x * (mass_a - mass_b) + 2 * mass_b * vel_b.x) / (mass_a + mass_b)
    new_vel_a_y = (vel_a.y * (mass_a - mass_b) + 2 * mass_b * vel_b.y) / (mass_a + mass_b)
    new_vel_b_x = (vel_b.x * (mass_b - mass_a) + 2 * mass_a * vel_a.x) / (mass_a + mass_b)
    new_vel_b_y = (vel_b.y * (mass_b - mass_a) + 2 * mass_a * vel_a.y) / (mass_a + mass_b)
    return vec(new_vel_a_x, new_vel_a_y), vec(new_vel_b_x, new_vel_b_y)


def rotate_image_about_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rotated_image = pg.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=rect.center)
    return rotated_image, rotated_rect

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
        self.radius = 8
        # pg.draw.circle(self.image, RED, self.rect.center, self.radius, 2)
        self.center = vec(WIDTH / 2, HEIGHT / 2)
        self.up = vec(0, 1)
        # Start Position / Speed
        self.pos = vec()
        self.on_planet = on_planet
        self.last_planet = on_planet
        self.angle = -90  # puts player at top of planet
        self.image_angle = (self.angle + 90) % 360  # player image standing straight up
        self.pos_from_planet = vec()
        self.pos_from_planet.from_polar((self.on_planet.radius, self.angle))
        self.pos = vec(self.on_planet.pos + self.pos_from_planet)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        # Angular properties used on the planet
        self.ang_vel = vec(0, 0)
        self.ang_acc = vec(0, 0)

        self.distance_from_center = int(abs(self.center.distance_to(self.pos)))


        self.fuel_level = 1

    def update(self):
        self.moon_collision_check()
        self.pickups_collision_check()
        if self.on_planet is not None:
            keys = pg.key.get_pressed()
            if keys[pg.K_w]:  # LAUNCH OFF PLANET
                self.mobility_launch()
            else:
                self.mobility_on_planet()
        else:
            self.mobility_freeflier()
        # self.arrow_check()

    # def arrow_check(self):
    #     self.distance_from_center = int(abs(self.center.distance_to(self.pos)))
    #     if self.distance_from_center > (HEIGHT ** 2 + WIDTH ** 2) ** 0.5 / 2:
    #         if len(self.game.arrows) == 0:
    #             Arrow(self.game, self)
    #             self.game.arrow_msg = self.distance_from_center
    #     else:
    #         Arrow.kill(self.game.arrows)
    #         self.game.arrow_msg = None


    def mobility_on_planet(self):
        self.angular_mobility()
        self.pos_from_planet.from_polar((self.on_planet.radius + self.rect.height / 3, self.angle))
        self.pos = vec(self.on_planet.pos + self.pos_from_planet)
        self.rect.center = self.pos
        self.on_planet_planet_collision_check()
        # todo: Add self.vel to this method so player can do a run and jump

    def on_planet_planet_collision_check(self):
        for planet in self.game.planets:
            if planet is not self.on_planet:
                if pg.sprite.collide_circle(self, planet):
                    self.game.player_crash_sound.play()
                    Explosion(self.game, self.rect.center, 'player')
                    self.game.score -= 100
                    self.game.corner_msg = 'Smashed by Planet: -1000'

    def angular_mobility(self):
        self.ang_acc.x = 0  # must clear acceleration every frame
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.ang_acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.ang_acc.x = PLAYER_ACC
        # APPLY FRICTION
        self.ang_acc.x += self.ang_vel.x * PLAYER_FRICTION  # applies friction to the player
        self.ang_vel += self.ang_acc
        if abs(self.ang_vel.x) < 0.1:  # otherwise vel.x never returns to '0', just gets infinitesimally small
            self.ang_vel.x = 0
        self.angle += self.ang_vel.x + 0.5 * self.ang_acc.x
        self.image_angle = -(self.angle + 90) % 360
        self.image, self.rect = rotate_image_about_center(self.image_original, self.rect, self.image_angle)

    def mobility_freeflier(self):
        self.angular_mobility()
        self.apply_gravity_field()
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.center = self.pos
        self.landing_and_crash_check()

    def landing_and_crash_check(self):
        for planet in self.game.planets:
            if pg.sprite.collide_circle(self, planet):
                if self.image_angle < 45 or self.image_angle > 315:
                    head_location = self.rect.midtop
                elif 45 < self.image_angle < 135:
                    head_location = self.rect.midleft
                elif 135 < self.image_angle < 225:
                    head_location = self.rect.midbottom
                else: head_location = self.rect.midright
                if not planet.pos.distance_to(head_location) <= planet.radius:
                    self.on_planet = planet
                    self.place_on_planet_surface(self.on_planet)
                    if self.on_planet is self.last_planet:
                        self.game.corner_msg = 'Returning to Surface: 0'
                    else:
                        self.game.score += 500
                        self.game.corner_msg = 'Nice Landing: +500'
                else:  # planet.pos.distance_to(self.rect.midtop) <= planet.radius: #or \
                        # planet.pos.distance_to(self.rect.topright) <= planet.radius or \
                        # planet.pos.distance_to(self.rect.topleft) <= planet.radius:
                    self.game.score -= 500
                    self.game.corner_msg = 'Crash Landing: -500'
                    self.on_planet = planet  # todo: remove later, here to keep from dozens of crash landings
                    self.place_on_planet_surface(self.on_planet)

    def place_on_planet_surface(self, arrival_planet):
        self.angle = self.up.angle_to(self.pos - arrival_planet.pos) + 90
        self.pos_from_planet.from_polar((arrival_planet.radius + self.rect.height / 3, self.angle))
        self.pos = vec(arrival_planet.pos + self.pos_from_planet)

    def mobility_launch(self):
        """Launch from planet"""
        self.game.launch_sound.play()
        planet_to_player_angle = self.up.angle_to(self.pos - self.on_planet.pos)
        self.vel.x = LAUNCH_FORCE * -sin(radians(planet_to_player_angle)) + self.on_planet.vel.x  # Launch Power / Velocity
        self.vel.y = LAUNCH_FORCE * cos(radians(planet_to_player_angle)) + self.on_planet.vel.y
        self.last_planet = self.on_planet
        self.on_planet = None

    def apply_gravity_field(self):
        self.acc = vec(0, 0)
        for planet in self.game.planets:
            if self.pos.distance_to(planet.pos) > planet.radius + 1: # No gravity inside the radius of the planet. todo: might not need at end
                try:
                    acc_magnitude = GRAVITATIONAL_CONSTANT * planet.mass / (self.pos.distance_to(planet.pos) ** 2)
                except ZeroDivisionError:
                    acc_magnitude = 0
                up = vec(0, 1)
                planet_to_player_angle = up.angle_to(self.pos - planet.pos)
                self.acc.y += acc_magnitude * -cos(radians(planet_to_player_angle))
                self.acc.x += acc_magnitude * sin(radians(planet_to_player_angle))

    def moon_collision_check(self):
        if pg.sprite.spritecollide(self, self.game.moons, True, pg.sprite.collide_circle):
            self.game.player_crash_sound.play()
            Explosion(self.game, self.rect.center, 'player')
            self.game.score -= 200
            self.game.corner_msg = 'Moon to the face: -200'

    def pickups_collision_check(self):
        if pg.sprite.spritecollide(self, self.game.pickups, True, pg.sprite.collide_circle):
            self.game.player.fuel_level += randrange(4, 9)
            self.game.score += 200
            self.game.corner_msg = 'Fuel Pickup: +200'
            if self.game.player.fuel_level > 150:
                self.game.player.fuel_level = 150


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
        self.spawn_fuel()

    def spawn_moons(self):
        last_orbital_radius = self.radius + 12
        self.moons = pg.sprite.Group()  # create moon group at the planet level
        for _ in range(randrange(MAX_MOONS + 1)):
            orbital_radius = last_orbital_radius + randrange(10, 15)
            new_moon = Moon(self, orbital_radius)  # todo: combine two lines
            self.moons.add(new_moon)  # with this line
            last_orbital_radius = orbital_radius

    def spawn_fuel(self):
        for _ in range(randrange(MAX_FUEL + 1)):
            new_fuel = Fuel(self)
            self.game.pickups.add(new_fuel)


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
        self.collision_check()

    def collision_check(self):
        for planet in self.game.planets:
            if self.pos.distance_to(planet.pos) < (self.radius + planet.radius):
                self.game.moon_crash_sound.play()
                # pos_explosion = collision_point(self.pos, planet.pos, self.radius, planet.radius)
                Explosion(self.game, self.pos, 'sm')
                # ToDo: Change to have new planet steel moon


class Fuel(pg.sprite.Sprite):
    def __init__(self, planet):
        self.up = vec(0, 1)
        self._layer = MOON_LAYER # good for fuel too
        self.planet = planet
        self.game = planet.game
        self.groups = self.game.all_sprites, self.game.pickups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = self.game.fuel_image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = .2
        self.image = pg.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        self.image_original = self.image
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2

        self.angle = randrange(360)
        self.image_angle = -(self.angle + 90) % 360

        self.pos_from_planet = vec()
        self.pos_from_planet.from_polar((self.planet.radius, self.angle))
        self.pos = vec(self.planet.pos + self.pos_from_planet)
        self.rect.center = self.pos

    def update(self):
        self.pos = vec(self.planet.pos + self.pos_from_planet)
        self.rect.center = self.pos
        self.angle = self.up.angle_to(self.pos - self.planet.pos) + 90
        self.image_angle = -(self.angle + 90) % 360
        self.image, self.rect = rotate_image_about_center(self.image_original, self.rect, self.image_angle)


# class Arrow(pg.sprite.Sprite):
#     def __init__(self, game, player):
#         self.game = game
#         self.player = player
#         self.up = vec(0, 1)
#         self.center = vec(WIDTH / 2, HEIGHT / 2)
#         self._layer = ARROW_LAYER # good for fuel too
#         self.groups = self.game.all_sprites, self.game.arrows
#         pg.sprite.Sprite.__init__(self, self.groups)
#         self.image = self.game.arrow_image
#         self.image.set_colorkey(BLACK)
#         self.rect = self.image.get_rect()
#         scale = .5
#         self.image = pg.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
#         self.image_original = self.image
#         self.rect = self.image.get_rect()
#         self.circle_radius = 400
#
#         self.angle = self.up.angle_to(self.player.pos - self.center) + 90
#         self.image_angle = -(self.angle + 90) % 360
#
#         self.pos_from_center = vec()
#         self.pos_from_center.from_polar((self.circle_radius, self.angle))
#         self.pos = vec(self.center + self.pos_from_center)
#         self.rect.center = self.pos
#
#     def update(self):
#         self.rect.center = self.pos
#         self.angle = self.up.angle_to(self.game.player.pos - self.center) + 90
#         self.image_angle = -(self.angle + 90) % 360
#         self.pos_from_center.from_polar((self.circle_radius, self.angle))
#         self.pos = vec(self.center + self.pos_from_center)
#         self.rect.center = self.pos
#         self.image, self.rect = rotate_image_about_center(self.image_original, self.rect, self.image_angle)
#

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

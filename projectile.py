import pygame
from settings import PLAYER_SHURIKEN_VELOCITY_X, PLAYER_SHURIKEN_WIDTH, PLAYER_SHURIKEN_HEIGHT, INFANTRYMAN_BULLET_WIDTH, INFANTRYMAN_BULLET_HEIGHT, INFANTRYMAN_BULLET_VELOCITY_X, INFANTRYMAN_BULLET_VELOCITY_Y, INFANTRYMAN_BULLET_WIDTH2, INFANTRYMAN_BULLET_HEIGHT2, WEB_WIDTH, WEB_HEIGHT
from images import player_image_shuriken, enemy_image_bullet, enemy_image_bullet2, spider_web_image
class Shuriken(pygame.Rect):
        def __init__(self, player):
            if player.direction == "left":
                x = player.x
                velocity = -PLAYER_SHURIKEN_VELOCITY_X
            else:
                x = player.right
                velocity = PLAYER_SHURIKEN_VELOCITY_X

            y = player.y + player.height // 2

            super().__init__(
                x,
                y,
                PLAYER_SHURIKEN_WIDTH,
                PLAYER_SHURIKEN_HEIGHT
            )

            self.velocity_x = velocity
            self.image = player_image_shuriken
            self.used = False
                
class Bullet(pygame.Rect):
    def __init__(self, enemy, velocity_y):
            if enemy.direction == "left":
                x = enemy.x
                velocity = -INFANTRYMAN_BULLET_VELOCITY_X
            else:
                x = enemy.right
                velocity = INFANTRYMAN_BULLET_VELOCITY_X

            y = enemy.y + enemy.height // 4

            super().__init__(
                x,
                y,
                INFANTRYMAN_BULLET_WIDTH,
                INFANTRYMAN_BULLET_HEIGHT
            )

            self.velocity_x = velocity
            self.velocity_y = velocity_y
            self.image = enemy_image_bullet
            self.used = False

class Bullet2(pygame.Rect):
    def __init__(self, enemy):
            if enemy.direction == "left":
                x = enemy.x
                velocity = -INFANTRYMAN_BULLET_VELOCITY_X
            else:
                x = enemy.right
                velocity = INFANTRYMAN_BULLET_VELOCITY_X

            y = enemy.y + enemy.height // 4

            super().__init__(
                x,
                y,
                INFANTRYMAN_BULLET_WIDTH2,
                INFANTRYMAN_BULLET_HEIGHT2
            )

            self.velocity_x = velocity
            # self.velocity_y = velocity_y
            self.image = enemy_image_bullet2
            self.used = False

class ShockWave(pygame.Rect):
    def __init__(self, x, y, direction):
        pygame.Rect.__init__(self, x, y, WEB_WIDTH, WEB_HEIGHT)
        self.direction = direction
        self.velocity_x = 6 * direction
        self.alive = True
        self.life_ms = 900
        self.spawn_time = pygame.time.get_ticks()
        self.image = spider_web_image

    def update(self, speed_scale=1.0):
        self.x += self.velocity_x * speed_scale
        if pygame.time.get_ticks() - self.spawn_time >= self.life_ms:
            self.alive = False
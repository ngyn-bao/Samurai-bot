import pygame
import os

from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_JUMP_WIDTH, PLAYER_JUMP_HEIGHT,PLAYER_ATTACK_WIDTH, GAME_WIDTH, GAME_HEIGHT, TILE_SIZE, INFANTRYMAN_WIDTH, INFANTRYMAN_HEIGHT, PLAYER_SHURIKEN_WIDTH, PLAYER_SHURIKEN_HEIGHT, INFANTRYMAN_BULLET_WIDTH, INFANTRYMAN_BULLET_HEIGHT, INFANTRYMAN_GUARD_HEIGHT, LIFE_ENERGY_WIDTH, LIFE_ENERGY_HEIGHT, BIG_LIFE_ENERGY_WIDTH, BIG_LIFE_ENERGY_HEIGHT, KEY_ITEM_WIDTH, KEY_ITEM_HEIGHT, DRONE_WIDTH, DRONE_HEIGHT, METALL_WIDTH, METALL_HEIGHT, INFANTRYMAN_GUARD_WIDTH, PLAYER_ATTACK_HEIGHT, INFANTRYMAN_BULLET_WIDTH2, INFANTRYMAN_BULLET_HEIGHT2, BOSS_WIDTH, BOSS_HEIGHT, WEB_WIDTH, WEB_HEIGHT

#images
def load_image(image_name, scale=None):
    image = pygame.image.load(os.path.join("images", image_name))
    if scale is not None:
        image = pygame.transform.scale(image, scale)
    return image

# background_image = pygame.image.load(os.path.join("images", "background.png"))
# player_image_right = pygame.image.load(os.path.join("images", "megaman-right.png"))
# player_image_right = pygame.transform.scale(player_image_right, (PLAYER_WIDTH, PLAYER_HEIGHT))
background_image = load_image("background.png", (GAME_WIDTH, GAME_HEIGHT))
player_image_right = load_image("samurai-right.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_image_left = load_image("samurai-left.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_takehit_left = load_image("samurai-gethit-left.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_takehit_right = load_image("samurai-gethit-right.png", (PLAYER_WIDTH, PLAYER_HEIGHT))
player_image_jump_right = load_image("samurai-right-jump.png", (PLAYER_JUMP_WIDTH, PLAYER_JUMP_HEIGHT))
player_image_jump_left = load_image("samurai-left-jump.png", (PLAYER_JUMP_WIDTH, PLAYER_JUMP_HEIGHT))
player_image_attack_right = load_image("samurai-right-attack.png",(PLAYER_ATTACK_WIDTH, PLAYER_ATTACK_HEIGHT))
player_image_attack_left = load_image("samurai-left-attack.png",(PLAYER_ATTACK_WIDTH, PLAYER_ATTACK_HEIGHT))
player_image_shuriken = load_image("shuriken.png",(PLAYER_SHURIKEN_WIDTH, PLAYER_SHURIKEN_HEIGHT))
# player_image_shoot_left = load_image()
floor_tile_image = load_image("floor-tile.png", (TILE_SIZE, TILE_SIZE))
wall_tile_image = load_image("wall-tile.png", (TILE_SIZE, TILE_SIZE))
beam_tile_image = load_image("beam-tile.png", (TILE_SIZE, TILE_SIZE))
rock_tile1_image = load_image("rock-tile1.png", (TILE_SIZE, TILE_SIZE))
rock_tile2_image = load_image("rock-tile2.png", (TILE_SIZE, TILE_SIZE))
rock_tile3_image = load_image("rock-tile3.png", (TILE_SIZE, TILE_SIZE))
rock_tile4_image = load_image("rock-tile4.png", (TILE_SIZE, TILE_SIZE))
door_tile_image = load_image("door-tile.png", (TILE_SIZE, TILE_SIZE))
room_tile_image = load_image("room-tile.png", (TILE_SIZE, TILE_SIZE))

infantryman_image_left = load_image("metall-left.png", (METALL_WIDTH, METALL_HEIGHT))
infantryman_image_right = load_image("metall-right.png", (METALL_WIDTH, METALL_HEIGHT))
infantryman_guard_right = load_image("metall-right-guard.png", (METALL_WIDTH, INFANTRYMAN_GUARD_HEIGHT))
infantryman_guard_left = load_image("metall-left-guard.png", (METALL_WIDTH, INFANTRYMAN_GUARD_HEIGHT))
infantryman_image_left2 = load_image("infantryman-left.png", (INFANTRYMAN_WIDTH, INFANTRYMAN_HEIGHT))
infantryman_image_right2 = load_image("infantryman-right.png", (INFANTRYMAN_WIDTH, INFANTRYMAN_HEIGHT))
infantryman_guard_right2 = load_image("infantryman-guard-right.png", (INFANTRYMAN_GUARD_WIDTH, INFANTRYMAN_HEIGHT))
infantryman_guard_left2 = load_image("infantryman-guard-left.png", (INFANTRYMAN_GUARD_WIDTH, INFANTRYMAN_HEIGHT))
enemy_image_bullet = load_image("metall-bullet.png",(INFANTRYMAN_BULLET_WIDTH, INFANTRYMAN_BULLET_HEIGHT))
enemy_image_bullet2 = load_image("bullet.png",(INFANTRYMAN_BULLET_WIDTH2, INFANTRYMAN_BULLET_HEIGHT2))
life_energy_image = load_image("life-energy.png",(LIFE_ENERGY_WIDTH, LIFE_ENERGY_HEIGHT))
big_life_energy_image = load_image("big-life-energy.png",(BIG_LIFE_ENERGY_WIDTH, BIG_LIFE_ENERGY_HEIGHT))
score_ball_image = load_image("score-ball.png", (TILE_SIZE // 2, TILE_SIZE // 2))
spike_image = load_image("spike.png", (TILE_SIZE, TILE_SIZE))
drone_image_right = load_image("drone-right.png", (DRONE_WIDTH, DRONE_HEIGHT))
drone_image_left = load_image("drone-left.png", (DRONE_WIDTH, DRONE_HEIGHT))
boss_spider_image = load_image("boss-spider.png", (BOSS_WIDTH, BOSS_HEIGHT))

spider_web_image = load_image("spider-web.png", (WEB_WIDTH, WEB_HEIGHT))
# health_image = load_image("health.png", (HEALTH_WIDTH, HEALTH_HEIGHT))

item_box_image = load_image("box-item-tile.png",(TILE_SIZE, TILE_SIZE))

time_warp_item_image = pygame.Surface((24, 24), pygame.SRCALPHA)
pygame.draw.circle(time_warp_item_image, (80, 220, 255), (12, 12), 11)
pygame.draw.circle(time_warp_item_image, (20, 50, 85), (12, 12), 8)
pygame.draw.line(time_warp_item_image, (190, 240, 255), (12, 12), (12, 7), 2)
pygame.draw.line(time_warp_item_image, (190, 240, 255), (12, 12), (16, 12), 2)

boss_key_item_image = pygame.Surface((KEY_ITEM_WIDTH, KEY_ITEM_HEIGHT), pygame.SRCALPHA)
pygame.draw.circle(boss_key_item_image, (235, 205, 80), (6, 9), 5)
pygame.draw.rect(boss_key_item_image, (235, 205, 80), (6, 8, 9, 3))
pygame.draw.rect(boss_key_item_image, (235, 205, 80), (12, 8, 2, 6))
pygame.draw.rect(boss_key_item_image, (235, 205, 80), (15, 10, 2, 4))
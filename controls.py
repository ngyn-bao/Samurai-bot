import pygame
# from player import player
from settings import PLAYER_DISTANCE, GAME_WIDTH, GAME_HEIGHT, PLAYER_VELOCITY_X, PLAYER_VELOCITY_Y
from physics import move_player_x

def handle_player_movement(player, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses):
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and not player.jumping:
        # player.y = max(player.y - PLAYER_DISTANCE, 0)   
        player.velocity_y = PLAYER_VELOCITY_Y
        player.jumping = True
    # if keys[pygame.K_DOWN] or keys[pygame.K_s]:
    #     player.y = min(player.y + PLAYER_DISTANCE, GAME_HEIGHT - player.height)
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        # player.velocity_x = -PLAYER_VELOCITY_X
        move_player_x(player, PLAYER_VELOCITY_X, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses)
        player.direction = "left"
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        # player.velocity_x = PLAYER_VELOCITY_X
        move_player_x(player,-PLAYER_VELOCITY_X, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses)
        move_player_x
        player.direction = "right"
    if keys[pygame.K_SPACE] and player.attacking == False:
        player.velocity_x = 0
        player.set_attack()
        # player.attacking = False
    if keys[pygame.K_x] and player.shooting == False:
        player.set_shooting(player)
        # print(len(player.shurikens))
        
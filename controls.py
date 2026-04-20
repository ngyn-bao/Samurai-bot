import pygame
from settings import PLAYER_VELOCITY_X, PLAYER_VELOCITY_Y
from physics import move_player_x, check_tile_collision

DEFAULT_KEYMAP = {
    "jump": [pygame.K_UP, pygame.K_w],
    "left": [pygame.K_LEFT, pygame.K_a],
    "right": [pygame.K_RIGHT, pygame.K_d],
    "attack": [pygame.K_SPACE],
    "shoot": [pygame.K_x],
    "time_warp": [pygame.K_c],
}


def get_player_intent(keys, keymap=None):
    keymap = keymap or DEFAULT_KEYMAP

    def pressed(action):
        return any(keys[k] for k in keymap.get(action, []))

    return {
        "jump": pressed("jump"),
        "left": pressed("left"),
        "right": pressed("right"),
        "attack": pressed("attack"),
        "shoot": pressed("shoot"),
        "time_warp": pressed("time_warp"),
    }


def apply_player_intent(player, intent, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses, scroll_world=True, extra_players=None):
    if intent.get("jump") and not player.jumping:
        player.velocity_y = PLAYER_VELOCITY_Y
        player.jumping = True

    if intent.get("left"):
        if scroll_world:
            move_player_x(player, PLAYER_VELOCITY_X, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses, linked_players=extra_players)
        else:
            player.x -= PLAYER_VELOCITY_X
            tile = check_tile_collision(player, tiles)
            if tile is not None:
                player.x = tile.x + tile.width
        player.direction = "left"

    if intent.get("right"):
        if scroll_world:
            move_player_x(player, -PLAYER_VELOCITY_X, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses, linked_players=extra_players)
        else:
            player.x += PLAYER_VELOCITY_X
            tile = check_tile_collision(player, tiles)
            if tile is not None:
                player.x = tile.x - player.width
        player.direction = "right"

    if intent.get("attack") and not player.attacking:
        player.velocity_x = 0
        player.set_attack()

    if intent.get("shoot") and not player.shooting:
        player.set_shooting(player)


def handle_player_movement(player, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses):
    keys = pygame.key.get_pressed()
    intent = get_player_intent(keys)
    apply_player_intent(player, intent, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses)
    return intent
        
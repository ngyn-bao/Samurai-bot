import pygame

from images import (
    background_image,
    rock_tile1_image,
    rock_tile2_image,
    rock_tile3_image,
    rock_tile4_image,
    floor_tile_image,
    wall_tile_image,
    beam_tile_image,
    room_tile_image,
    door_tile_image,
    item_box_image,
    infantryman_guard_left,
    infantryman_guard_right,
    infantryman_image_left2,
    infantryman_image_right2,
    drone_image_left,
    drone_image_right,
    boss_spider_image,
    spike_image,
    player_image_shuriken,
    enemy_image_bullet,
    enemy_image_bullet2,
    spider_web_image,
    life_energy_image,
    big_life_energy_image,
    time_warp_item_image,
    boss_key_item_image,
    score_ball_image,
)
from settings import (
    GAME_WIDTH,
    GAME_HEIGHT,
    GAME_FONT_PATH,
    HP_PER_SEGMENT,
    MAX_SEGMENTS,
    HEALTH_SEGMENT_WIDTH,
    HEALTH_SEGMENT_HEIGHT,
    HEALTH_BAR_X,
    HEALTH_BAR_Y,
    COLOR_EMPTY,
    COLOR_FILL,
    COLOR_BORDER,
    BORDER_THICKNESS,
)
from player_skins import load_player_skin

_TILE_SURFACE_BY_KIND = {
    "rock1": rock_tile1_image,
    "rock2": rock_tile2_image,
    "rock3": rock_tile3_image,
    "rock4": rock_tile4_image,
    "floor": floor_tile_image,
    "wall": wall_tile_image,
    "beam": beam_tile_image,
    "room": room_tile_image,
    "door": door_tile_image,
    "item_box": item_box_image,
}


def _tile_surface(kind):
    return _TILE_SURFACE_BY_KIND.get(kind, rock_tile1_image)


def _camera_offset(snapshot):
    players = snapshot.get("players", [])
    p2 = next((p for p in players if p.get("id") == 2), None)
    if p2 is None and players:
        p2 = players[min(1, len(players) - 1)]
    if p2 is None:
        return 0, 0

    target_x = GAME_WIDTH // 2 - p2.get("w", 48) // 2
    target_y = GAME_HEIGHT // 2 - p2.get("h", 54) // 2
    return p2.get("x", 0) - target_x, p2.get("y", 0) - target_y


def _player_surface(p):
    skin = load_player_skin(p.get("skin_id", "samurai"))
    direction = p.get("direction", "right")
    jumping = p.get("jumping", False)
    attacking = p.get("attacking", False)
    invincible = p.get("invincible", False)

    if jumping:
        return skin["jump_right"] if direction == "right" else skin["jump_left"]
    if attacking:
        return skin["attack_right"] if direction == "right" else skin["attack_left"]
    if invincible:
        return skin["hit_right"] if direction == "right" else skin["hit_left"]
    return skin["right"] if direction == "right" else skin["left"]


def _item_surface(effect_type):
    if effect_type == "time_warp":
        return time_warp_item_image
    if effect_type == "boss_key":
        return boss_key_item_image
    if effect_type == "big_life":
        return big_life_energy_image
    if effect_type == "score":
        return score_ball_image
    return life_energy_image


def _draw_health_bar(window, player_state, bar_x, bar_y, label, label_color):
    font = pygame.font.Font(GAME_FONT_PATH, 20)
    label_surface = font.render(label, True, label_color)
    window.blit(label_surface, (bar_x, bar_y - 22))

    max_health = max(1, int(player_state.get("max_health", HP_PER_SEGMENT * MAX_SEGMENTS)))
    health = max(0, min(max_health, int(player_state.get("health", 0))))
    segments = max(1, max_health // HP_PER_SEGMENT)

    for i in range(segments):
        x = bar_x + i * HEALTH_SEGMENT_WIDTH
        rect = pygame.Rect(x, bar_y, HEALTH_SEGMENT_WIDTH, HEALTH_SEGMENT_HEIGHT)
        pygame.draw.rect(window, COLOR_EMPTY, rect)

        segment_hp = health - i * HP_PER_SEGMENT
        segment_hp = max(0, min(HP_PER_SEGMENT, segment_hp))

        if segment_hp > 0:
            fill_width = int(HEALTH_SEGMENT_WIDTH * (segment_hp / HP_PER_SEGMENT))
            fill_rect = pygame.Rect(x, bar_y, fill_width, HEALTH_SEGMENT_HEIGHT)
            pygame.draw.rect(window, COLOR_FILL, fill_rect)

        pygame.draw.rect(window, COLOR_BORDER, rect, BORDER_THICKNESS)


def draw_snapshot(window, snapshot):
    if not snapshot:
        return

    cam_dx, cam_dy = _camera_offset(snapshot)

    def tx(x):
        return x - cam_dx

    def ty(y):
        return y - cam_dy

    window.fill((0, 0, 0))
    window.blit(background_image, (0, 0))

    for tile in snapshot.get("background_tiles", []):
        window.blit(_tile_surface(tile.get("kind")), (tx(tile["x"]), ty(tile["y"])))

    for tile in snapshot.get("tiles", []):
        window.blit(_tile_surface(tile.get("kind")), (tx(tile["x"]), ty(tile["y"])))

    for spike in snapshot.get("spikes", []):
        window.blit(spike_image, (tx(spike["x"]), ty(spike["y"])))

    for item in snapshot.get("items", []):
        window.blit(_item_surface(item.get("effect_type")), (tx(item["x"]), ty(item["y"])))

    for enemy in snapshot.get("enemies", []):
        img = infantryman_guard_right if enemy.get("direction") == "right" else infantryman_guard_left
        window.blit(img, (tx(enemy["x"]), ty(enemy["y"])))
        for bullet in enemy.get("bullets", []):
            window.blit(enemy_image_bullet, (tx(bullet["x"]), ty(bullet["y"])))

    for enemy in snapshot.get("enemies2", []):
        img = infantryman_image_right2 if enemy.get("direction") == "right" else infantryman_image_left2
        window.blit(img, (tx(enemy["x"]), ty(enemy["y"])))
        for bullet in enemy.get("bullets", []):
            window.blit(enemy_image_bullet2, (tx(bullet["x"]), ty(bullet["y"])))

    for drone in snapshot.get("drones", []):
        img = drone_image_right if drone.get("direction") == "right" else drone_image_left
        window.blit(img, (tx(drone["x"]), ty(drone["y"])))

    for boss in snapshot.get("bosses", []):
        window.blit(boss_spider_image, (tx(boss["x"]), ty(boss["y"])))
        for wave in boss.get("projectiles", []):
            window.blit(spider_web_image, (tx(wave["x"]), ty(wave["y"])))

    players = snapshot.get("players", [])
    for p in players:
        window.blit(_player_surface(p), (tx(p["x"]), ty(p["y"])))
        for s in p.get("shurikens", []):
            window.blit(player_image_shuriken, (tx(s["x"]), ty(s["y"])))

    font = pygame.font.Font(GAME_FONT_PATH, 20)
    if players:
        p1 = players[0]
        _draw_health_bar(window, p1, HEALTH_BAR_X, HEALTH_BAR_Y, "P1", (230, 230, 230))
        p1_score = font.render(f"Score: {p1.get('score', 0)}", True, (230, 230, 230))
        window.blit(p1_score, (HEALTH_BAR_X, HEALTH_BAR_Y + 24))

    if len(players) > 1:
        p2 = players[1]
        bar_width = HEALTH_SEGMENT_WIDTH * MAX_SEGMENTS
        p2_bar_x = GAME_WIDTH - bar_width - HEALTH_BAR_X
        _draw_health_bar(window, p2, p2_bar_x, HEALTH_BAR_Y, "P2", (180, 220, 255))
        p2_score = font.render(f"Score: {p2.get('score', 0)}", True, (180, 220, 255))
        window.blit(p2_score, (p2_bar_x, HEALTH_BAR_Y + 24))

    life_text = font.render(f"Lives: {snapshot.get('shared_lives', 0)}", True, (255, 220, 120))
    window.blit(life_text, (HEALTH_BAR_X, HEALTH_BAR_Y + 48))

    if snapshot.get("game_over"):
        over = font.render("GAME OVER - host can restart with E", True, (255, 90, 90))
        window.blit(over, (GAME_WIDTH // 2 - 170, GAME_HEIGHT // 2))
    elif snapshot.get("victory_done"):
        win = font.render("VICTORY - host can restart with E", True, (255, 220, 120))
        window.blit(win, (GAME_WIDTH // 2 - 150, GAME_HEIGHT // 2))

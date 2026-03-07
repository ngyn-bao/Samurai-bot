import pygame
from images import background_image
# from player import draw_player
# from enemy import draw_enemy
# from map import draw_map
from settings import *

_HUD_FONT = None

def draw(window, player, background_tiles, tiles, enemies, enemies2, shurikens, items, spikes, drones, bosses):
    draw_background(window)
    draw_background_tiles(window, background_tiles)
    draw_tiles(window, tiles)
    draw_spikes(window,spikes)
    draw_player(window, player)
    draw_shurikens(window, shurikens)
    draw_enemies(window, enemies)
    draw_enemies2(window, enemies2)
    draw_drones(window, drones)
    draw_bosses(window, bosses)
    draw_item(window, items)
    # pygame.draw.rect(window, "red", (TILE_SIZE, TILE_SIZE, 10 * player.max_health, 10))
    # pygame.draw.rect(window, "green", (TILE_SIZE, TILE_SIZE, 10 * player.health, 10))
    draw_health_bar(window, player)
    draw_boss_health_bar(window, player, bosses)
    draw_time_warp_hud(window, player)

def draw_background(window):
    window.fill("black")
    window.blit(background_image, (0, 0))

def draw_background_tiles(window, background_tiles):
    for tile in background_tiles:
        if tile.x > GAME_WIDTH:
            break
        window.blit(tile.image, tile)

def draw_tiles(window, tiles):
    for tile in tiles:
        if tile.x > GAME_WIDTH:
            break
        window.blit(tile.image, tile)

def draw_shurikens(window, shurikens):
    for shuriken in shurikens:
        window.blit(shuriken.image, shuriken)

def draw_enemies(window, enemies):
    for enemy in enemies:
        if enemy.x > GAME_WIDTH:
            break
        enemy.update_image()
        window.blit(enemy.image, enemy)
        for bullet in enemy.bullets:
            window.blit(bullet.image, bullet) 

def draw_enemies2(window, enemies2):
    for enemy in enemies2:
        if enemy.x > GAME_WIDTH:
            break
        enemy.update_image()
        window.blit(enemy.image, enemy)
        for bullet in enemy.bullets:
            window.blit(bullet.image, bullet)
            
def draw_player(window, player):
    player.update_image()
    window.blit(player.image, player)
    
def draw_health_bar(window, player):
    if player.invincible and pygame.time.get_ticks() % 200 < 100:
        return
    segments = player.max_health // HP_PER_SEGMENT

    for i in range(segments):
        x = HEALTH_BAR_X + i * (HEALTH_SEGMENT_WIDTH)
        y = HEALTH_BAR_Y

        # HP của segment này (0 → HP_PER_SEGMENT)
        segment_hp = player.health - i * HP_PER_SEGMENT
        segment_hp = max(0, min(HP_PER_SEGMENT, segment_hp))

        rect = pygame.Rect(
            x, y,
            HEALTH_SEGMENT_WIDTH,
            HEALTH_SEGMENT_HEIGHT
        )

        pygame.draw.rect(window, COLOR_EMPTY, rect)

        if segment_hp > 0:
            fill_width = int(
                HEALTH_SEGMENT_WIDTH * (segment_hp / HP_PER_SEGMENT)
            )

            fill_rect = pygame.Rect(
                x, y,
                fill_width,
                HEALTH_SEGMENT_HEIGHT
            )

            pygame.draw.rect(window, COLOR_FILL, fill_rect)
            
        pygame.draw.rect(
            window,
            COLOR_BORDER,
            rect,
            BORDER_THICKNESS
        )


def draw_time_warp_hud(window, player):
    global _HUD_FONT
    if _HUD_FONT is None:
        _HUD_FONT = pygame.font.Font(GAME_FONT_PATH, 20)
        _HUD_FONT.set_bold(True)

    font = _HUD_FONT
    charges_text = font.render(f"Time Warp [C]: {player.time_warp_charges}", True, (0, 51, 204))
    window.blit(charges_text, (HEALTH_BAR_X, HEALTH_BAR_Y + 24))

    if player.is_time_warp_active():
        active_text = font.render("TIME WARP ACTIVE", True, (0, 51, 204))
        window.blit(active_text, (HEALTH_BAR_X, HEALTH_BAR_Y + 46))

    # if player.has_boss_key:
    #     window.blit(font.render("Boss Key: YES", True, (240, 220, 120)), (HEALTH_BAR_X, HEALTH_BAR_Y + 68))

def draw_item(window, items):
    for item in items:
        if item.x > GAME_WIDTH:
            break
        window.blit(item.image, item)
        
def draw_spikes(window, spikes):
    for spike in spikes:
        if spike.x > GAME_WIDTH:
            break
        window.blit(spike.image, spike)
        
def draw_drones(window, drones):
    for drone in drones:
        if drone.x > GAME_WIDTH:
            break
        drone.update_image()
        window.blit(drone.image, drone)

def draw_bosses(window, bosses):
    for boss in bosses:
        if boss.health <= 0:
            continue

        anchor_y = getattr(boss, "ceiling_y", 0)
        pygame.draw.line(
            window,
            (245, 245, 245),
            (boss.centerx, anchor_y),
            (boss.centerx, boss.top + 6),
            2
        )
        window.blit(boss.image, boss)

        # hp_ratio = max(0, boss.health) / boss.max_health
        # pygame.draw.rect(window, (60, 60, 60), (boss.x, boss.y - 8, boss.width, 5))
        # pygame.draw.rect(window, (220, 50, 50), (boss.x, boss.y - 8, int(boss.width * hp_ratio), 5))

        for p in boss.projectiles:
            if getattr(p, "alive", True):
                window.blit(p.image, p)
                
def draw_boss_health_bar(window, player, bosses):
    # Chỉ hiện khi player vào vùng boss
    # Có thể chỉnh 12 -> 10/14 để hẹp/rộng hơn
    trigger_half_width = TILE_SIZE * 12

    boss = next(
        (
            b for b in bosses
            if getattr(b, "health", 0) > 0
            and abs(player.centerx - getattr(b, "start_x", b.centerx)) <= trigger_half_width
        ),
        None
    )
    if boss is None:
        return

    boss_max_hp = max(1, getattr(boss, "max_health", 1))
    ratio = max(0, min(1, boss.health / boss_max_hp))

    player_bar_width = HEALTH_SEGMENT_WIDTH * MAX_SEGMENTS
    x = HEALTH_BAR_X + player_bar_width + 30
    y = HEALTH_BAR_Y
    w = player_bar_width
    h = HEALTH_SEGMENT_HEIGHT

    pygame.draw.rect(window, (0, 0, 0), (x - 2, y - 2, w + 4, h + 4))
    pygame.draw.rect(window, (70, 70, 70), (x, y, w, h))
    pygame.draw.rect(window, (210, 40, 40), (x, y, int(w * ratio), h))
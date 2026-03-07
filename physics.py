import pygame
from settings import GRAVITY, GAME_WIDTH, FRICTION, INFANTRYMAN_DAMAGE, TILE_SIZE, DRONE_DAMAGE, METALL_DAMAGE, ENEMY_BULLET_DAMAGE, BOSS_CONTACT_DAMAGE, PLAYER_VELOCITY_Y, TIME_WARP_ENEMY_SPEED_MULTIPLIER, TIME_WARP_MAX_CHARGES
from items import drop_item, drop_item_from_box
from images import life_energy_image, big_life_energy_image, time_warp_item_image, boss_key_item_image, score_ball_image
from items import Item


def move(player, tiles, enemies, enemies2, shurikens, items, spikes, drones, bosses):
    enemy_speed_scale = TIME_WARP_ENEMY_SPEED_MULTIPLIER if player.is_time_warp_active() else 1.0
    # FRICTION (x movement)
    # if player.direction == "left" and player.velocity_x < 0:
    #     player.velocity_x += FRICTION
    # elif player.direction == "right" and player.velocity_x > 0:
    #     player.velocity_x -= FRICTION
    # else:
    #     player.velocity_x = 0
    # if abs(player.velocity_x) < FRICTION:
    #     player.velocity_x = 0
    # elif player.velocity_x > 0:
    #     player.velocity_x -= FRICTION
    # elif player.velocity_x < 0:
    #     player.velocity_x += FRICTION

        
    # player.x += player.velocity_x
    
    # if player.x < 0:
    #     player.x = 0
    # elif player.x +player.width > GAME_WIDTH:
    #     player.x = GAME_WIDTH - player.width
    
    check_tile_collision_x(player, tiles)
    # JUMPING (y movement)
    player.velocity_y += GRAVITY
    player.y += player.velocity_y

    # if player.y + player.height >= FLOOR_Y:
    #     player.y = FLOOR_Y - player.height
    #     player.velocity_y = 0
    #     player.jumping = False
    check_tile_collision_y(player, tiles)

    if player.attacking and player.attack_rect:
        if player.direction == "right":
            player.attack_rect.x = player.right
            player.attack_rect.y = player.y
        else:
            player.attack_rect.x = player.x - player.attack_rect.width
            player.attack_rect.y = player.y
    
    for spike in spikes:
        if player.colliderect(spike):
            if player.invincible:
                player.health -= 0
            else:
                player.set_invincible()
                player.health = max(0, player.health // 2) # game over
                player.x -= TILE_SIZE
                
            
    #shurikens
    for shuriken in shurikens:
        shuriken.x += shuriken.velocity_x
        
        broken_boxes = []

        for tile in tiles:
            if getattr(tile, "is_item_box", False) and shuriken.colliderect(tile):
                if not getattr(tile, "opened", False):
                    tile.opened = True
                    drop_item_from_box(tile, items)
                    broken_boxes.append(tile)

        if broken_boxes:
            tiles[:] = [tile for tile in tiles if tile not in broken_boxes]
            
        for enemy in enemies:
            if enemy.health > 0 and not shuriken.used and shuriken.colliderect(enemy):
                shuriken.used = True
                if not enemy.guarding:
                    enemy.health = max(0, enemy.health - player.shuriken_damge)
                    if enemy.health <= 0:
                        drop_item(enemy, items)
                        player.score += 500

        
        for enemy in enemies2:
            if enemy.health > 0 and not shuriken.used and shuriken.colliderect(enemy):
                shuriken.used = True
                enemy.health = max(0, enemy.health - player.shuriken_damge)
                if enemy.health <= 0:
                    drop_item(enemy, items) 
                    player.score += 600
        
        for drone in drones:
            if drone.health > 0 and not shuriken.used and shuriken.colliderect(drone):
                shuriken.used = True
                drone.health = max(0, drone.health - player.shuriken_damge)
                if drone.health <= 0:
                    drop_item(drone, items)    
                    player.score += 700
                    
        for boss in bosses:
            if boss.health > 0 and not shuriken.used and shuriken.colliderect(boss):
                shuriken.used = True
                boss.on_hit(player.shuriken_damge, player)
        # xoá shuriken đã dùng
    shurikens[:] = [s for s in shurikens if not s.used \
        and s.x + s.width > 0 and s.x < GAME_WIDTH]

     # ===== MELEE ATTACK =====
    if player.attacking and player.attack_rect:
        broken_boxes = []

        for tile in tiles:
            if getattr(tile, "is_item_box", False) and player.attack_rect.colliderect(tile):
                if not getattr(tile, "opened", False):
                    tile.opened = True
                    drop_item_from_box(tile, items)
                    broken_boxes.append(tile)

        if broken_boxes:
            tiles[:] = [tile for tile in tiles if tile not in broken_boxes]

        for enemy in enemies:
            if enemy.health > 0 and player.attack_rect.colliderect(enemy):
                enemy.health = max(0, enemy.health - player.attack_damage)
                if enemy.health <= 0:
                    drop_item(enemy, items)
                    player.score += 500
        for drone in drones:
            if drone.health > 0 and player.attack_rect.colliderect(drone):
                drone.health = max(0, drone.health - player.attack_damage)
                if drone.health <= 0:
                    drop_item(drone, items)
                    player.score += 700
        for enemy in enemies2:
            if enemy.health > 0 and player.attack_rect.colliderect(enemy):
                enemy.health = max(0, enemy.health - player.attack_damage)
                if enemy.health <= 0:
                    drop_item(enemy, items)
                    player.score += 600
        for boss in bosses:
            if boss.health > 0 and player.attack_rect.colliderect(boss):
                boss.on_hit(player.attack_damage, player)
    
    # new = []
    
    # for shuriken in player.shurikens:
    #     if not shuriken.used:
    #         new.append(shuriken)
    # player.shurikens = new 
    # enemies = [enemy for enemy in enemies if enemy.health > 0]   
    for boss in bosses:
        if boss.health <= 0:
            if not getattr(boss, "key_dropped", False):
                items.append(Item(boss.x + boss.width // 2, boss.y, boss_key_item_image, effect_type="boss_key"))
                boss.key_dropped = True
            continue

        boss.update(player, enemy_speed_scale)

        if not player.invincible and player.colliderect(boss):
            player.health = max(0, player.health - BOSS_CONTACT_DAMAGE)
            player.set_invincible()

        for wave in boss.projectiles:
            if getattr(wave, "alive", True) and not player.invincible and player.colliderect(wave):
                wave.alive = False
                player.health = max(0, player.health - player.max_health // 2)
                player.set_invincible()
    
    for enemy in enemies:
        if player.x < enemy.x:
            enemy.direction = "left"
        else:
            enemy.direction = "right"
            
        enemy.velocity_y += GRAVITY * enemy_speed_scale
        enemy.y += enemy.velocity_y
        check_tile_collision_y(enemy, tiles)
        
        if player.colliderect(enemy):
            stomped_guarding_metall = (
                enemy.guarding
                and player.velocity_y > 0
                and player.bottom <= enemy.top + TILE_SIZE // 2
                and player.centerx >= enemy.left
                and player.centerx <= enemy.right
            )

            if stomped_guarding_metall:
                enemy.health = 0
                drop_item(enemy, items)
                player.score += 500
                player.velocity_y = int(PLAYER_VELOCITY_Y * 0.8)
                player.jumping = True
                continue

            if not player.invincible:
                # print("COLLISION WITH ENEMY!")
                player.health -= METALL_DAMAGE
                player.health = max(0, player.health)
                player.set_invincible()
        
        enemy.set_shooting(player, enemy)
        for bullet in enemy.bullets:
            bullet.x += bullet.velocity_x * enemy_speed_scale
            bullet.y += bullet.velocity_y * enemy_speed_scale
            if not player.invincible and player.colliderect(bullet):
                player.health = max(0, player.health - ENEMY_BULLET_DAMAGE)
                bullet.used = True
                player.set_invincible()
            
        enemy.bullets = [bullet for bullet in enemy.bullets if not bullet.used and bullet.x + bullet.width > 0 and bullet.width < GAME_WIDTH]
    
    # for drone in drones:
    #     if abs(drone.x + drone.velocity_x - drone.start_x) >= drone.max_range_x:
    #         drone.velocity_x *= -1
    #         if drone.velocity_x < 0:
    #             drone.direction = "left"
    #         elif drone.velocity_x > 0:
    #             drone.direction = "right"
    #     else:
    #         drone.x += drone.velocity_x
            
    #     if abs(drone.y + drone.velocity_y - drone.start_y) >= drone.max_range_y:
    #         drone.velocity_y *= -1
    #     else:
    #         drone.y += drone.velocity_y

    #     if not player.invincible and player.colliderect(drone):
    #         player.health -= 33
    #         player.set_invincible()
    for drone in drones:

        now = pygame.time.get_ticks()
        distance = abs(drone.centerx - player.centerx)

        # ======================
        # PATROL
        # ======================
        if drone.state == "patrol":

            # bay qua lại bình thường
            drone.x += drone.velocity_x * enemy_speed_scale

            if abs(drone.x - drone.start_x) > drone.max_range_x:
                drone.velocity_x *= -1

            drone.direction = "right" if drone.velocity_x > 0 else "left"

            # phát hiện player
            if distance <= drone.attack_range:
                drone.state = "dive"

        # ======================
        # DIVE (lao chéo xuống)
        # ======================
        elif drone.state == "dive":

            dx = player.centerx - drone.centerx
            dy = player.centery - drone.centery

            length = max(1, (dx**2 + dy**2) ** 0.5)

            drone.x += drone.attack_speed * enemy_speed_scale * dx / length
            drone.y += drone.attack_speed * enemy_speed_scale * dy / length

            # chạm player
            if drone.colliderect(player):
                stomped = (
                    player.velocity_y > 0
                    and player.bottom <= drone.top + TILE_SIZE // 2
                    and player.centerx >= drone.left
                    and player.centerx <= drone.right
                )

                if stomped:
                    drone.health = 0
                    drop_item(drone, items)
                    player.score += 700
                    player.velocity_y = int(PLAYER_VELOCITY_Y * 0.8)
                    player.jumping = True
                    continue

                if not player.invincible:
                    player.health = max(0, player.health - DRONE_DAMAGE)
                    player.set_invincible()
                    drone.state = "rise"

            # nếu lao quá thấp
            if drone.y > drone.start_y + TILE_SIZE * 3:
                drone.state = "rise"

        # ======================
        # RISE (bay chéo lên lại)
        # ======================
        elif drone.state == "rise":

            dx = drone.start_x - drone.x
            dy = drone.start_y - drone.y

            length = max(1, (dx**2 + dy**2) ** 0.5)

            drone.x += drone.attack_speed * enemy_speed_scale * dx / length
            drone.y += drone.attack_speed * enemy_speed_scale * dy / length

            # về vị trí ban đầu
            if abs(drone.x - drone.start_x) < 5 and abs(drone.y - drone.start_y) < 5:
                drone.x = drone.start_x
                drone.y = drone.start_y
                drone.state = "cooldown"
                drone.last_action_time = now

        # ======================
        # COOLDOWN
        # ======================
        elif drone.state == "cooldown":

            if now - drone.last_action_time > drone.cooldown_time:
                if distance <= drone.attack_range:
                    drone.state = "dive"
                else:
                    drone.state = "patrol"

        if drone.health > 0 and drone.state != "dive" and drone.colliderect(player):
            stomped = (
                player.velocity_y > 0
                and player.bottom <= drone.top + TILE_SIZE // 2
                and player.centerx >= drone.left
                and player.centerx <= drone.right
            )

            if stomped:
                drone.health = 0
                drop_item(drone, items)
                player.score += 700
                player.velocity_y = int(PLAYER_VELOCITY_Y * 0.8)
                player.jumping = True
                continue

            if not player.invincible:
                player.health = max(0, player.health - DRONE_DAMAGE)
                player.set_invincible()
    
    for enemy in enemies2:
        distance = abs(enemy.x - player.x)
        if distance <= TILE_SIZE * 3:
            enemy.state = "attack"
        else:
            enemy.state = "patrol"

        # ===== PATROL =====
        if enemy.state == "patrol":
            enemy.x += enemy.velocity_x * enemy_speed_scale

            distance_from_start = enemy.x - enemy.start_x

            if distance_from_start > enemy.max_range_x:
                enemy.x = enemy.start_x + enemy.max_range_x
                enemy.velocity_x *= -1

            elif distance_from_start < -enemy.max_range_x:
                enemy.x = enemy.start_x - enemy.max_range_x
                enemy.velocity_x *= -1

            enemy.direction = "right" if enemy.velocity_x > 0 else "left"

        # ===== ATTACK =====
        elif enemy.state == "attack":
            # Đứng yên
            # KHÔNG update x

            # quay mặt về player
            if player.centerx < enemy.centerx:
                enemy.direction = "left"
            else:
                enemy.direction = "right"

            enemy.set_shooting(player, enemy)
        # if player.x < enemy.x:
        #     enemy.direction = "left"
        # else:
        #     enemy.direction = "right"
            
        enemy.velocity_y += GRAVITY * enemy_speed_scale
        enemy.y += enemy.velocity_y
        check_tile_collision_y(enemy, tiles)
        
        if not player.invincible and player.colliderect(enemy):
            # print("COLLISION WITH ENEMY!")
            # player.health -= INFANTRYMAN_DAMAGE
            player.health = max(0, player.health - INFANTRYMAN_DAMAGE)
            player.set_invincible()
        
        enemy.set_shooting(player, enemy)
        for bullet in enemy.bullets:
            bullet.x += bullet.velocity_x * enemy_speed_scale
            # bullet.y += bullet.velocity_y
            if not player.invincible and player.colliderect(bullet):
                player.health = max(0, player.health - ENEMY_BULLET_DAMAGE)
                bullet.used = True
                player.set_invincible()
            
        enemy.bullets = [bullet for bullet in enemy.bullets if not bullet.used and bullet.x + bullet.width > 0 and bullet.width < GAME_WIDTH]
    
    for item in items:
        item.velocity_y += GRAVITY
        item.y += item.velocity_y
        check_tile_collision_y(item, tiles)
        if player.colliderect(item):
            item.used = True
            if item.image == life_energy_image:
                player.health = min(player.health + 33, player.max_health)
            elif item.image == big_life_energy_image:
                player.health = min(player.health + 66, player.max_health)
            elif item.image == time_warp_item_image or getattr(item, "effect_type", None) == "time_warp":
                player.add_time_warp_charge(TIME_WARP_MAX_CHARGES)
            elif item.image == boss_key_item_image or getattr(item, "effect_type", None) == "boss_key":
                player.has_boss_key = True
                player.exit_zones = [tile.copy() for tile in tiles if getattr(tile, "is_door", False)]
                tiles[:] = [tile for tile in tiles if not getattr(tile, "is_door", False)]
            elif item.image == score_ball_image:
                player.score += 1000

    for zone in player.exit_zones:
        if player.colliderect(zone):
            player.reached_exit = True
            break
    
    # xoá enemy chết
    enemies[:] = [e for e in enemies if e.health > 0]
    enemies2[:] = [e for e in enemies2 if e.health > 0]
    drones[:] = [d for d in drones if d.health > 0]
    bosses[:] = [b for b in bosses if b.health > 0]          
    items[:] = [item for item in items if not item.used]
    
def check_tile_collision(character, tiles):
    for tile in tiles:
        if getattr(tile, "is_door", False) and getattr(tile, "is_open", False):
            continue
        if character.colliderect(tile):
            return tile
        elif tile.x - character.x > GAME_WIDTH:
            return None
    return None

def check_tile_collision_x(character, tiles):
    tile = check_tile_collision(character, tiles)
    if tile is not None:
        if character.velocity_x < 0:
            character.x = tile.x + tile.width
        elif character.velocity_x > 0:
            character.x = tile.x - character.width
        character.velocity_x = 0
        
def check_tile_collision_y(character, tiles):
    tile = check_tile_collision(character, tiles)
    if tile is not None:
        if character.velocity_y < 0:
            character.y = tile.y + tile.height
        elif character.velocity_y > 0:
            character.y = tile.y - character.height
            character.jumping = False
        character.velocity_y = 0    
        
def move_player_x(player, velocity_x, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses):
    move_map_x(player, velocity_x, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses)
    tile = check_tile_collision(player, tiles)
    if tile is not None:
        move_map_x(player, -velocity_x, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses)


def move_map_x(player, velocity_x, background_tiles, tiles, enemies, enemies2, items, spikes, drones, bosses):
    for background_tile in background_tiles:
        background_tile.x += velocity_x
        
    for tile in tiles:
        tile.x += velocity_x
        
    for enemy in enemies:
        enemy.x += velocity_x
        for bullet in enemy.bullets:
            bullet.x += velocity_x
    
    for enemy in enemies2:
        enemy.start_x += velocity_x 
        enemy.x += velocity_x
        for bullet in enemy.bullets:
            bullet.x += velocity_x
    
    for item in items:
        item.x += velocity_x

    for exit_zone in player.exit_zones:
        exit_zone.x += velocity_x
        
    for spike in spikes:
        spike.x += velocity_x

    for drone in drones:
        drone.start_x += velocity_x    
        drone.x += velocity_x
    
    for boss in bosses:
        boss.start_x += velocity_x
        boss.x += velocity_x
        for p in boss.projectiles:
            p.x += velocity_x

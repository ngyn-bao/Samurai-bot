import pygame
from sys import exit

from settings import (
    FPS,
    GAME_WIDTH,
    GAME_HEIGHT,
    INVINCIBLE_END,
    SHOOTING_END,
    ATTACKING_END,
    GAME_BGM_PATH,
    GAME_BGM_VOLUME,
    TIME_WARP_DURATION_MS,
    GAME_FONT_PATH,
    GRAVITY,
    BOSS_CONTACT_DAMAGE,
    ENEMY_BULLET_DAMAGE,
    INFANTRYMAN_DAMAGE,
    METALL_DAMAGE,
    DRONE_DAMAGE,
    TILE_SIZE,
    TIME_WARP_MAX_CHARGES,
    TIME_WARP_ENEMY_SPEED_MULTIPLIER,
    PLAYER_VELOCITY_Y
)
from controls import get_player_intent, apply_player_intent
from physics import move, check_tile_collision_y
from render import draw
from client_render import draw_snapshot
from player import Player
from images import player_image_right, life_energy_image, big_life_energy_image, time_warp_item_image, boss_key_item_image, score_ball_image
from map import create_map
from rules import load_rules
from netplay import NetSession, world_snapshot
from items import drop_item, drop_item_from_box


class Game:
    def __init__(self, mode="single", host="127.0.0.1", port=5055, rules=None, selected_skins=None):
        self.mode = mode
        self.rules = rules or load_rules()
        available_skins = self.rules.get("skins", {}).get("available", ["samurai", "samurai-2"])
        skin1 = available_skins[0] if len(available_skins) > 0 else "samurai"
        skin2 = available_skins[1] if len(available_skins) > 1 else skin1
        default_selected = self.rules.get("skins", {}).get("selected", {})
        selected_skins = selected_skins or {}
        self.selected_skins = {
            "player1": selected_skins.get("player1", default_selected.get("player1", "samurai")),
            "player2": selected_skins.get("player2", default_selected.get("player2", "samurai-2")),
        }
        if self.mode == "host":
            self.selected_skins = {
                "player1": skin1,
                "player2": skin2,
            }

        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

        self.net = NetSession(mode=mode if mode in ("host", "client") else "single", host=host, port=port)
        self.remote_intent = {}
        self.last_snapshot = None

        self._init_world()
        pygame.display.set_icon(player_image_right)
        pygame.display.set_caption("Samurai-bot")

        self.paused = False
        self.pause_state = "main"
        self.pause_music_on = True

        self.pause_title_font = pygame.font.Font(GAME_FONT_PATH, 46)
        self.pause_title_font.set_bold(True)
        self.pause_btn_font = pygame.font.Font(GAME_FONT_PATH, 30)
        self.pause_btn_font.set_bold(True)
        self.pause_text_font = pygame.font.Font(GAME_FONT_PATH, 24)

        self.pause_buttons_main = [
            ("Resume", pygame.Rect(GAME_WIDTH // 2 - 120, 200, 240, 52)),
            ("Option", pygame.Rect(GAME_WIDTH // 2 - 120, 270, 240, 52)),
            ("Exit Game", pygame.Rect(GAME_WIDTH // 2 - 120, 340, 240, 52)),
        ]
        self.pause_buttons_options = [
            ("Toggle Music", pygame.Rect(GAME_WIDTH // 2 - 140, 250, 280, 52)),
            ("Back", pygame.Rect(GAME_WIDTH // 2 - 140, 320, 280, 52)),
        ]

        self.game_over = False
        self.victory_cutscene = False
        self.victory_done = False

        self.game_over_title_font = pygame.font.Font(GAME_FONT_PATH, 56)
        self.game_over_title_font.set_bold(True)
        self.game_over_text_font = pygame.font.Font(GAME_FONT_PATH, 28)
        self.game_over_text_font.set_bold(True)
        self.victory_title_font = pygame.font.Font(GAME_FONT_PATH, 56)
        self.victory_title_font.set_bold(True)
        self.victory_text_font = pygame.font.Font(GAME_FONT_PATH, 28)
        self.victory_text_font.set_bold(True)
        self.score_font = pygame.font.Font(GAME_FONT_PATH, 24)
        self.score_font.set_bold(True)

        self._start_bgm()

    def _init_world(self):
        self.player = Player(player_id=1, skin_id=self.selected_skins.get("player1", "samurai"))
        self.player2 = Player(player_id=2, spawn_x=self.player.spawn_x + 64, spawn_y=self.player.spawn_y, skin_id=self.selected_skins.get("player2", "samurai-2"))
        self.players = [self.player]

        if self.mode == "host":
            self.players.append(self.player2)

        self.shared_lives = int(self.rules.get("coop", {}).get("shared_lives", 2)) if self.mode in ("host", "client") else 0

        time_warp_rules = self.rules.get("time_warp", {})
        configured_duration = int(time_warp_rules.get("duration_ms", TIME_WARP_DURATION_MS))
        configured_max_charges = int(time_warp_rules.get("max_charges", TIME_WARP_MAX_CHARGES))
        configured_enemy_speed_multiplier = float(time_warp_rules.get("enemy_speed_multiplier",  TIME_WARP_ENEMY_SPEED_MULTIPLIER))

        self.time_warp_duration_ms = max(250, configured_duration)
        self.time_warp_max_charges = max(0, configured_max_charges)
        self.time_warp_enemy_speed_multiplier = min(1.0, max(0.1, configured_enemy_speed_multiplier))

        self.player.time_warp_duration_ms = self.time_warp_duration_ms
        self.player.time_warp_max_charges = self.time_warp_max_charges
        self.player.time_warp_enemy_speed_multiplier = self.time_warp_enemy_speed_multiplier

        self.player2.time_warp_duration_ms = self.time_warp_duration_ms
        self.player2.time_warp_max_charges = self.time_warp_max_charges
        self.player2.time_warp_enemy_speed_multiplier = self.time_warp_enemy_speed_multiplier

        self.enemies = []
        self.enemies2 = []
        self.tiles = []
        self.background_tiles = []
        self.items = []
        self.spikes = []
        self.drones = []
        self.bosses = []

        if self.mode != "client":
            create_map(self.player, self.background_tiles, self.tiles, self.enemies, self.enemies2, self.spikes, self.drones, self.bosses)

    def _start_bgm(self):
        try:
            pygame.mixer.music.load(GAME_BGM_PATH)
            pygame.mixer.music.set_volume(GAME_BGM_VOLUME)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def _stop_bgm(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def run(self):
        while True:
            self.handle_events()

            if self.mode == "client":
                self._run_client_frame()
            else:
                self._run_host_or_single_frame()

            pygame.display.update()
            self.clock.tick(FPS)

    def _run_client_frame(self):
        self.net.poll_client_connect()

        if not self.paused:
            keys = pygame.key.get_pressed()
            intent = get_player_intent(keys)
            self.net.send({"type": "input", "intent": intent})

        incoming = self.net.poll_receive()
        if incoming and incoming.get("type") == "snapshot":
            self.last_snapshot = incoming.get("payload")

        draw_snapshot(self.window, self.last_snapshot)

    def _run_host_or_single_frame(self):
        if self.mode == "host":
            self.net.poll_connect()
            incoming = self.net.poll_receive()
            if incoming and incoming.get("type") == "input":
                self.remote_intent = incoming.get("intent", {})

        if not self.paused and not self.game_over and not self.victory_cutscene and not self.victory_done:
            keys = pygame.key.get_pressed()
            local_intent = get_player_intent(keys)
            apply_player_intent(
                self.player,
                local_intent,
                self.background_tiles,
                self.tiles,
                self.enemies,
                self.enemies2,
                self.items,
                self.spikes,
                self.drones,
                self.bosses,
                scroll_world=True,
                extra_players=[self.player2] if self.mode == "host" and self.net.connected else None,
            )
            if local_intent.get("time_warp"):
                self.player.activate_time_warp()

            if self.mode == "host" and self.net.connected:
                apply_player_intent(
                    self.player2,
                    self.remote_intent,
                    self.background_tiles,
                    self.tiles,
                    self.enemies,
                    self.enemies2,
                    self.items,
                    self.spikes,
                    self.drones,
                    self.bosses,
                    scroll_world=False,
                )
                if self.remote_intent.get("time_warp"):
                    self.player2.activate_time_warp()

            move(
                self.player,
                self.tiles,
                self.enemies,
                self.enemies2,
                self.player.shurikens,
                self.items,
                self.spikes,
                self.drones,
                self.bosses,
                all_players=self.players if self.mode == "host" else None,
            )

            if self.mode == "host":
                self._update_secondary_player(self.player2)

            self._check_team_progress()

        elif self.victory_cutscene:
            self._update_victory_cutscene()

        extra_players = [self.player2] if self.mode == "host" and self.net.connected else None
        draw(self.window, self.player, self.background_tiles, self.tiles, self.enemies, self.enemies2, self.player.shurikens, self.items, self.spikes, self.drones, self.bosses, extra_players=extra_players)
        self._draw_score()

        if self.mode == "host" and self.net.connected:
            self._draw_connection_status("CONNECTED")
        elif self.mode == "host":
            self._draw_connection_status("WAITING FOR CLIENT")

        if self.game_over:
            self._draw_game_over()
        elif self.victory_done:
            self._draw_victory_screen()
        elif self.paused:
            self._draw_pause_menu()

        if self.mode == "host":
            self.net.send({"type": "snapshot", "payload": world_snapshot(self)})

    def _update_secondary_player(self, player):
        player.velocity_y += GRAVITY
        player.y += player.velocity_y
        check_tile_collision_y(player, self.tiles)

        if player.attacking and player.attack_rect:
            if player.direction == "right":
                player.attack_rect.x = player.right
                player.attack_rect.y = player.y
            else:
                player.attack_rect.x = player.x - player.attack_rect.width
                player.attack_rect.y = player.y

        self._apply_secondary_player_offense(player)

        for spike in self.spikes:
            if player.colliderect(spike) and not player.invincible:
                player.health = max(0, player.health // 2)
                player.set_invincible()

        for enemy in self.enemies:
            hit_player = player if player.colliderect(enemy) else None
            if hit_player is not None:
                stomped_guarding_metall = (
                    hit_player.velocity_y > 1
                    and hit_player.centery < enemy.centery
                    and hit_player.bottom <= enemy.top + TILE_SIZE // 3
                    and hit_player.centerx >= enemy.left + enemy.width // 5
                    and hit_player.centerx <= enemy.right - enemy.width // 5
                )

                if stomped_guarding_metall:
                    enemy.health = 0
                    drop_item(enemy, self.items)
                    hit_player.score += 500
                    hit_player.velocity_y = int(PLAYER_VELOCITY_Y * 0.8)
                    hit_player.jumping = True
                    continue

                if not hit_player.invincible:
                    hit_player.health = max(0, hit_player.health - METALL_DAMAGE)
                    hit_player.set_invincible()
            for bullet in enemy.bullets:
                hit_player = player if player.colliderect(bullet) else None
                if hit_player is not None and not hit_player.invincible:
                    hit_player.health = max(0, hit_player.health - ENEMY_BULLET_DAMAGE)
                    bullet.used = True
                    hit_player.set_invincible()

        for enemy in self.enemies2:
            if player.colliderect(enemy) and not player.invincible:
                player.health = max(0, player.health - INFANTRYMAN_DAMAGE)
                player.set_invincible()
            for bullet in enemy.bullets:
                if player.colliderect(bullet) and not player.invincible:
                    player.health = max(0, player.health - ENEMY_BULLET_DAMAGE)
                    bullet.used = True
                    player.set_invincible()

        for drone in self.drones:
            if player.colliderect(drone) and not player.invincible:
                player.health = max(0, player.health - DRONE_DAMAGE)
                player.set_invincible()
                drone.state = "rise"

        for boss in self.bosses:
            if player.colliderect(boss) and not player.invincible:
                player.health = max(0, player.health - BOSS_CONTACT_DAMAGE)
                player.set_invincible()
            for wave in boss.projectiles:
                if getattr(wave, "alive", True) and not player.invincible and player.colliderect(wave):
                    wave.alive = False
                    player.health = max(0, player.health - player.max_health // 2)
                    player.set_invincible()

        for item in self.items:
            if player.colliderect(item):
                item.used = True
                if item.image == life_energy_image:
                    player.health = min(player.health + 33, player.max_health)
                elif item.image == big_life_energy_image:
                    player.health = min(player.health + 66, player.max_health)
                elif item.image == time_warp_item_image or getattr(item, "effect_type", None) == "time_warp":
                    player.add_time_warp_charge()
                elif item.image == boss_key_item_image or getattr(item, "effect_type", None) == "boss_key":
                    for p in self.players:
                        p.has_boss_key = True
                        p.exit_zones = [tile.copy() for tile in self.tiles if getattr(tile, "is_door", False)]
                    self.tiles[:] = [tile for tile in self.tiles if not getattr(tile, "is_door", False)]
                elif item.image == score_ball_image:
                    player.score += 1000

        for zone in player.exit_zones:
            if player.colliderect(zone):
                player.reached_exit = True
                break

    def _apply_secondary_player_offense(self, player):
        for shuriken in player.shurikens:
            shuriken.x += shuriken.velocity_x

            broken_boxes = []
            for tile in self.tiles:
                if getattr(tile, "is_item_box", False) and shuriken.colliderect(tile) and not getattr(tile, "opened", False):
                    tile.opened = True
                    drop_item_from_box(tile, self.items)
                    shuriken.used = True
                    broken_boxes.append(tile)

            if broken_boxes:
                self.tiles[:] = [tile for tile in self.tiles if tile not in broken_boxes]

            for enemy in self.enemies:
                if enemy.health > 0 and not shuriken.used and shuriken.colliderect(enemy):
                    shuriken.used = True
                    if not enemy.guarding:
                        enemy.health = max(0, enemy.health - player.shuriken_damge)
                        if enemy.health <= 0:
                            drop_item(enemy, self.items)
                            player.score += 500

            for enemy in self.enemies2:
                if enemy.health > 0 and not shuriken.used and shuriken.colliderect(enemy):
                    shuriken.used = True
                    enemy.health = max(0, enemy.health - player.shuriken_damge)
                    if enemy.health <= 0:
                        drop_item(enemy, self.items)
                        player.score += 600

            for drone in self.drones:
                if drone.health > 0 and not shuriken.used and shuriken.colliderect(drone):
                    shuriken.used = True
                    drone.health = max(0, drone.health - player.shuriken_damge)
                    if drone.health <= 0:
                        drop_item(drone, self.items)
                        player.score += 700

            for boss in self.bosses:
                if boss.health > 0 and not shuriken.used and shuriken.colliderect(boss):
                    shuriken.used = True
                    boss.on_hit(player.shuriken_damge, player)

        world_right = max((tile.right for tile in self.tiles), default=GAME_WIDTH) + TILE_SIZE
        player.shurikens[:] = [
            s for s in player.shurikens
            if not s.used and s.x + s.width > -TILE_SIZE and s.x < world_right
        ]

        if player.attacking and player.attack_rect:
            broken_boxes = []
            for tile in self.tiles:
                if getattr(tile, "is_item_box", False) and player.attack_rect.colliderect(tile) and not getattr(tile, "opened", False):
                    tile.opened = True
                    drop_item_from_box(tile, self.items)
                    broken_boxes.append(tile)

            if broken_boxes:
                self.tiles[:] = [tile for tile in self.tiles if tile not in broken_boxes]

            for enemy in self.enemies:
                if enemy.health > 0 and player.attack_rect.colliderect(enemy):
                    enemy.health = max(0, enemy.health - player.attack_damage)
                    if enemy.health <= 0:
                        drop_item(enemy, self.items)
                        player.score += 500

            for enemy in self.enemies2:
                if enemy.health > 0 and player.attack_rect.colliderect(enemy):
                    enemy.health = max(0, enemy.health - player.attack_damage)
                    if enemy.health <= 0:
                        drop_item(enemy, self.items)
                        player.score += 600

            for drone in self.drones:
                if drone.health > 0 and player.attack_rect.colliderect(drone):
                    drone.health = max(0, drone.health - player.attack_damage)
                    if drone.health <= 0:
                        drop_item(drone, self.items)
                        player.score += 700

            for boss in self.bosses:
                if boss.health > 0 and player.attack_rect.colliderect(boss):
                    boss.on_hit(player.attack_damage, player)

        self.enemies[:] = [e for e in self.enemies if e.health > 0]
        self.enemies2[:] = [e for e in self.enemies2 if e.health > 0]
        self.drones[:] = [d for d in self.drones if d.health > 0]
        self.bosses[:] = [b for b in self.bosses if b.health > 0]

    def _check_team_progress(self):
        for p in self.players:
            if p.health <= 0 or p.y > GAME_HEIGHT:
                self._consume_shared_life(p)

        require_all = bool(self.rules.get("coop", {}).get("require_all_players_at_exit", True))
        if self.mode == "host":
            reached = [p.reached_exit for p in self.players]
            if (require_all and all(reached)) or ((not require_all) and any(reached)):
                self._start_victory_cutscene()
        else:
            if self.player.reached_exit:
                self._start_victory_cutscene()

    def _consume_shared_life(self, player):
        if self.mode == "single":
            self.game_over = True
            self._stop_bgm()
            return

        if self.shared_lives > 0:
            self.shared_lives -= 1
            player.health = player.max_health
            player.reset_to_spawn()
        else:
            self.game_over = True
            self.paused = False
            self._stop_bgm()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._stop_bgm()
                self.net.close()
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not self.paused:
                    self.paused = True
                    self.pause_state = "main"
                else:
                    if self.pause_state == "main":
                        self.paused = False
                    else:
                        self.pause_state = "main"
                continue

            if self.mode != "client":
                if self.victory_done and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self._restart_game()
                    continue
                if self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self._restart_game()
                    continue

            if self.paused:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.pause_state == "main":
                        self._handle_pause_click_main(event.pos)
                    elif self.pause_state == "options":
                        self._handle_pause_click_options(event.pos)
                continue

            if event.type == INVINCIBLE_END:
                for p in self.players:
                    p.invincible = False
            elif event.type == SHOOTING_END:
                for p in self.players:
                    p.shooting = False
            elif event.type == ATTACKING_END:
                for p in self.players:
                    p.attacking = False
                    p.attack_rect = None

    def _restart_game(self):
        pygame.time.set_timer(INVINCIBLE_END, 0)
        pygame.time.set_timer(SHOOTING_END, 0)
        pygame.time.set_timer(ATTACKING_END, 0)
        self._init_world()
        self.game_over = False
        self.victory_cutscene = False
        self.victory_done = False
        self.paused = False
        self.pause_state = "main"
        self._start_bgm()

    def _start_victory_cutscene(self):
        self.victory_cutscene = True
        self.victory_done = False
        self.player.velocity_x = 0
        self.player.velocity_y = 0
        self.player.jumping = False
        self.player.direction = "right"

    def _update_victory_cutscene(self):
        self.player.direction = "right"
        self.player.x += 2
        if self.player.x > GAME_WIDTH + self.player.width:
            self.victory_cutscene = False
            self.victory_done = True
            self._stop_bgm()

    def _draw_score(self):
        if self.mode == "host":
            text = f"Score: {self.player.score + self.player2.score}"
        else:
            text = str(self.player.score)
        text_surface = self.score_font.render(text, True, (204, 153, 0))
        text_rect = text_surface.get_rect(topright=(GAME_WIDTH - 16, 12))
        self.window.blit(text_surface, text_rect)

        if self.mode in ("host", "client"):
            lives_text = self.score_font.render(f"Lives: {self.shared_lives}", True, (255, 240, 160))
            self.window.blit(lives_text, (16, 12))

    def _draw_connection_status(self, text):
        status = self.pause_text_font.render(text, True, (220, 240, 255))
        self.window.blit(status, (16, GAME_HEIGHT - 28))

    def _draw_pause_button(self, text, rect):
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        color = (95, 110, 140) if hovered else (70, 85, 110)
        pygame.draw.rect(self.window, color, rect, border_radius=8)
        pygame.draw.rect(self.window, (230, 230, 230), rect, 2, border_radius=8)

        label = self.pause_btn_font.render(text, True, (255, 255, 255))
        self.window.blit(label, label.get_rect(center=rect.center))

    def _draw_pause_menu(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.window.blit(overlay, (0, 0))

        if self.pause_state == "main":
            title = self.pause_title_font.render("PAUSED", True, (255, 255, 255))
            self.window.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 130)))

            for text, rect in self.pause_buttons_main:
                self._draw_pause_button(text, rect)

            tip = self.pause_text_font.render("Press ESC to resume", True, (235, 235, 235))
            self.window.blit(tip, tip.get_rect(center=(GAME_WIDTH // 2, 430)))
        else:
            title = self.pause_title_font.render("OPTIONS", True, (255, 255, 255))
            self.window.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 150)))

            status = self.pause_text_font.render(f"Music: {'ON' if self.pause_music_on else 'OFF'}", True, (255, 255, 210))
            self.window.blit(status, status.get_rect(center=(GAME_WIDTH // 2, 220)))

            for text, rect in self.pause_buttons_options:
                self._draw_pause_button(text, rect)

    def _draw_game_over(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.window.blit(overlay, (0, 0))

        title = self.game_over_title_font.render("GAME OVER", True, (240, 70, 70))
        self.window.blit(title, title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 30)))

        hint = self.game_over_text_font.render("Press E to restart", True, (245, 245, 245))
        self.window.blit(hint, hint.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 30)))

    def _draw_victory_screen(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.window.blit(overlay, (0, 0))

        title = self.victory_title_font.render("JOB'S DONE!", True, (255, 225, 120))
        self.window.blit(title, title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 30)))

        hint = self.victory_text_font.render("Press E to restart", True, (245, 245, 245))
        self.window.blit(hint, hint.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 30)))

    def _handle_pause_click_main(self, pos):
        for text, rect in self.pause_buttons_main:
            if rect.collidepoint(pos):
                if text == "Resume":
                    self.paused = False
                elif text == "Option":
                    self.pause_state = "options"
                elif text == "Exit Game":
                    self._stop_bgm()
                    self.net.close()
                    pygame.quit()
                    exit()

    def _handle_pause_click_options(self, pos):
        for text, rect in self.pause_buttons_options:
            if rect.collidepoint(pos):
                if text == "Toggle Music":
                    self.pause_music_on = not self.pause_music_on
                    if self.pause_music_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                elif text == "Back":
                    self.pause_state = "main"

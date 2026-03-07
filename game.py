import pygame
from sys import exit

from settings import FPS, GAME_WIDTH, GAME_HEIGHT, TILE_SIZE, INVINCIBLE_END, SHOOTING_END, ATTACKING_END, GAME_BGM_PATH, GAME_BGM_VOLUME, TIME_WARP_DURATION_MS, GAME_FONT_PATH
from controls import handle_player_movement
from physics import move
from render import draw
from player import Player
from images import player_image_right
from map import create_map
# from enemy import Enemy

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        self._init_world()
        pygame.display.set_icon(player_image_right)
        pygame.display.set_caption("Samurai-bot")

        self.paused = False
        self.pause_state = "main"  # main | options
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
        self.game_over_title_font = pygame.font.Font(GAME_FONT_PATH, 56)
        self.game_over_title_font.set_bold(True)
        self.game_over_text_font = pygame.font.Font(GAME_FONT_PATH, 28)
        self.game_over_text_font.set_bold(True)
        self.victory_cutscene = False
        self.victory_done = False
        self.victory_title_font = pygame.font.Font(GAME_FONT_PATH, 56)
        self.victory_title_font.set_bold(True)
        self.victory_text_font = pygame.font.Font(GAME_FONT_PATH, 28)
        self.victory_text_font.set_bold(True)
        self.score_font = pygame.font.Font(GAME_FONT_PATH, 24)
        self.score_font.set_bold(True)

        self._start_bgm()

    def _init_world(self):
        self.player = Player()
        self.enemies = []
        self.enemies2 = []
        self.tiles = []
        self.background_tiles = []
        self.items = []
        self.spikes = []
        self.drones = []
        self.bosses = []
        create_map(self.player, self.background_tiles, self.tiles, self.enemies, self.enemies2, self.spikes, self.drones, self.bosses)

    def _start_bgm(self):
        try:
            pygame.mixer.music.load(GAME_BGM_PATH)
            pygame.mixer.music.set_volume(GAME_BGM_VOLUME)
            # print("[BGM] loading:", bgm_path, "exists=", os.path.exists(bgm_path))
            pygame.mixer.music.play(-1)  # loop
            print("[BGM] playing")
        except Exception as e:
            print("[BGM] ERROR:", e)

    def _stop_bgm(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
    
    def run(self):
        while True:
            self.handle_events()

            if not self.paused and not self.game_over and not self.victory_cutscene and not self.victory_done:
                handle_player_movement(self.player, self.background_tiles, self.tiles, self.enemies, self.enemies2, self.items, self.spikes, self.drones, self.bosses)
                move(self.player, self.tiles, self.enemies, self.enemies2, self.player.shurikens, self.items, self.spikes, self.drones, self.bosses)
                if self.player.reached_exit:
                    self._start_victory_cutscene()
            elif self.victory_cutscene:
                self._update_victory_cutscene()

            draw(self.window, self.player, self.background_tiles, self.tiles, self.enemies, self.enemies2, self.player.shurikens, self.items, self.spikes, self.drones, self.bosses)
            self._draw_score()
            if self.game_over:
                self._draw_game_over()
            elif self.victory_done:
                self._draw_victory_screen()
            elif self.paused:
                self._draw_pause_menu()

            pygame.display.update()
            self.clock.tick(FPS)
            if not self.game_over and getattr(self.player, "health", 1) <= 0:
                self.game_over = True
                self.paused = False
                self._stop_bgm()
            # print(pygame.time.get_ticks())
            elif not self.game_over and self.player.y > GAME_HEIGHT:
                self.player.health = 0
                self.game_over = True
                self.paused = True
                self._stop_bgm()
                
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._stop_bgm()
                pygame.quit()
                exit()

            if self.victory_done:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self._restart_game()
                continue

            if self.victory_cutscene:
                continue

            if self.game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self._restart_game()
                continue

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

            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                self.player.activate_time_warp(TIME_WARP_DURATION_MS)
                continue

            if self.paused:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.pause_state == "main":
                        self._handle_pause_click_main(event.pos)
                    elif self.pause_state == "options":
                        self._handle_pause_click_options(event.pos)
                continue

            if event.type == INVINCIBLE_END:
                self.player.invincible = False
            elif event.type == SHOOTING_END:
                self.player.shooting = False
            elif event.type == ATTACKING_END:
                self.player.attacking = False
                self.player.attack_rect = None

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
        text_surface = self.score_font.render(str(self.player.score), True, (204, 153, 0))
        text_rect = text_surface.get_rect(topright=(GAME_WIDTH - 16, 12))
        self.window.blit(text_surface, text_rect)
    
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
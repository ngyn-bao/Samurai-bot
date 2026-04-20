import pygame
from settings import GAME_WIDTH, GAME_HEIGHT, GAME_FONT_PATH
from rules import load_rules
from player_skins import get_selectable_skins


class MainMenu:
    def __init__(self, window):
        self.window = window
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.Font(GAME_FONT_PATH, 56)
        self.font_title.set_bold(True)
        self.font_btn = pygame.font.Font(GAME_FONT_PATH, 32)
        self.font_btn.set_bold(True)
        self.font_text = pygame.font.Font(GAME_FONT_PATH, 24)
        self.font_input = pygame.font.Font(GAME_FONT_PATH, 22)

        rules = load_rules()
        self.default_host = str(rules.get("network", {}).get("default_host", "127.0.0.1"))
        self.default_port = int(rules.get("network", {}).get("port", 5055))
        self.join_host = self.default_host

        selected = rules.get("skins", {}).get("selected", {})
        self.available_skins = get_selectable_skins()
        self.skin_p1 = str(selected.get("player1", "samurai"))
        self.skin_p2 = str(selected.get("player2", "samurai-2"))
        if self.skin_p1 not in self.available_skins:
            self.skin_p1 = self.available_skins[0]
        if self.skin_p2 not in self.available_skins:
            self.skin_p2 = self.available_skins[0]
        self.pending_start_action = None

        self.state = "main"  # main | options | about | join | skin
        self.music_on = True

        self.menu_music_loaded = False
        try:
            pygame.mixer.music.load("music/menu_music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            self.menu_music_loaded = True
        except Exception:
            self.menu_music_loaded = False

        self.bg = self._load_background()

        self.buttons_main = [
            ("New Game", pygame.Rect(GAME_WIDTH // 2 - 120, 165, 240, 44)),
            ("Co-op Host", pygame.Rect(GAME_WIDTH // 2 - 120, 215, 240, 44)),
            ("Co-op Join", pygame.Rect(GAME_WIDTH // 2 - 120, 265, 240, 44)),
            ("Option", pygame.Rect(GAME_WIDTH // 2 - 120, 315, 240, 44)),
            ("About", pygame.Rect(GAME_WIDTH // 2 - 120, 365, 240, 44)),
            ("Exit", pygame.Rect(GAME_WIDTH // 2 - 120, 415, 240, 44)),
        ]

        self.buttons_options = [
            ("Toggle Music", pygame.Rect(GAME_WIDTH // 2 - 140, 280, 280, 52)),
            ("Back", pygame.Rect(GAME_WIDTH // 2 - 140, 350, 280, 52)),
        ]

        self.buttons_about = [
            ("Back", pygame.Rect(GAME_WIDTH // 2 - 140, 430, 280, 52)),
        ]

        self.buttons_join = [
            ("Connect", pygame.Rect(GAME_WIDTH // 2 - 140, 350, 280, 52)),
            ("Back", pygame.Rect(GAME_WIDTH // 2 - 140, 420, 280, 52)),
        ]

        self.skin_buttons = {
            "p1_prev": pygame.Rect(GAME_WIDTH // 2 - 180, 220, 44, 44),
            "p1_next": pygame.Rect(GAME_WIDTH // 2 + 136, 220, 44, 44),
            "p2_prev": pygame.Rect(GAME_WIDTH // 2 - 180, 300, 44, 44),
            "p2_next": pygame.Rect(GAME_WIDTH // 2 + 136, 300, 44, 44),
            "start": pygame.Rect(GAME_WIDTH // 2 - 140, 390, 280, 52),
            "back": pygame.Rect(GAME_WIDTH // 2 - 140, 455, 280, 52),
        }

    def _load_background(self):
        try:
            img = pygame.image.load("images/background-menu.jpg").convert()
            return pygame.transform.smoothscale(img, (GAME_WIDTH, GAME_HEIGHT))
        except Exception:
            return None

    def _draw_bg(self):
        if self.bg:
            self.window.blit(self.bg, (0, 0))
        else:
            self.window.fill((20, 20, 30))

    def _draw_button(self, text, rect):
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        color = (90, 120, 180) if hovered else (60, 80, 120)
        pygame.draw.rect(self.window, color, rect, border_radius=8)
        pygame.draw.rect(self.window, (220, 220, 220), rect, 2, border_radius=8)

        label = self.font_btn.render(text, True, (255, 255, 255))
        self.window.blit(label, label.get_rect(center=rect.center))

    def _draw_title(self, text, center):
        pulse = 1.0 + 0.03 * (pygame.time.get_ticks() % 1200) / 600.0
        if pulse > 1.03:
            pulse = 2.06 - pulse

        title_surface = self.font_title.render(text, True, (128, 128, 128))
        w = int(title_surface.get_width() * pulse)
        h = int(title_surface.get_height() * pulse)
        title_surface = pygame.transform.smoothscale(title_surface, (w, h))
        title_rect = title_surface.get_rect(center=center)

        outline_surface = self.font_title.render(text, True, (12, 18, 30))
        outline_surface = pygame.transform.smoothscale(outline_surface, (w, h))
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            self.window.blit(outline_surface, title_rect.move(ox, oy))

        glow_surface = self.font_title.render(text, True, (128, 0, 0))
        glow_surface = pygame.transform.smoothscale(glow_surface, (w, h))
        glow_surface.set_alpha(120)
        for gx, gy in [(-5, 0), (5, 0), (0, -4), (0, 4)]:
            self.window.blit(glow_surface, title_rect.move(gx, gy))

        self.window.blit(title_surface, title_rect)

    def _draw_main(self):
        self._draw_bg()
        self._draw_title("SAMURAI-BOT", (GAME_WIDTH // 2, 120))
        for text, rect in self.buttons_main:
            self._draw_button(text, rect)

    def _draw_options(self):
        self._draw_bg()
        title = self.font_title.render("OPTIONS", True, (255, 255, 255))
        self.window.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 140)))

        status = self.font_text.render(
            f"Music: {'ON' if self.music_on else 'OFF'}", True, (255, 255, 200)
        )
        self.window.blit(status, status.get_rect(center=(GAME_WIDTH // 2, 230)))

        for text, rect in self.buttons_options:
            self._draw_button(text, rect)

    def _draw_about(self):
        self._draw_bg()
        title = self.font_title.render("ABOUT", True, (255, 255, 255))
        self.window.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 120)))

        lines = [
            "SAMURAI-BOT",
            "A game made by: Group 6",
        ]
        y = 220
        for line in lines:
            txt = self.font_text.render(line, True, (230, 230, 230))
            self.window.blit(txt, txt.get_rect(center=(GAME_WIDTH // 2, y)))
            y += 36

        for text, rect in self.buttons_about:
            self._draw_button(text, rect)

    def _draw_join(self):
        self._draw_bg()
        title = self.font_title.render("CO-OP JOIN", True, (255, 255, 255))
        self.window.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 120)))

        tip = self.font_text.render("Enter host IP address", True, (230, 230, 230))
        self.window.blit(tip, tip.get_rect(center=(GAME_WIDTH // 2, 190)))

        input_rect = pygame.Rect(GAME_WIDTH // 2 - 180, 230, 360, 48)
        pygame.draw.rect(self.window, (25, 30, 45), input_rect, border_radius=8)
        pygame.draw.rect(self.window, (220, 220, 220), input_rect, 2, border_radius=8)

        host_text = self.font_input.render(self.join_host, True, (240, 240, 240))
        self.window.blit(host_text, (input_rect.x + 12, input_rect.y + 12))

        port_text = self.font_text.render(f"Port: {self.default_port}", True, (220, 220, 180))
        self.window.blit(port_text, port_text.get_rect(center=(GAME_WIDTH // 2, 305)))

        for text, rect in self.buttons_join:
            self._draw_button(text, rect)

    def _draw_skin_select(self):
        self._draw_bg()
        title = self.font_title.render("SELECT SKIN", True, (255, 255, 255))
        self.window.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 120)))

        p1_text = self.font_text.render(f"P1: {self.skin_p1}", True, (240, 240, 240))
        self.window.blit(p1_text, p1_text.get_rect(center=(GAME_WIDTH // 2, 242)))

        p2_text = self.font_text.render(f"P2: {self.skin_p2}", True, (200, 235, 255))
        self.window.blit(p2_text, p2_text.get_rect(center=(GAME_WIDTH // 2, 322)))

        self._draw_button("<", self.skin_buttons["p1_prev"])
        self._draw_button(">", self.skin_buttons["p1_next"])
        self._draw_button("<", self.skin_buttons["p2_prev"])
        self._draw_button(">", self.skin_buttons["p2_next"])
        self._draw_button("Start", self.skin_buttons["start"])
        self._draw_button("Back", self.skin_buttons["back"])

    def _cycle_skin(self, current, step):
        if not self.available_skins:
            return current
        idx = self.available_skins.index(current)
        return self.available_skins[(idx + step) % len(self.available_skins)]

    def _handle_click_main(self, pos):
        for text, rect in self.buttons_main:
            if rect.collidepoint(pos):
                if text == "New Game":
                    if self.menu_music_loaded:
                        pygame.mixer.music.stop()
                    return {
                        "action": "newgame",
                        "selected_skins": {
                            "player1": self.skin_p1,
                            "player2": self.skin_p2,
                        },
                    }
                if text == "Co-op Host":
                    if self.menu_music_loaded:
                        pygame.mixer.music.stop()
                    skin1 = self.available_skins[0] if self.available_skins else "samurai"
                    skin2 = self.available_skins[1] if len(self.available_skins) > 1 else skin1
                    return {
                        "action": "coop_host",
                        "host": "0.0.0.0",
                        "port": self.default_port,
                        "selected_skins": {
                            "player1": skin1,
                            "player2": skin2,
                        },
                    }
                if text == "Co-op Join":
                    self.state = "join"
                    return None
                if text == "Option":
                    self.state = "options"
                elif text == "About":
                    self.state = "about"
                elif text == "Exit":
                    if self.menu_music_loaded:
                        pygame.mixer.music.stop()
                    return {"action": "exit"}
        return None

    def _handle_click_options(self, pos):
        for text, rect in self.buttons_options:
            if rect.collidepoint(pos):
                if text == "Toggle Music":
                    self.music_on = not self.music_on
                    if self.menu_music_loaded:
                        if self.music_on:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                elif text == "Back":
                    self.state = "main"

    def _handle_click_about(self, pos):
        for text, rect in self.buttons_about:
            if rect.collidepoint(pos):
                if text == "Back":
                    self.state = "main"

    def _handle_click_join(self, pos):
        for text, rect in self.buttons_join:
            if rect.collidepoint(pos):
                if text == "Connect":
                    if self.menu_music_loaded:
                        pygame.mixer.music.stop()
                    host = self.join_host.strip() or self.default_host
                    return {"action": "coop_join", "host": host, "port": self.default_port}
                if text == "Back":
                    self.state = "main"
        return None

    def _handle_click_skin(self, pos):
        if self.skin_buttons["p1_prev"].collidepoint(pos):
            self.skin_p1 = self._cycle_skin(self.skin_p1, -1)
            return None
        if self.skin_buttons["p1_next"].collidepoint(pos):
            self.skin_p1 = self._cycle_skin(self.skin_p1, 1)
            return None
        if self.skin_buttons["p2_prev"].collidepoint(pos):
            self.skin_p2 = self._cycle_skin(self.skin_p2, -1)
            return None
        if self.skin_buttons["p2_next"].collidepoint(pos):
            self.skin_p2 = self._cycle_skin(self.skin_p2, 1)
            return None
        if self.skin_buttons["start"].collidepoint(pos):
            action = self.pending_start_action or "newgame"
            return {
                "action": action,
                "host": self.default_host,
                "port": self.default_port,
                "selected_skins": {
                    "player1": self.skin_p1,
                    "player2": self.skin_p2,
                },
            }
        if self.skin_buttons["back"].collidepoint(pos):
            self.state = "main"
            self.pending_start_action = None
        return None

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {"action": "exit"}

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == "main":
                        return {"action": "exit"}
                    if self.state == "skin":
                        self.pending_start_action = None
                    self.state = "main"

                if self.state == "join" and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.join_host = self.join_host[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.menu_music_loaded:
                            pygame.mixer.music.stop()
                        host = self.join_host.strip() or self.default_host
                        return {"action": "coop_join", "host": host, "port": self.default_port}
                    else:
                        ch = event.unicode
                        if ch and ch in "0123456789.:abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-":
                            if len(self.join_host) < 40:
                                self.join_host += ch

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "main":
                        action = self._handle_click_main(event.pos)
                        if action:
                            return action
                    elif self.state == "options":
                        self._handle_click_options(event.pos)
                    elif self.state == "about":
                        self._handle_click_about(event.pos)
                    elif self.state == "join":
                        action = self._handle_click_join(event.pos)
                        if action:
                            return action
                    elif self.state == "skin":
                        action = self._handle_click_skin(event.pos)
                        if action:
                            if self.menu_music_loaded:
                                pygame.mixer.music.stop()
                            return action

            if self.state == "main":
                self._draw_main()
            elif self.state == "options":
                self._draw_options()
            elif self.state == "join":
                self._draw_join()
            elif self.state == "skin":
                self._draw_skin_select()
            else:
                self._draw_about()

            pygame.display.update()
            self.clock.tick(60)

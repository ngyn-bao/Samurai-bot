import pygame
from settings import GAME_WIDTH, GAME_HEIGHT, GAME_FONT_PATH


class MainMenu:
    def __init__(self, window):
        self.window = window
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.Font(GAME_FONT_PATH, 56)
        self.font_title.set_bold(True)
        self.font_btn = pygame.font.Font(GAME_FONT_PATH, 32)
        self.font_btn.set_bold(True)
        self.font_text = pygame.font.Font(GAME_FONT_PATH, 24)

        self.state = "main"  # main | options | about
        self.music_on = True

        self.menu_music_loaded = False
        try:
            pygame.mixer.music.load("music/menu_music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # loop
            self.menu_music_loaded = True
        except Exception:
            self.menu_music_loaded = False

        self.bg = self._load_background()

        self.buttons_main = [
            ("New Game", pygame.Rect(GAME_WIDTH // 2 - 120, 220, 240, 52)),
            ("Option", pygame.Rect(GAME_WIDTH // 2 - 120, 290, 240, 52)),
            ("About", pygame.Rect(GAME_WIDTH // 2 - 120, 360, 240, 52)),
            ("Exit", pygame.Rect(GAME_WIDTH // 2 - 120, 430, 240, 52)),
        ]

        self.buttons_options = [
            ("Toggle Music", pygame.Rect(GAME_WIDTH // 2 - 140, 280, 280, 52)),
            ("Back", pygame.Rect(GAME_WIDTH // 2 - 140, 350, 280, 52)),
        ]

        self.buttons_about = [
            ("Back", pygame.Rect(GAME_WIDTH // 2 - 140, 430, 280, 52)),
        ]

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
        # Pulse title scale for subtle arcade-style motion.
        pulse = 1.0 + 0.03 * (pygame.time.get_ticks() % 1200) / 600.0
        if pulse > 1.03:
            pulse = 2.06 - pulse

        title_surface = self.font_title.render(text, True, (128, 128, 128))
        w = int(title_surface.get_width() * pulse)
        h = int(title_surface.get_height() * pulse)
        title_surface = pygame.transform.smoothscale(title_surface, (w, h))
        title_rect = title_surface.get_rect(center=center)

        # Thin dark outline to keep the title readable on bright backgrounds.
        outline_surface = self.font_title.render(text, True, (12, 18, 30))
        outline_surface = pygame.transform.smoothscale(outline_surface, (w, h))
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            self.window.blit(outline_surface, title_rect.move(ox, oy))

        # Cyan glow layer behind the title.
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

    def _handle_click_main(self, pos):
        for text, rect in self.buttons_main:
            if rect.collidepoint(pos):
                if text == "New Game":
                    if self.menu_music_loaded:
                        pygame.mixer.music.stop()
                    return "newgame"
                if text == "Option":
                    self.state = "options"
                elif text == "About":
                    self.state = "about"
                elif text == "Exit":
                    if self.menu_music_loaded:
                        pygame.mixer.music.stop()
                    return "exit"
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

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == "main":
                        return "exit"
                    self.state = "main"

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "main":
                        action = self._handle_click_main(event.pos)
                        if action in ("newgame", "exit"):
                            return action
                    elif self.state == "options":
                        self._handle_click_options(event.pos)
                    elif self.state == "about":
                        self._handle_click_about(event.pos)

            if self.state == "main":
                self._draw_main()
            elif self.state == "options":
                self._draw_options()
            else:
                self._draw_about()

            pygame.display.update()
            self.clock.tick(60)

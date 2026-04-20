# import pygame
# from game import Game

# pygame.init()

# game = Game()
# game.run()
import pygame
from game import Game
from menu import MainMenu
from settings import GAME_WIDTH, GAME_HEIGHT
from rules import load_rules

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

menu = MainMenu(window)
action = menu.run()
rules = load_rules()

if action.get("action") == "newgame":
    game = Game(mode="single", rules=rules, selected_skins=action.get("selected_skins"))
    game.run()
elif action.get("action") == "coop_host":
    game = Game(mode="host", host=action.get("host", "0.0.0.0"), port=action.get("port", rules.get("network", {}).get("port", 5055)), rules=rules, selected_skins=action.get("selected_skins"))
    game.run()
elif action.get("action") == "coop_join":
    game = Game(mode="client", host=action.get("host", rules.get("network", {}).get("default_host", "127.0.0.1")), port=action.get("port", rules.get("network", {}).get("port", 5055)), rules=rules)
    game.run()
else:
    pygame.quit()
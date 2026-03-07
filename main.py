# import pygame
# from game import Game

# pygame.init()

# game = Game()
# game.run()
import pygame
from game import Game
from menu import MainMenu
from settings import GAME_WIDTH, GAME_HEIGHT

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))

menu = MainMenu(window)
action = menu.run()

if action == "newgame":
    game = Game()
    game.run()
else:
    pygame.quit()
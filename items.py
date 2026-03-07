import pygame
import random
from settings import TILE_SIZE, ITEM_VELOCITY_Y
from tile import Tile
from images import big_life_energy_image, life_energy_image, time_warp_item_image, item_box_image, score_ball_image


class Item(pygame.Rect):
    def __init__(self, x, y, image, effect_type=None):
        pygame.Rect.__init__(self, x, y, image.get_width(), image.get_height())
        self.image = image
        self.effect_type = effect_type
        self.jumping = False
        self.used = False
        self.velocity_y = ITEM_VELOCITY_Y


class ItemBox(Tile):
    def __init__(self, x, y):
        super().__init__(x, y, item_box_image)
        self.is_item_box = True
        self.opened = False

def drop_item(character, items):
    random_number = random.randint(1, 100) #inclusive of 100
    if 0 < random_number <= 15:
        items.append(Item(character.x, character.y, big_life_energy_image))
    elif 15 < random_number <= 47:
        items.append(Item(character.x, character.y, life_energy_image))
    elif 47 < random_number <= 50:
        items.append(Item(character.x, character.y, time_warp_item_image, effect_type="time_warp"))
    elif 50 < random_number <= 75:
        items.append(Item(character.x, character.y, score_ball_image))

def drop_item_from_box(box, items):
    random_number = random.randint(1, 100)
    if random_number <= 30:
        items.append(Item(box.x, box.y, big_life_energy_image))
    elif random_number <= 95:
        items.append(Item(box.x, box.y, life_energy_image))
    else:
        items.append(Item(box.x, box.y, time_warp_item_image, effect_type="time_warp"))
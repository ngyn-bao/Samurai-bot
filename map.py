import pygame
from tile import Tile
from enemy import Metall, Drone, Infantryman, SpiderBoss
from settings import TILE_SIZE, GAME_MAP
from items import ItemBox
from images import floor_tile_image, spike_image, rock_tile1_image, rock_tile2_image, rock_tile3_image, rock_tile4_image, door_tile_image, beam_tile_image, room_tile_image, wall_tile_image

def append_tiles(map_code, background_tiles, tiles, tile):
    tile.kind = getattr(tile, "kind", "rock1")
    if map_code < 0:
        background_tiles.append(tile)
    else:
        tiles.append(tile)


def create_map(player, background_tiles, tiles, enemies, enemies2, spikes, drones, bosses):
    for col in range(len(GAME_MAP[0])):
        for row in range(len(GAME_MAP)):
            map_code = GAME_MAP[row][col]
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            if map_code == 0:
                continue #empty tile
            elif abs(map_code) == 1:
                t = Tile(x, y, rock_tile1_image)
                t.kind = "rock1"
                append_tiles(map_code, background_tiles, tiles, t)
            elif abs(map_code) == 2:
                t = Tile(x, y, rock_tile2_image)
                t.kind = "rock2"
                append_tiles(map_code, background_tiles, tiles, t)
            elif abs(map_code) == 3:
                t = Tile(x, y, rock_tile3_image)
                t.kind = "rock3"
                append_tiles(map_code, background_tiles, tiles, t)
            elif abs(map_code) == 4:
                t = Tile(x, y, rock_tile4_image)
                t.kind = "rock4"
                append_tiles(map_code, background_tiles, tiles, t)
            elif abs(map_code) == 5:
                t = Tile(x, y, floor_tile_image)
                t.kind = "floor"
                append_tiles(map_code, background_tiles, tiles, t)
            elif abs(map_code) == 6:
                t = Tile(x, y, wall_tile_image)
                t.kind = "wall"
                append_tiles(map_code, background_tiles, tiles, t)
            elif map_code == 7:
                t = Tile(x, y, beam_tile_image)
                t.kind = "beam"
                background_tiles.append(t)
            elif map_code == 8:
                t = Tile(x, y, spike_image)
                t.kind = "spike"
                spikes.append(t)
            elif map_code == 9:
                door_tile = Tile(x, y, door_tile_image)
                door_tile.kind = "door"
                door_tile.is_door = True
                door_tile.is_open = False
                tiles.append(door_tile)
            elif map_code == 10:
                t = Tile(x, y, room_tile_image)
                t.kind = "room"
                background_tiles.append(t)
            elif map_code == 11:
                enemies.append(Metall(x, y))
            elif map_code == 12:
                drones.append(Drone(x, y))
            elif map_code == 13:
                enemies2.append(Infantryman(x, y))
            elif map_code == 14:
                bosses.append(SpiderBoss(x, y))
            elif map_code == 15:
                box = ItemBox(x, y)
                box.kind = "item_box"
                tiles.append(box)
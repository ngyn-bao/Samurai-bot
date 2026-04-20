import os
import pygame

from rules import load_rules
from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_JUMP_WIDTH, PLAYER_JUMP_HEIGHT, PLAYER_ATTACK_WIDTH, PLAYER_ATTACK_HEIGHT

_REQUIRED_PARTS = [
    "right",
    "left",
    "jump_right",
    "jump_left",
    "attack_right",
    "attack_left",
    "hit_right",
    "hit_left",
]

_SIZE_BY_PART = {
    "right": (PLAYER_WIDTH, PLAYER_HEIGHT),
    "left": (PLAYER_WIDTH, PLAYER_HEIGHT),
    "jump_right": (PLAYER_JUMP_WIDTH, PLAYER_JUMP_HEIGHT),
    "jump_left": (PLAYER_JUMP_WIDTH, PLAYER_JUMP_HEIGHT),
    "attack_right": (PLAYER_ATTACK_WIDTH, PLAYER_ATTACK_HEIGHT),
    "attack_left": (PLAYER_ATTACK_WIDTH, PLAYER_ATTACK_HEIGHT),
    "hit_right": (PLAYER_WIDTH, PLAYER_HEIGHT),
    "hit_left": (PLAYER_WIDTH, PLAYER_HEIGHT),
}

_DEFAULT_SKIN = {
    "right": "samurai-right.png",
    "left": "samurai-left.png",
    "jump_right": "samurai-right-jump.png",
    "jump_left": "samurai-left-jump.png",
    "attack_right": "samurai-right-attack.png",
    "attack_left": "samurai-left-attack.png",
    "hit_right": "samurai-gethit-right.png",
    "hit_left": "samurai-gethit-left.png",
}

_SKIN_CACHE = {}


def _skin_file_map(skin_id):
    if skin_id == "samurai":
        return dict(_DEFAULT_SKIN)

    prefix = skin_id
    return {
        "right": f"{prefix}-right.png",
        "left": f"{prefix}-left.png",
        "jump_right": f"{prefix}-right-jump.png",
        "jump_left": f"{prefix}-left-jump.png",
        "attack_right": f"{prefix}-right-attack.png",
        "attack_left": f"{prefix}-left-attack.png",
        "hit_right": f"{prefix}-gethit-right.png",
        "hit_left": f"{prefix}-gethit-left.png",
    }


def _load_scaled(file_name, size):
    image = pygame.image.load(os.path.join("images", file_name)).convert_alpha()
    return pygame.transform.scale(image, size)


def load_player_skin(skin_id):
    skin_id = skin_id or "samurai"
    if skin_id in _SKIN_CACHE:
        return _SKIN_CACHE[skin_id]

    file_map = _skin_file_map(skin_id)
    surfaces = {}
    for part in _REQUIRED_PARTS:
        size = _SIZE_BY_PART[part]
        try:
            surfaces[part] = _load_scaled(file_map[part], size)
        except Exception:
            surfaces[part] = _load_scaled(_DEFAULT_SKIN[part], size)

    _SKIN_CACHE[skin_id] = surfaces
    return surfaces


def get_selectable_skins():
    rules = load_rules()
    configured = rules.get("skins", {}).get("available", ["samurai", "samurai-2"])
    skins = []
    for skin_id in configured:
        if skin_id not in skins:
            skins.append(str(skin_id))
    if "samurai" not in skins:
        skins.insert(0, "samurai")
    return skins

import json
from pathlib import Path

DEFAULT_RULES = {
    "coop": {
        "enabled": True,
        "require_all_players_at_exit": True,
        "shared_lives": 2,
        "friendly_fire": False,
    },
    "network": {
        "default_host": "127.0.0.1",
        "port": 5055,
    },
    "time_warp": {
        "duration_ms": 4000,
        "max_charges": 3,
        "enemy_speed_multiplier": 0.5,
    },
    "skins": {
        "available": ["samurai", "samurai-2"],
        "selected": {
            "player1": "samurai",
            "player2": "samurai-2"
        }
    }
}


def _deep_update(dst, src):
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            _deep_update(dst[key], value)
        else:
            dst[key] = value
    return dst


def load_rules(path="rules.json"):
    rules = json.loads(json.dumps(DEFAULT_RULES))
    file_path = Path(path)
    if file_path.exists():
        try:
            with file_path.open("r", encoding="utf-8") as f:
                user_rules = json.load(f)
            _deep_update(rules, user_rules)
        except Exception:
            pass
    return rules

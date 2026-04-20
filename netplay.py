import json
import socket
import time
import select
import errno


class NetSession:
    def __init__(self, mode="single", host="127.0.0.1", port=5055):
        self.mode = mode
        self.host = host
        self.port = int(port)

        self.server_socket = None
        self.peer_socket = None
        self.read_buffer = ""
        self.connected = False
        self.last_message = None
        self.last_connect_attempt = 0.0
        self.reconnect_interval = 1.0

        if mode == "host":
            self._start_host()
        elif mode == "client":
            self._start_client()

    def _start_host(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False)

    def _configure_peer_socket(self, sock):
        sock.setblocking(False)
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError:
            pass

    def _start_client(self):
        self._attempt_client_connect()

    def _attempt_client_connect(self):
        now = time.monotonic()
        if self.peer_socket is not None:
            return
        if now - self.last_connect_attempt < self.reconnect_interval:
            return

        self.last_connect_attempt = now
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.setblocking(False)
            err = sock.connect_ex((self.host, self.port))

            if err in (0, errno.EISCONN):
                self._configure_peer_socket(sock)
                self.peer_socket = sock
                self.connected = True
                self.read_buffer = ""
                return

            in_progress = {
                getattr(errno, "EINPROGRESS", 10035),
                getattr(errno, "EWOULDBLOCK", 10035),
                getattr(errno, "EALREADY", 10037),
                10035,
                10036,
                10037,
            }
            if err not in in_progress:
                raise OSError(err, "connect_ex failed")

            _, writable, _ = select.select([], [sock], [], 0.2)
            if not writable:
                raise OSError("connect timeout")

            so_error = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if so_error != 0:
                raise OSError(so_error, "connect failed")

            self._configure_peer_socket(sock)
            self.peer_socket = sock
            self.connected = True
            self.read_buffer = ""
        except OSError:
            sock.close()
            self.connected = False

    def poll_client_connect(self):
        if self.mode == "client" and self.peer_socket is None:
            self._attempt_client_connect()

    def close(self):
        if self.peer_socket is not None:
            try:
                self.peer_socket.close()
            except OSError:
                pass
        self.peer_socket = None

        if self.server_socket is not None:
            try:
                self.server_socket.close()
            except OSError:
                pass
        self.server_socket = None
        self.connected = False

    def poll_connect(self):
        if self.mode != "host" or self.server_socket is None or self.peer_socket is not None:
            return
        try:
            client, _ = self.server_socket.accept()
            self._configure_peer_socket(client)
            self.peer_socket = client
            self.connected = True
            self.read_buffer = ""
        except BlockingIOError:
            return
        except OSError:
            return

    def send(self, payload):
        if self.peer_socket is None:
            return
        data = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        try:
            self.peer_socket.sendall(data)
        except BlockingIOError:
            return
        except OSError:
            self._drop_peer()

    def poll_receive(self):
        if self.mode == "client" and self.peer_socket is None:
            self._attempt_client_connect()
            return None

        if self.peer_socket is None:
            return None

        got_data = False
        for _ in range(32):
            try:
                chunk = self.peer_socket.recv(65536)
            except BlockingIOError:
                break
            except OSError:
                self._drop_peer()
                return None

            if not chunk:
                self._drop_peer()
                return None

            got_data = True
            self.read_buffer += chunk.decode("utf-8", errors="ignore")

        if not got_data:
            return None

        if "\n" not in self.read_buffer:
            return None

        lines = self.read_buffer.split("\n")
        self.read_buffer = lines[-1]

        latest = None
        for line in lines[:-1]:
            line = line.strip()
            if not line:
                continue
            try:
                latest = json.loads(line)
            except json.JSONDecodeError:
                continue

        self.last_message = latest
        return latest

    def _drop_peer(self):
        if self.peer_socket is not None:
            try:
                self.peer_socket.close()
            except OSError:
                pass
        self.peer_socket = None
        self.connected = False
        self.read_buffer = ""


def player_to_dict(player):
    return {
        "id": getattr(player, "player_id", 1),
        "skin_id": getattr(player, "skin_id", "samurai"),
        "x": player.x,
        "y": player.y,
        "w": player.width,
        "h": player.height,
        "direction": player.direction,
        "jumping": player.jumping,
        "attacking": player.attacking,
        "invincible": player.invincible,
        "health": player.health,
        "max_health": player.max_health,
        "score": player.score,
        "time_warp_charges": player.time_warp_charges,
        "time_warp_active": player.is_time_warp_active(),
        "reached_exit": player.reached_exit,
        "shurikens": [
            {"x": s.x, "y": s.y, "w": s.width, "h": s.height, "direction": 1 if s.velocity_x >= 0 else -1}
            for s in player.shurikens
            if not getattr(s, "used", False)
        ],
    }


def world_snapshot(game):
    return {
        "players": [player_to_dict(p) for p in game.players],
        "enemies": [
            {
                "x": e.x,
                "y": e.y,
                "direction": getattr(e, "direction", "left"),
                "guarding": getattr(e, "guarding", False),
                "bullets": [{"x": b.x, "y": b.y, "w": b.width, "h": b.height} for b in getattr(e, "bullets", [])],
            }
            for e in game.enemies
        ],
        "enemies2": [
            {
                "x": e.x,
                "y": e.y,
                "direction": getattr(e, "direction", "left"),
                "state": getattr(e, "state", "patrol"),
                "bullets": [{"x": b.x, "y": b.y, "w": b.width, "h": b.height} for b in getattr(e, "bullets", [])],
            }
            for e in game.enemies2
        ],
        "drones": [
            {"x": d.x, "y": d.y, "direction": getattr(d, "direction", "right")}
            for d in game.drones
        ],
        "bosses": [
            {
                "x": b.x,
                "y": b.y,
                "health": getattr(b, "health", 0),
                "max_health": getattr(b, "max_health", 1),
                "projectiles": [{"x": p.x, "y": p.y, "w": p.width, "h": p.height} for p in getattr(b, "projectiles", []) if getattr(p, "alive", True)],
            }
            for b in game.bosses
        ],
        "items": [
            {
                "x": i.x,
                "y": i.y,
                "effect_type": getattr(i, "effect_type", None),
                "w": i.width,
                "h": i.height,
            }
            for i in game.items
            if not getattr(i, "used", False)
        ],
        "tiles": [{"x": t.x, "y": t.y, "w": t.width, "h": t.height, "kind": getattr(t, "kind", "rock1")} for t in game.tiles],
        "background_tiles": [{"x": t.x, "y": t.y, "w": t.width, "h": t.height, "kind": getattr(t, "kind", "rock1")} for t in game.background_tiles],
        "spikes": [{"x": s.x, "y": s.y, "w": s.width, "h": s.height} for s in game.spikes],
        "game_over": game.game_over,
        "victory_cutscene": game.victory_cutscene,
        "victory_done": game.victory_done,
        "shared_lives": game.shared_lives,
    }

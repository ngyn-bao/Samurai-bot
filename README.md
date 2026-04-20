# Samurai-bot

## Che do choi

- Single player: choi 1 nguoi nhu cu.
- Co-op Host: tao phong, game chay mo phong o may host.
- Co-op Join: ket noi vao host bang IP.

## Dieu khien

- Di chuyen: `A/D` hoac mui ten trai/phai
- Nhay: `W` hoac mui ten len
- Chem: `Space`
- Nem shuriken: `X`
- Time Warp: `C`

## Chinh luat choi

Sua file `rules.json`:

```json
{
  "coop": {
    "require_all_players_at_exit": true,
    "shared_lives": 2
  },
  "network": {
    "default_host": "127.0.0.1",
    "port": 5055
  },
  "time_warp": {
    "duration_ms": 4000,
    "max_charges": 3,
    "enemy_speed_multiplier": 0.5
  }
}
```

- `require_all_players_at_exit`: `true` => ca 2 nguoi phai den cua thoat, `false` => chi can 1 nguoi.
- `shared_lives`: so mang chung cua team trong che do co-op.
- `network.port`: cong mang de host/client dong bo.
- `time_warp.duration_ms`: thoi gian hieu luc Time Warp (ms).
- `time_warp.max_charges`: so lan Time Warp toi da co the tich.
- `time_warp.enemy_speed_multiplier`: he so toc do enemy khi Time Warp dang bat (0.5 = cham 50%).

## Chay game

1. Cai thu vien:

```bash
pip install -r requirements.txt
```

1. Chay:

```bash
python main.py
```

1. Tren may Host: chon `Co-op Host`.
1. Tren may Client: chon `Co-op Join`, nhap IP cua host.

## Ghi chu

- Host la ben mo phong logic game va gui snapshot cho client.
- Neu client mat ket noi, host van tiep tuc choi duoc.

# Audio-Module

Low-latency local audio bridge for Matcha (LuaVM) and Roblox.

---

## 1. Quick Start

1. Run **`AudioServer.exe`** on your machine.
   - Runs in the background (Windows System Tray).
   - Right-click tray icon to check status or exit.
2. In Matcha, load the client bridge:

```lua
loadstring(game:HttpGet("https://raw.githubusercontent.com/WhyMayko/Audio-Module/main/Audio.luau"))()
-- `Audio` is now directly available globally, or:
-- local Audio = loadstring(...)() or Audio
```

---

## 2. API (`Audio`)

### `Audio:Get(name, url)`
Caches audio on disk and decodes into RAM buffers.
```lua
-- Single
Audio:Get("hit", "https://raw.githubusercontent.com/Kittywy/Neverlose.cc-hitsounds/main/wav/aimbooster.wav")

-- Batch
Audio:Get({
    hit = "https://raw.githubusercontent.com/Kittywy/Neverlose.cc-hitsounds/main/wav/aimbooster.wav",
    kill = "https://raw.githubusercontent.com/Kittywy/Neverlose.cc-hitsounds/main/wav/bonk.wav"
})
```

### `Audio:Play(name, volume, duration)`
Plays audio instantly in a free voice channel.
```lua
Audio:Play("hit")
Audio:Play("hit", 0.8)        -- 80% volume
Audio:Play("hit", 1.0, 0.15)  -- Cuts off at 150ms
```

### `Audio:Stop(name)`
Stops audio playback.
```lua
Audio:Stop("hit") -- Stop specific sound
Audio:Stop()      -- Stop all playing sounds
```

### `Audio:Status()`
Returns current server state.
```lua
local state = Audio:Status()
-- { ok = true, busy = 0, cached = { "hit", "kill" } }
```

---

## 3. Files

- **`AudioServer.exe`**: Ready-to-run Windows background service (System Tray).
- **`server.py`**: Python source code (`pygame-ce` mixer on port `6767`).
- **`Audio.luau`**: Client bridge for Matcha.

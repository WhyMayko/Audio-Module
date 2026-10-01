import os
import json
import time
import socket
import hashlib
import threading
import urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import pygame
import pystray
from PIL import Image, ImageDraw

PORT = 6767
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
pygame.mixer.init()
pygame.mixer.set_num_channels(128)

COLOR_WAITING = (180, 180, 180, 255)
COLOR_CONNECTED = (40, 215, 120, 255)

sounds = {}
connected = False
last_ping = 0
tray_icon = None

def create_icon(color):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(2, 5), (6, 5), (10, 2), (10, 13), (6, 10), (2, 10)], fill=color)
    d.arc([(9, 3), (14, 12)], -60, 60, fill=color, width=2)
    return img

def update_tray():
    if tray_icon:
        tray_icon.icon = create_icon(COLOR_CONNECTED if connected else COLOR_WAITING)
        tray_icon.update_menu()

def get_file_ext(url):
    clean = url.split("?")[0].split("#")[0]
    ext = os.path.splitext(clean)[1].lower()
    return ext if ext in [".wav", ".mp3", ".ogg"] else ".mp3"

def cache_and_load(name, url):
    if not isinstance(url, str) or not (url.startswith("http://") or url.startswith("https://")):
        return None

    ext = get_file_ext(url)
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    file_path = os.path.join(CACHE_DIR, f"{h}{ext}")

    if not os.path.exists(file_path):
        req = urllib.request.Request(url, headers={"User-Agent": "AudioModule/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        with open(file_path, "wb") as f:
            f.write(data)

    sound = pygame.mixer.Sound(file_path)
    sounds[name] = sound
    return sound

class FastServer(ThreadingHTTPServer):
    daemon_threads = True

    def server_bind(self):
        super().server_bind()
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def get_request(self):
        sock, addr = super().get_request()
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock, addr

class AudioHandler(BaseHTTPRequestHandler):
    def address_string(self):
        return self.client_address[0]

    def log_message(self, format, *args):
        pass

    def send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def do_GET(self):
        global connected, last_ping
        last_ping = time.time()
        if not connected:
            connected = True
            update_tray()

        if self.path == "/status":
            self.send_json({"ok": True, "cached": list(sounds.keys())})

    def do_POST(self):
        global connected, last_ping
        last_ping = time.time()
        if not connected:
            connected = True
            update_tray()

        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        body = json.loads(raw) if raw else {}
        path = self.path

        if path == "/play":
            name = body["name"]
            channel = pygame.mixer.find_channel(force=True)
            if channel:
                channel.set_volume(body.get("volume", 1.0))
                channel.play(sounds[name], maxtime=int(body.get("duration", 0) * 1000))
            self.send_json({"ok": True})

        elif path == "/get":
            audios = body.get("audios")
            if isinstance(audios, dict):
                for name, url in audios.items():
                    cache_and_load(name, url)
            else:
                cache_and_load(body["name"], body["url"])
            update_tray()
            self.send_json({"ok": True, "cached": list(sounds.keys())})

        elif path == "/stop":
            name = body.get("name")
            if name:
                sounds[name].stop()
            else:
                pygame.mixer.stop()
            self.send_json({"ok": True})

        elif path == "/status":
            self.send_json({"ok": True, "cached": list(sounds.keys())})

def run():
    global tray_icon

    server = FastServer(("127.0.0.1", PORT), AudioHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    def monitor():
        global connected
        while True:
            time.sleep(1)
            if connected and (time.time() - last_ping > 10):
                connected = False
                sounds.clear()
                update_tray()

    threading.Thread(target=monitor, daemon=True).start()

    def on_exit(icon, item):
        icon.stop()
        pygame.mixer.quit()
        server.shutdown()
        server.server_close()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem(lambda text: "connected" if connected else "waiting", None, enabled=False),
        pystray.MenuItem(lambda text: f"cached: {len(sounds)}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("exit", on_exit)
    )

    tray_icon = pystray.Icon("AudioModule", create_icon(COLOR_WAITING), "Audio Module", menu)
    tray_icon.run()

if __name__ == "__main__":
    run()

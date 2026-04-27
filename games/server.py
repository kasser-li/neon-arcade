#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8888
DIRECTORY = "/root/.openclaw/workspace/games"

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        file_path = os.path.join(DIRECTORY, self.path.lstrip('/'))
        if not os.path.exists(file_path) and not self.path.startswith('/games/'):
            self.path = '/index.html'
        return super().do_GET()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("0.0.0.0", PORT), SPAHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}/")
        httpd.serve_forever()

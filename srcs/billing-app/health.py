"""Minimal liveness endpoint so the billing-app container is reachable on
port 8080, as required by the play-with-containers spec. The service's real
job — consuming billing_queue — has no HTTP surface by design; this thread
only proves the container is up.
"""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def log_message(self, *args):
        pass


def start_health_server(host="0.0.0.0", port=8080):
    server = HTTPServer((host, port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

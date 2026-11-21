import json
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
DEFAULT_PORT = 8000


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self.send_json(404, {"error": "Not found"})


def create_server(port: int = DEFAULT_PORT) -> HTTPServer:
    return HTTPServer((HOST, port), Handler)


def serve() -> None:
    raise Exception("Not implemented")

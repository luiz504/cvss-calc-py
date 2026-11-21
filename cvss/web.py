from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
DEFAULT_PORT = 8000


class Handler(BaseHTTPRequestHandler):
    def some_method(self) -> None:
        raise Exception("Not Implemented")


def create_server(port: int = DEFAULT_PORT) -> HTTPServer:
    return HTTPServer((HOST, port), Handler)


def serve() -> None:
    raise Exception("Not implemented")

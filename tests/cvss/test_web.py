import json
import threading
import urllib
import urllib.error
import urllib.request
from collections.abc import Iterator

import pytest

from cvss.web import create_server


@pytest.fixture
def base_url() -> Iterator[str]:
    server = create_server(port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
    thread.start()

    yield f"http://127.0.0.1:{server.server_address[1]}"

    server.shutdown()
    server.server_close()
    thread.join()


def request(method: str, url: str, body: bytes | None = None) -> tuple[int, str, bytes]:
    http_request = urllib.request.Request(url, data=body, method=method)

    try:
        with urllib.request.urlopen(http_request) as response:
            return response.status, response.headers["Content-Type"], response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers["Content-Type"], error.read()


def test_server_binds_to_loopback_only() -> None:
    server = create_server(port=0)

    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


def test_unknown_get_path_returns_404(base_url: str) -> None:
    status, _, body = request("GET", base_url + "/nope")

    assert status == 404
    assert json.loads(body) == {"error": "Not found"}

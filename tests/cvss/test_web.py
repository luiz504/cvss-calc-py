import threading
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

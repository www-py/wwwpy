import logging
import socket

from wwwpy.server import tcp_port

logger = logging.getLogger(__name__)


def test_is_port_busy():
    port = tcp_port.find_port()
    assert not tcp_port.is_port_busy(port)


def test_port_is_busy():
    port = tcp_port.find_port()

    with socket.create_server(('0.0.0.0', port)) as s:
        assert tcp_port.is_port_busy(port)

    assert not tcp_port.is_port_busy(port)


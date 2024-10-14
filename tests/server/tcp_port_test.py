from wwwpy.server import tcp_port


def test_is_port_busy():
    port = tcp_port.find_port()
    assert not tcp_port.is_port_busy(port)


def test_port_is_busy():
    port = tcp_port.find_port()
    with tcp_port.socket.socket(tcp_port.socket.AF_INET, tcp_port.socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', port))
        assert tcp_port.is_port_busy(port)

    assert not tcp_port.is_port_busy(port)
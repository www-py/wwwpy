from wwwpy.remote import component as wpc


class RpcIssueAlert(wpc.Component):
    def init_component(self):
        # language=html
        self.element.innerHTML = """
<h2>Server.rpc issue:
The package server.rpc is not completely supported by the hot-reload yet.
It is necessary to restart the server process.
<a href='https://github.com/www-py/wwwpy/issues/6' target='_blank'>See and vote the github issue</a>
</h2>

        """
        self.element.style.display = 'none'
        try:
            from server import rpc
        except ImportError as e:
            self.element.style.display = 'block'

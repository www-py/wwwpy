messages_listeners = []


class Rpc:
    def new_message(self, msg: str):
        for listener in messages_listeners:
            listener(msg)

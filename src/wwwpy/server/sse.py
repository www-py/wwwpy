# server-side events - implementation for the server
def create_event(data, event_type=None):
    if data is None or data == "":
        raise ValueError("Data field cannot be empty")

    event_str = ""
    if event_type:
        event_str += f"event: {event_type}\n"
    if data:
        for line in data.splitlines():
            event_str += f"data: {line}\n"
    event_str += "\n"
    return event_str

import asyncio


class _DropZoneSelector:
    def __init__(self):
        self._future = None

    def start(self):
        """It starts the process for the user to select a drop zone.
        While moving the mouse, it highlights the drop zones.
        It will intercept (and prevent) the mouse click event.
        On such a mouse click event, it will stop the process and set the result.
        """
        self._future = asyncio.Future()

    def stop(self):
        """It stops the process of selecting a drop zone.
        It will remove the highlights and the event listener.
        """

    async def result(self):
        """It returns the result. It could be:
        - the drop zone if selected
        - None if the process was stopped before selection
        """
        pass


drop_zone_selector = _DropZoneSelector()

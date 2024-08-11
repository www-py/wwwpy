# Filesystem-sync

This package serves to monitor a filesystem and propagate changes to another filesystem to keep them in sync.

The source and target filesystems are assumed to be on different machines and there is a small part that serializes the filesystem changes to be sent over the transport (e.g., network)

The source filesystem is monitored using [watchdog](https://pypi.org/project/watchdog/).

There are in essence two parts:
- one part to debounce the filesystem events to avoid frenzied activity
- one part that takes in the debounced events and propagates them to the target filesystem

Both parts have tests and are tested in isolation.

## Debounce
This is a general implementation that keeps a buffer and notifies the observer when a timeout is reached.

## Sync
Take a look to the [Sync](src/filesystem_sync/sync.py) protocol
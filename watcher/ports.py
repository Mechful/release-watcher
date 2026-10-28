from typing import Protocol

from .domain import Release


class ReleaseSource(Protocol):
    def latest(self, repo: str) -> Release | None:
        """Latest published release of `repo`, or None if it has none."""


class Notifier(Protocol):
    def send(self, release: Release) -> None: ...


class StateStore(Protocol):
    def get(self, repo: str) -> str | None:
        """Last tag we already notified about (or seeded) for `repo`."""

    def set(self, repo: str, tag: str) -> None: ...

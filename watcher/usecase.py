import logging
from dataclasses import dataclass

from .ports import Notifier, ReleaseSource, StateStore

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RunSummary:
    sent: int = 0
    failed: int = 0


class CheckForNewReleases:
    def __init__(
        self, source: ReleaseSource, notifier: Notifier, state: StateStore
    ) -> None:
        self._source = source
        self._notifier = notifier
        self._state = state

    def run(self, repos: list[str]) -> RunSummary:
        sent = failed = 0
        for repo in repos:
            try:
                sent += self._check(repo)
            except Exception:
                failed += 1
                log.exception("Failed to process %s", repo)
        return RunSummary(sent=sent, failed=failed)

    def _check(self, repo: str) -> int:
        release = self._source.latest(repo)
        if release is None:
            log.info("%s: no releases found, skipping", repo)
            return 0

        seen = self._state.get(repo)
        if seen == release.tag:
            return 0

        if seen is None:
            # First time we see this repo: remember the current release
            # silently so adding a repo doesn't trigger a notification.
            log.info("%s: seeding at %s", repo, release.tag)
            self._state.set(repo, release.tag)
            return 0

        self._notifier.send(release)
        # Only advance state after a successful send, so failures retry next run.
        self._state.set(repo, release.tag)
        log.info("%s: notified %s", repo, release.tag)
        return 1

"""Composition root: the only place that knows about concrete adapters."""
import logging
import os
import sys
from pathlib import Path

from .adapters.discord_notifier import DiscordWebhookNotifier
from .adapters.github_source import GitHubReleaseSource
from .adapters.json_state_store import JsonFileStateStore
from .usecase import CheckForNewReleases

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("release-watcher")


def load_repos(path: Path) -> list[str]:
    lines = (line.split("#")[0].strip() for line in path.read_text().splitlines())
    return [line for line in lines if line]


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    use_case = CheckForNewReleases(
        source=GitHubReleaseSource(token=os.environ.get("GITHUB_TOKEN")),
        notifier=DiscordWebhookNotifier(os.environ["DISCORD_WEBHOOK_URL"]),
        state=JsonFileStateStore(ROOT / "state.json"),
    )
    summary = use_case.run(load_repos(ROOT / "repos.txt"))
    log.info("Done: %d sent, %d failed", summary.sent, summary.failed)
    return 1 if summary.failed else 0


if __name__ == "__main__":
    sys.exit(main())

import json
import time
import urllib.error
import urllib.request

from ..domain import Release

MAX_DESCRIPTION = 4000  # Discord's hard limit is 4096


class DiscordWebhookNotifier:
    def __init__(
        self, webhook_url: str, color: int = 0x5865F2, timeout: int = 15
    ) -> None:
        self._url = webhook_url
        self._color = color
        self._timeout = timeout

    def send(self, release: Release) -> None:
        self._post({"username": "Release Watcher", "embeds": [self._embed(release)]})

    def _embed(self, r: Release) -> dict:
        body = r.body.strip()
        if len(body) > MAX_DESCRIPTION:
            body = body[: MAX_DESCRIPTION - 1].rstrip() + "…"

        embed: dict = {
            "title": f"{r.repo} {r.tag}"[:256],
            "url": r.url,
            "description": body or "*No release notes provided.*",
            "color": self._color,
        }
        if r.name and r.name != r.tag:
            embed["footer"] = {"text": r.name[:2048]}
        if r.published_at:
            embed["timestamp"] = r.published_at
        if r.author:
            embed["author"] = {"name": r.author}
            if r.author_avatar_url:
                embed["author"]["icon_url"] = r.author_avatar_url
        return embed

    def _post(self, payload: dict, retries: int = 1) -> None:
        req = urllib.request.Request(
            self._url,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                # Discord/Cloudflare may reject the default Python user agent.
                "User-Agent": "release-watcher/1.0",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=self._timeout).close()
        except urllib.error.HTTPError as e:
            if e.code == 429 and retries > 0:
                wait = float(json.load(e).get("retry_after", 1))
                time.sleep(min(wait, 30))
                return self._post(payload, retries - 1)
            raise

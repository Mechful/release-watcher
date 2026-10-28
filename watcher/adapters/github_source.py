import json
import urllib.error
import urllib.request

from ..domain import Release


class GitHubReleaseSource:
    """Reads the latest non-draft, non-prerelease release via the GitHub REST API."""

    def __init__(self, token: str | None = None, timeout: int = 15) -> None:
        self._token = token
        self._timeout = timeout

    def latest(self, repo: str) -> Release | None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "release-watcher",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/releases/latest", headers=headers
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 404:  # no releases (or repo missing)
                return None
            raise

        author = data.get("author") or {}
        return Release(
            repo=repo,
            tag=data["tag_name"],
            name=data.get("name") or data["tag_name"],
            url=data["html_url"],
            body=data.get("body") or "",
            published_at=data.get("published_at"),
            author=author.get("login"),
            author_avatar_url=author.get("avatar_url"),
        )

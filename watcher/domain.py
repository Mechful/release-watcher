from dataclasses import dataclass


@dataclass(frozen=True)
class Release:
    repo: str  # "owner/name"
    tag: str
    name: str
    url: str
    body: str
    published_at: str | None  # ISO 8601, as returned by GitHub
    author: str | None
    author_avatar_url: str | None

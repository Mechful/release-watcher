import json
from pathlib import Path


class JsonFileStateStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, str] = (
            json.loads(path.read_text()) if path.exists() else {}
        )

    def get(self, repo: str) -> str | None:
        return self._data.get(repo)

    def set(self, repo: str, tag: str) -> None:
        self._data[repo] = tag
        self._path.write_text(json.dumps(self._data, indent=2, sort_keys=True) + "\n")

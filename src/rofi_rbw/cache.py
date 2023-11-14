from typing import List

from .entry import Entry
from .paths import cache_file


class Cache:
    def __init__(self, entries: List[Entry]):
        cache_file.parent.mkdir(exist_ok=True)
        cache_file.touch(exist_ok=True)

        self.cache = {entry.sha1: [0, entry] for entry in entries}

        with cache_file.open() as f:
            for line in f:
                if line.strip():
                    n, sha1 = line.strip().split(" ", maxsplit=1)
                    if sha1 in self.cache:
                        self.cache[sha1][0] = int(n)

    def sorted(self) -> List[Entry]:
        return [
            e
            for _, e in sorted(
                self.cache.values(),
                key=lambda t: t[0],
                reverse=True,
            )
        ]

    def update(self, entry: Entry):
        self.cache[entry.sha1][0] += 1
        with cache_file.open("w") as f:
            for n, e in self.cache.values():
                f.write(f"{n} {e.sha1}\n")

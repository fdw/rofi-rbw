from collections import defaultdict
from typing import List

from .paths import cache_file


class Cache:
    def __init__(self):
        cache_file.parent.mkdir(exist_ok=True)
        cache_file.touch(exist_ok=True)

        self.cache = []

        with cache_file.open() as f:
            for line in f:
                if line.strip():
                    n, entry = line.strip().split(" ", maxsplit=1)
                    self.cache.append((int(n), entry))

    def sort(self, entries: List[str]) -> List[str]:
        for _, entry in self.cache:
            if entry in entries:
                entries.remove(entry)
                entries = [entry, *entries]

        return entries

    def update(self, entry: str):
        entries = defaultdict(int, {e: n for n, e in self.cache})
        entries[entry] += 1
        with cache_file.open("w") as f:
            for n, e in sorted((n, e) for e, n in entries.items()):
                print(n, e, file=f)

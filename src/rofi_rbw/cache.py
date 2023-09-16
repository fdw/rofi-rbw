from collections import defaultdict
from typing import List

from .entry import Entry
from .paths import cache_file


class Cache:
    def __init__(self):
        cache_file.parent.mkdir(exist_ok=True)
        cache_file.touch(exist_ok=True)

        self.cache = []

        with cache_file.open() as f:
            for line in f:
                if line.strip():
                    n, hashed_entry = line.strip().split(" ", maxsplit=1)
                    self.cache.append((int(n), hashed_entry))

    def sort(self, entries: List[Entry]) -> List[Entry]:
        hashed_entries = {entry.sha1: entry for entry in entries}
        for _, hashed_entry in self.cache:
            if hashed_entry in hashed_entries.keys():
                entries.remove(hashed_entries[hashed_entry])
                entries = [hashed_entries[hashed_entry], *entries]

        return entries

    def update(self, entry: Entry):
        hashed_entries = defaultdict(int, {h: n for n, h in self.cache})
        hashed_entries[entry.sha1] += 1
        lines = [(n, h) for h, n in hashed_entries.items()]
        with cache_file.open("w") as f:
            for n, e in sorted(lines):
                f.write(f"{n} {e}")

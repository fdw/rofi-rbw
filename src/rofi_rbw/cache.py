from math import floor
from typing import List

from .entry import Entry
from .paths import cache_file


class Cache:
    def __init__(self):
        cache_file.parent.mkdir(exist_ok=True)
        self.cache = dict()

    def sorted(self, entries: List[Entry]) -> List[Entry]:
        entries = {entry.hashed: entry for entry in entries}
        sorted_entries = []

        if cache_file.exists():
            with cache_file.open() as f:
                for line in f:
                    sline = line.strip()
                    if sline:
                        n, hashed = sline.split(" ", maxsplit=1)
                        try:
                            sorted_entries.append(entries.pop(hashed))
                            self.cache[hashed] = int(n)
                        except KeyError:
                            pass

        return [*sorted_entries, *entries.values()]

    def update(self, entry: Entry):
        self.cache[entry.hashed] = self.cache.get(entry.hashed, 0) + 1.1

        with cache_file.open("w") as f:
            for hashed, n in sorted(self.cache.items(), key=lambda i: i[1], reverse=True):
                f.write(f"{floor(n)} {hashed}\n")

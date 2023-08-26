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
                    n, entry = line.strip().split(" ", maxsplit=1)
                    self.cache.append((int(n), Entry.parse(entry, use_markup=True)))

    def sort(self, entries: List[Entry]) -> List[Entry]:
        for _, entry in self.cache:
            if entry in entries:
                entries.remove(entry)
                entries = [entry, *entries]

        return entries

    def update(self, entry: Entry):
        entries = defaultdict(int, {e: n for n, e in self.cache})
        entries[entry] += 1
        lines = [(n, e.format(0, True, True)) for e, n in entries.items()]
        with cache_file.open("w") as f:
            for n, e in sorted(lines):
                print(n, e, file=f)

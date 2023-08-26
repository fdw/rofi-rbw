from collections import defaultdict
from typing import List, Tuple

from .paths import cache_file


def read_cache() -> List[Tuple[int, str]]:
    cache_file.parent.mkdir(exist_ok=True)
    cache_file.touch(exist_ok=True)

    cache = []

    with cache_file.open() as f:
        for line in f:
            if line.strip():
                n, entry = line.strip().split(" ", maxsplit=1)
                cache.append((int(n), entry))

    return cache


def cached_entries_first(cache: List[Tuple[int, str]], entries: List[str]) -> List[str]:
    for _, entry in cache:
        if entry in entries:
            entries.remove(entry)
            entries = [entry, *entries]

    return entries


def update_cache(cache: List[Tuple[int, str]], entry: str):
    entries = defaultdict(int, {e: n for n, e in cache})
    entries[entry] += 1
    with cache_file.open("w") as f:
        for n, e in sorted((n, e) for e, n in entries.items()):
            print(n, e, file=f)

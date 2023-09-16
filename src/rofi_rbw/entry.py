from dataclasses import dataclass
from functools import cached_property
from hashlib import sha1
from typing import Optional


@dataclass(frozen=True)
class Entry:
    name: str
    folder: Optional[str] = ""
    username: Optional[str] = ""

    @cached_property
    def sha1(self) -> str:
        m = sha1()
        m.update(self.name.encode())
        m.update(self.folder.encode())
        m.update(self.username.encode())
        return m.hexdigest()

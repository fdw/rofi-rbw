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
    def hashed(self) -> str:
        m = sha1()
        m.update(self.name.encode())
        if self.folder:
            m.update(self.folder.encode())
        if self.username:
            m.update(self.username.encode())
        return m.hexdigest()

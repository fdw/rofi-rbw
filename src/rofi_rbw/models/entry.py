from dataclasses import dataclass
from functools import cached_property
from hashlib import sha1


@dataclass(frozen=True)
class Entry:
    name: str
    folder: str = ""
    username: str = ""

    @cached_property
    def hashed(self) -> str:
        m = sha1()
        m.update(self.name.encode())
        if self.folder:
            m.update(self.folder.encode())
        if self.username:
            m.update(self.username.encode())
        return m.hexdigest()

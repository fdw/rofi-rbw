from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Entry:
    name: str
    folder: Optional[str] = ""
    username: Optional[str] = ""
    length: int = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        object.__setattr__(self, "length", len(self.name) + len(self.folder) + 1)

    def __len__(self) -> int:
        return self.length

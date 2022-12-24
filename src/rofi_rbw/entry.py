from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Entry:
    name: str
    folder: Optional[str] = ""
    username: Optional[str] = ""

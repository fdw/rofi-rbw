from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Entry:
    name: str
    folder: Optional[str] = ""
    username: Optional[str] = ""

    def format(self, max_width: int, show_folders: bool, use_markup: bool):
        folder = f"{self.folder}/" if show_folders and self.folder else ""
        name = f"<b>{self.name}</b>" if use_markup else self.name
        start = f"{folder}{name}"
        return f"{start:<{max_width}}  {self.username}"

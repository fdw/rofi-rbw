from re import compile
from dataclasses import dataclass
from typing import Optional

RE = compile("(?:(?P<folder>.+?)/)?(?P<name>.*?)? *  (?P<username>.*)?")
RE_MARKUP = compile("(?:(?P<folder>.+?)/)?<b>(?P<name>.*)</b> *  (?P<username>.*)?")


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

    @staticmethod
    def parse(formatted_string: str, use_markup: bool) -> "Entry":
        match = (RE_MARKUP if use_markup else RE).search(formatted_string)
        return Entry(**match.groupdict())

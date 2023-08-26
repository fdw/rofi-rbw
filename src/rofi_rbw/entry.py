from dataclasses import dataclass
from re import compile
from typing import Optional

RE = compile("(?:(?P<folder>.+)/)?<b>(?P<name>.*)</b> *  (?P<username>.+)?")
RE_NO_M = compile("(?:(?P<folder>.+)/)?(?P<name>.*?)? *  (?P<username>.+)?")


@dataclass(frozen=True)
class Entry:
    name: str
    folder: Optional[str] = ""
    username: Optional[str] = ""

    def format(self, max_width: int, show_folders: bool, use_markup: bool) -> str:
        """Format this Entry as str.

        >>> entry = Entry(name="test", folder="path/sub", username="joe")
        >>> entry.format(40, True, True)
        'path/sub/<b>test</b>                      joe'
        >>> entry.format(40, False, True)
        '<b>test</b>                               joe'
        >>> entry.format(40, True, False)
        'path/sub/test                             joe'
        >>> entry.format(0, True, True)
        'path/sub/<b>test</b>  joe'
        >>> entry = Entry(name="name_only")
        >>> entry.format(40, True, True)
        '<b>name_only</b>                          '
        """

        folder = f"{self.folder}/" if show_folders and self.folder else ""
        name = f"<b>{self.name}</b>" if use_markup else self.name
        start = f"{folder}{name}"
        return f"{start:<{max_width}}  {self.username}"

    @staticmethod
    def parse(formatted_string: str, use_markup: bool) -> "Entry":
        """Parse str as Entry.

        >>> Entry.parse('path/sub/<b>test</b>  joe', True)
        Entry(name='test', folder='path/sub', username='joe')
        >>> Entry.parse('path/sub/<b>test</b>                      joe', True)
        Entry(name='test', folder='path/sub', username='joe')
        >>> Entry.parse('path/sub/test                             joe', False)
        Entry(name='test', folder='path/sub', username='joe')
        >>> Entry.parse('<b>name_only</b>                          ', True)
        Entry(name='name_only', folder=None, username=None)
        """

        match = (RE if use_markup else RE_NO_M).search(formatted_string)
        return Entry(**match.groupdict())


if __name__ == "__main__":
    import doctest

    doctest.testmod()

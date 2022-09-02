import re
from dataclasses import dataclass, field
from re import Pattern
from typing import ClassVar, Optional


@dataclass(frozen=True)
class Entry:
    parsing_regex: ClassVar[Pattern] = re.compile('(?P<folder>.*)/<b>(?P<name>.*)</b>(?P<username>.*)')

    name: str
    folder: Optional[str] = ''
    username: Optional[str] = ''
    length: int = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        object.__setattr__(self, 'length', len(self.name) + len(self.folder) + 1)

    def __len__(self) -> int:
        return self.length

    def formatted_string(self, max_width: int) -> str:
        return f'{self.folder}/<b>{self.name.ljust(max_width - len(self.folder))}</b>{self.username}'

    @staticmethod
    def parse_formatted_string(formatted_string: str) -> 'Entry':
        match = Entry.parsing_regex.search(formatted_string)

        return Entry(
            match.group('name').strip(),
            match.group('folder'),
            match.group('username').strip()
        )

    @staticmethod
    def parse_rbw_output(rbw_string: str) -> 'Entry':
        fields = rbw_string.split('\t')

        try:
            return Entry(
                fields[1],
                fields[0],
                fields[2] if len(fields) > 2 else ''
            )
        except IndexError:
            raise Exception('Entry is incorrectly formatted and cannot be parsed')

import re


class Entry:
    def __init__(self, name: str = '', folder: str = '', username: str = '') -> None:
        self.name = name
        self.folder = folder
        self.username = username
        self.length = len(self.name) + len(self.folder) + 1

    def __len__(self) -> int:
        return self.length

    def formatted_string(self, max_width: int) -> str:
        return f'{self.folder}/<b>{self.name.ljust(max_width - len(self.folder))}</b>{self.username}'

    @staticmethod
    def parse_formatted_string(formatted_string: str) -> 'Entry':
        regex = re.compile('(?P<folder>.*)/<b>(?P<name>.*)</b>(?P<username>.*)')
        match = regex.search(formatted_string)

        return Entry(
            match.group('name').strip(),
            match.group('folder'),
            match.group('username').strip()
        )

    @staticmethod
    def parse_rbw_output(rbw_string: str) -> 'Entry':
        fields = rbw_string.split('\t')

        return Entry(
            fields[1],
            fields[0],
            fields[2] if len(fields) > 2 else ''
        )

import re
from subprocess import run

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

    @classmethod
    def parse_formatted_string(cls, formatted_string: str) -> 'Entry':
        regex = re.compile('(?P<folder>.*)/<b>(?P<name>.*)</b>(?P<username>.*)')
        match = regex.search(formatted_string)

        return cls(
            match.group('name').strip(),
            match.group('folder'),
            match.group('username').strip()
        )

    @classmethod
    def get_list(cls) -> List['Entry']:
        rofi = run(
            ['rbw', 'ls', '--fields', 'folder,name,user'],
            encoding='utf-8',
            capture_output=True
        )

        if rofi.returncode != 0:
            print('There was a problem calling rbw. Is it correctly configured?')
            print(rofi.stderr)
            exit(2)

        return [cls.parse_rbw_output(it) for it in (rofi.stdout.strip().split('\n'))]

    @classmethod
    def parse_rbw_output(cls, rbw_string: str) -> 'Entry':
        fields = rbw_string.split('\t')

        try:
            return cls(
                fields[1],
                fields[0],
                fields[2] if len(fields) > 2 else ''
            )
        except IndexError:
            raise Exception('Entry is incorrectly formatted and cannot be parsed')

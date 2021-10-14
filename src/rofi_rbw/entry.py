from typing import Union, List


class Entry:

    def __init__(self, data: str) -> None:
        self.name = ''
        self.folder = ''
        self.username = ''

        fields = data.split('\t')
        self.name = fields[1]
        self.folder = fields[0]
        self.length = len(self.name) + len(self.folder) + 1

        try:
            self.username = fields[2]
        except IndexError:
            self.username = ''

    def __len__(self) -> int:
        return self.length

    def formatted_string(self, max_width: int) -> str:
        return f'{self.folder}/<b>{self.name.ljust(max_width - len(self.folder))}</b>{self.username}'

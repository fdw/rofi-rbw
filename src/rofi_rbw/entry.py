from typing import Union, List


class Entry:

    def __init__(self) -> None:
        self.name = ''
        self.folder = ''
        self.username = ''

    def __len__(self) -> int:
        return self.length

    def formatted_string(self, max_width: int) -> str:
        return f'{self.folder}/<b>{self.name.ljust(max_width - len(self.folder))}</b>{self.username}'

    def unformat_string(data: str):
        item = Entry()
        data = data.split('/<b>')
        item.folder = data[0]

        data = data[1].split('</b>')
        # Remove added padding spaces
        item.name = data[0].rstrip(' ')

        try:
            item.username = data[1]
        except IndexError:
            pass

        item.length = len(item.name) + len(item.folder) + 1
        return item

    def from_rbw(data: str):
        item = Entry()
        fields = data.split('\t')
        item.name = fields[1]
        item.folder = fields[0]

        try:
            item.username = fields[2]
        except IndexError:
            pass

        item.length = len(item.name) + len(item.folder) + 1
        return item

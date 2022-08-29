from subprocess import run
from typing import Union, Optional, List

from .models import Target, Targets
from .entry import Entry


class Credentials:
    def __init__(self, name: str, username: str, folder: Optional[str]) -> None:
        self.name = name
        self.folder = folder
        self.username = username

        self.password = ''
        self.has_totp = False
        self.uris = []
        self.further = {}

        self.__load_from_rbw()

    @classmethod
    def from_entry(cls, entry: Entry) -> 'Credentials':
        return Credentials(entry.name, entry.username, entry.folder)

    def __load_from_rbw(self):
        command = ['rbw', 'get', '--full', self.name]
        if self.username:
            command.append(self.username)

        if self.folder != "":
            command.extend(["--folder", self.folder])

        result = run(
            command,
            capture_output=True,
            encoding='utf-8'
        ).stdout

        self.__parse_rbw_output(result)

    def __parse_rbw_output(self, output: str):
        line, *rest = output.strip().split('\n')
        if len(line.split(": ", 1)) == 2:
            # First line contains ': ' and thus there is no password
            rest = [line] + rest
        else:
            self.password = line

        for line in rest:
            try:
                key, value = line.split(": ", 1)
                if key == "Username":
                    self.username = value
                elif key == "URI":
                    self.uris.append(value)
                elif key == "TOTP Secret":
                    self.has_totp = True
                elif key == 'Match type':
                    pass
                else:
                    self.further[key] = value
            except ValueError:
                pass

    def __getitem__(self, target: Target) -> Optional[Union[str, List[str]]]:
        if target == Targets.USERNAME:
            return self.username
        elif target == Targets.PASSWORD:
            return self.password
        elif target == Targets.TOTP:
            return self.totp
        elif target.is_uri():
            return self.uris[target.uri_index()]
        else:
            return self.further.get(target.raw, None)

    def to_menu_entries(self) -> List[str]:
        entries = []
        if self.username:
            entries.append(f'Username: {self.username}')
        if self.password:
            entries.append(f'Password: {self.password[0]}{"*" * (len(self.password) - 1)}')
        if self.has_totp:
            entries.append(f'TOTP: {self.totp}')
        if len(self.uris) == 1:
            entries.append(f'URI: {self.uris[0]}')
        else:
            for (key, value) in enumerate(self.uris):
                entries.append(f'URI {key + 1}: {value}')
        for (key, value) in self.further.items():
            entries.append(f'{key}: {value[0]}{"*" * (len(value) - 1)}')
        return entries

    @property
    def totp(self):
        if not self.has_totp:
            return ''

        command = ['rbw', 'code', self.name]
        if self.folder:
            command.extend(["--folder", self.folder])
        return run(
            command,
            capture_output=True,
            encoding='utf-8'
        ).stdout.strip()

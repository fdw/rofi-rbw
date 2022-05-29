from subprocess import run
from typing import Union, Optional, List

from .models import Target, Targets


class Credentials:
    def __init__(self, name: str, username: str, folder: Optional[str]) -> None:
        self.name = name
        self.folder = folder
        self.username = username

        self.password = ''
        self.has_totp = False
        self.uris = []
        self.further = {}

        self.__load_from_rbw(name, username, folder)

    def __load_from_rbw(self, name: str, username: str, folder: Optional[str]):
        command = ['rbw', 'get', '--full', name]
        if username:
            command.append(username)

        if folder != "":
            command.extend(["--folder", folder])

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

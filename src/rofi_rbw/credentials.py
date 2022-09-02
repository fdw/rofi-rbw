from dataclasses import dataclass, field
from subprocess import run
from typing import Union, Optional, List, Dict

from .entry import Entry
from .models import Target, Targets


@dataclass(frozen=True)
class Credentials(Entry):
    password: Optional[str] = ''
    has_totp: bool = False
    uris: List[str] = field(default_factory=list)
    further: Dict[str, str] = field(default_factory=dict)

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

    @staticmethod
    def from_entry(entry: Entry) -> 'Credentials':
        def __load_from_rbw(name: str, username: str, folder: Optional[str]) -> str:
            command = ['rbw', 'get', '--full', name]
            if username:
                command.append(username)

            if folder != "":
                command.extend(["--folder", folder])

            return run(
                command,
                capture_output=True,
                encoding='utf-8'
            ).stdout

        def __parse_output(line: str) -> None:
            try:
                key, value = line.split(": ", 1)
                if key == "URI":
                    uris.append(value)
                elif key == "TOTP Secret":
                    nonlocal has_totp
                    has_totp = True
                elif key == 'Match type' or key == 'username':
                    pass
                else:
                    further[key] = value
            except ValueError:
                pass

        password = ''
        has_totp = False
        uris = []
        further = {}

        line, *rest = __load_from_rbw(entry.name, entry.username, entry.folder).strip().split('\n')
        if len(line.split(": ", 1)) == 2:
            # First line contains ': ' and thus there is no password
            rest = [line] + rest
        else:
            password = line

        for line in rest:
            __parse_output(line)

        return Credentials(entry.name, entry.folder, entry.username, password, has_totp, uris, further)

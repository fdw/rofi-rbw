from subprocess import run
from typing import List, Optional

from credentials import Credentials
from entry import Entry


class Rbw:
    def list_entries(self) -> List[Entry]:
        rbw = run(
            ['rbw', 'ls', '--fields', 'folder,name,user'],
            encoding='utf-8',
            capture_output=True
        )

        if rbw.returncode != 0:
            print('There was a problem calling rbw. Is it correctly configured?')
            print(rbw.stderr)
            exit(2)

        return [self.__parse_rbw_output(it) for it in (rbw.stdout.strip().split('\n'))]

    def __parse_rbw_output(self, rbw_string: str) -> 'Entry':
        fields = rbw_string.split('\t')

        try:
            return Entry(
                fields[1],
                fields[0],
                fields[2] if len(fields) > 2 else ''
            )
        except IndexError:
            raise Exception('Entry is incorrectly formatted and cannot be parsed')

    def fetch_credentials(self, entry: Entry) -> 'Credentials':
        password = ''
        has_totp = False
        uris = []
        further = {}

        line, *rest = self.__load_from_rbw(entry.name, entry.username, entry.folder).strip().split('\n')
        if len(line.split(": ", 1)) == 2:
            # First line contains ': ' and thus there is no password
            rest = [line] + rest
        else:
            password = line

        for line in rest:
            try:
                key, value = line.split(": ", 1)
                if key == "URI":
                    uris.append(value)
                elif key == "TOTP Secret":
                    has_totp = True
                elif key == 'Match type' or key == 'username':
                    pass
                else:
                    further[key] = value
            except ValueError:
                pass
        return Credentials(entry.name, entry.folder, entry.username, password, has_totp, uris, further)

    def __load_from_rbw(self, name: str, username: str, folder: Optional[str]) -> str:
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

    def sync(self):
        run(['rbw', 'sync'])

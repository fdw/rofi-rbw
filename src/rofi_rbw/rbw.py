import json
from subprocess import run
from typing import List, Optional

from .credentials import Credentials
from .entry import Entry


class Rbw:
    def list_entries(self) -> List[Entry]:
        rbw = run(["rbw", "ls", "--fields", "folder,name,user"], encoding="utf-8", capture_output=True)

        if rbw.returncode != 0:
            print("There was a problem calling rbw. Is it correctly configured?")
            print(rbw.stderr)
            exit(2)

        return sorted(
            [self.__parse_rbw_output(it) for it in (rbw.stdout.strip().split("\n"))],
            key=lambda x: x.folder.lower() + x.name.lower(),
        )

    def __parse_rbw_output(self, rbw_string: str) -> "Entry":
        fields = rbw_string.split("\t")

        try:
            return Entry(fields[1], fields[0], fields[2] if len(fields) > 2 else "")
        except IndexError:
            raise Exception("Entry is incorrectly formatted and cannot be parsed")

    def fetch_credentials(self, entry: Entry) -> "Credentials":
        password = ""
        has_totp = False
        uris = []
        further = {}

        data = json.loads(self.__load_from_rbw(entry.name, entry.username, entry.folder).strip())

        if data['data']:
            if data['data']['password']:
                password = data['data']['password']

            for key in data['data']:
                value = data['data'][key]
                if value:
                    further[key] = value
                if key == 'totp':
                    has_totp = True
                if key == 'uris':
                    uris = list(map(lambda x: x['uri'], value))

        for record in data['fields']:
            try:
                key = record['name']
                value = record['value']
                if value:
                    further[key] = value
            except ValueError:
                pass
        return Credentials(entry.name, entry.folder, entry.username, password, has_totp, uris, further)

    def __load_from_rbw(self, name: str, username: str, folder: Optional[str]) -> str:
        command = ["rbw", "get", "--raw", name]
        if username:
            command.append(username)

        if folder:
            command.extend(["--folder", folder])

        return run(command, capture_output=True, encoding="utf-8").stdout

    def sync(self):
        run(["rbw", "sync"])

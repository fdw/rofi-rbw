import json
from json import JSONDecodeError
from subprocess import run
from typing import List, Optional

from .credentials import Credentials
from .entry import Entry


class Rbw:
    def list_entries(self) -> List[Entry]:
        rbw = run(["rbw", "list", "--fields", "folder,name,user"], encoding="utf-8", capture_output=True)

        if rbw.returncode != 0:
            print("There was a problem calling rbw. Is it correctly configured?")
            print(rbw.stderr)
            exit(2)

        return sorted(
            [self.__parse_rbw_output(it) for it in (rbw.stdout.strip("\n").split("\n"))],
            key=lambda x: x.folder.lower() + x.name.lower(),
        )

    def __parse_rbw_output(self, rbw_string: str) -> "Entry":
        fields = rbw_string.split("\t")

        try:
            return Entry(fields[1], fields[0], fields[2] if len(fields) > 2 else "")
        except IndexError:
            raise Exception("Entry is incorrectly formatted and cannot be parsed")

    def fetch_credentials(self, entry: Entry) -> "Credentials":
        try:
            data = json.loads(self.__load_from_rbw(entry.name, entry.username, entry.folder).strip())

            if data["data"] is None or "password" not in data["data"]:
                print("rofi-rbw only supports logins")
                return Credentials(
                    entry.name,
                    data["folder"],
                    entry.username,
                    notes=data["notes"],
                    further={item["name"]: item["value"] for item in data["fields"]},
                )

            return Credentials(
                entry.name,
                data["folder"],
                entry.username,
                data["data"]["password"] or "",
                data["data"]["totp"] is not None,
                data["notes"],
                [item["uri"] for item in data["data"]["uris"]],
                {item["name"]: item["value"] for item in data["fields"]},
            )

        except JSONDecodeError as exception:
            print(f"Could not parse the output: {exception.msg}")
            exit(12)

    def __load_from_rbw(self, name: str, username: str, folder: Optional[str]) -> str:
        command = ["rbw", "get", "--raw", name]
        if username:
            command.append(username)

        if folder:
            command.extend(["--folder", folder])

        return run(command, capture_output=True, encoding="utf-8").stdout

    def sync(self):
        run(["rbw", "sync"])

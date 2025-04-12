import json
from json import JSONDecodeError
from subprocess import run
from typing import List, Optional, Union

from .credentials import Card, Credentials, Field, FieldType
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

    def __parse_rbw_output(self, rbw_string: str) -> Entry:
        fields = rbw_string.split("\t")

        try:
            return Entry(fields[1], fields[0], fields[2] if len(fields) > 2 else "")
        except IndexError:
            raise Exception(f"Entry '{rbw_string}' cannot be parsed")

    def fetch_credentials(self, entry: Entry) -> Union[Credentials, Card]:
        try:
            data = json.loads(self.__load_from_rbw(entry.name, entry.username, entry.folder).strip())

            if data["data"] is not None and "password" in data["data"]:
                return Credentials(
                    entry.name,
                    data["folder"],
                    entry.username,
                    data["data"]["password"] or "",
                    data["data"]["totp"] is not None,
                    data["notes"],
                    [item["uri"] for item in data["data"]["uris"]],
                    fields=[Field(item["name"], item["value"], FieldType(item["type"])) for item in data["fields"]],
                )

            if data["data"] is not None and "number" in data["data"]:
                return Card(
                    entry.name,
                    entry.folder,
                    entry.username,
                    data["data"]["cardholder_name"],
                    data["data"]["number"],
                    data["data"]["brand"],
                    data["data"]["exp_month"],
                    data["data"]["exp_year"],
                    data["data"]["code"],
                    data["notes"],
                    fields=[Field(item["name"], item["value"], FieldType(item["type"])) for item in data["fields"]],
                )

            print("rofi-rbw only supports logins")
            exit(7)

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

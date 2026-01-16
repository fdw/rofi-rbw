import json
from json import JSONDecodeError
from subprocess import run
from typing import Any

from .models.card import Card
from .models.credentials import Credentials
from .models.detailed_entry import DetailedEntry
from .models.entry import Entry
from .models.EntryType import EntryType
from .models.field import Field, FieldType
from .models.note import Note


class Rbw:
    def list_entries(self) -> list[Entry]:
        rbw = run(["rbw", "list", "--raw"], encoding="utf-8", capture_output=True)

        if rbw.returncode != 0:
            print("There was a problem calling rbw. Is it correctly configured?")
            print(rbw.stderr)
            exit(2)

        data = json.loads(rbw.stdout.strip())

        return sorted(
            [
                Entry(item["name"], item["folder"] or "", item["user"] or "", item["type"])
                for item in data
                if item["type"] in {EntryType.LOGIN.value, EntryType.CARD.value, EntryType.NOTE.value}
            ],
            key=lambda x: x.folder.lower() + x.name.lower(),
        )

    def fetch_credentials(self, entry: Entry) -> DetailedEntry:
        if entry.type == EntryType.LOGIN.value:
            return self.__fetch_login(entry)
        elif entry.type == EntryType.CARD.value:
            return self.__fetch_card(entry)
        elif entry.type == EntryType.NOTE.value:
            return self.__fetch_note(entry)
        else:
            print(f"Unsupported type: {entry.type}")
            exit(7)

    def __fetch_login(self, entry: Entry) -> Credentials:
        data = self.__load_from_rbw(entry.name, entry.username, entry.folder)

        return Credentials(
            entry.name,
            data["folder"],
            [Field(item["name"], item["value"], FieldType(item["type"])) for item in data["fields"]],
            entry.username,
            data["data"]["password"] or "",
            data["data"]["totp"] is not None,
            data["notes"],
            [item["uri"] for item in data["data"]["uris"]],
        )

    def __fetch_card(self, entry: Entry) -> Card:
        data = self.__load_from_rbw(entry.name, entry.username, entry.folder)

        return Card(
            entry.name,
            entry.folder,
            [Field(item["name"], item["value"], FieldType(item["type"])) for item in data["fields"]],
            data["data"]["cardholder_name"],
            data["data"]["number"],
            data["data"]["brand"],
            data["data"]["exp_month"],
            data["data"]["exp_year"],
            data["data"]["code"],
            data["notes"],
        )

    def __fetch_note(self, entry: Entry) -> Note:
        data = self.__load_from_rbw(entry.name, entry.username, entry.folder)

        return Note(
            entry.name,
            entry.folder,
            [Field(item["name"], item["value"], FieldType(item["type"])) for item in data["fields"]],
            data["notes"],
        )

    def __load_from_rbw(self, name: str, username: str, folder: str | None) -> dict[str, Any]:
        command = ["rbw", "get", "--raw", name]
        if username:
            command.append(username)

        if folder:
            command.extend(["--folder", folder])

        data = run(command, capture_output=True, encoding="utf-8").stdout

        try:
            return json.loads(data.strip())

        except JSONDecodeError as exception:
            print(f"Could not parse the output: {exception.msg}")
            exit(12)

    def sync(self):
        run(["rbw", "sync"])

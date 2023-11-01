from dataclasses import dataclass
from enum import Enum
from typing import List, Union


class Action(Enum):
    TYPE = "type"
    COPY = "copy"
    PRINT = "print"
    SYNC = "sync"
    CANCEL = "cancel"


class Target:
    __value: str

    def __init__(self, input: str):
        prepared_input = input.strip()
        if prepared_input.lower() in (
            "username",
            "password",
            "menu",
            "totp",
            "notes",
        ) or prepared_input.lower().startswith("uri"):
            self.__value = prepared_input.lower()
        else:
            self.__value = prepared_input

    def is_uri(self) -> bool:
        return self.__value.startswith("uri")

    def uri_index(self) -> int:
        if not self.is_uri():
            raise IndexError()

        if len(self.__value) == 3:
            return 0
        else:
            return int(self.__value[4:]) - 1

    @property
    def raw(self):
        return self.__value

    def __eq__(self, other):
        return self.__value == other.__value


class Targets:
    USERNAME = Target("username")
    PASSWORD = Target("password")
    TOTP = Target("totp")
    NOTES = Target("notes")
    MENU = Target("menu")


@dataclass
class Keybinding:
    shortcut: str
    action: Action
    targets: Union[List[Target], None]

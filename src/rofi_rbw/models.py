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
            "brand",
            "cardholder",
            "code",
            "expiry",
            "menu",
            "notes",
            "number",
            "password",
            "totp",
            "username",
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


class TypeTarget(Target):
    pass


class Targets:
    USERNAME = Target("username")
    PASSWORD = Target("password")
    TOTP = Target("totp")
    NUMBER = Target("number")
    CARDHOLDER = Target("cardholder")
    BRAND = Target("brand")
    EXPIRY = Target("expiry")
    CODE = Target("code")
    NOTES = Target("notes")
    MENU = Target("menu")


class TypeTargets:
    DELAY = TypeTarget("delay")
    ENTER = TypeTarget("enter")
    TAB = TypeTarget("tab")


@dataclass
class Keybinding:
    shortcut: str
    action: Action
    targets: Union[List[TypeTarget], None]

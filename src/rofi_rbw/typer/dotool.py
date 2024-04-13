from subprocess import run

from ..abstractionhelper import is_installed
from .typer import Key, Typer


class DotoolTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return is_installed("dotool")

    @staticmethod
    def name() -> str:
        return "dotool"

    def get_active_window(self) -> str:
        return "not possible with dotool"

    def type_characters(self, characters: str, key_delay: int, active_window: str) -> None:
        run(["dotool"], input=f"typedelay {key_delay}\ntype {characters}", encoding="utf-8")

    def press_key(self, key: Key) -> None:
        if key == Key.ENTER:
            key_name = "enter"
        elif key == Key.TAB:
            key_name = "tab"
        else:
            raise Exception("Unknown key")

        run(["dotool"], input=f"key {key_name}", encoding="utf-8")

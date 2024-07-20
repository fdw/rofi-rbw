from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from .typer import Key, Typer


class WTypeTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("wtype")

    @staticmethod
    def name() -> str:
        return "wtype"

    def get_active_window(self) -> str:
        return "not possible with wtype"

    def type_characters(self, characters: str, key_delay: int, active_window: str) -> None:
        args = ["wtype"]

        if key_delay > 0:
            args = args + ["-d", str(key_delay)]

        args.append(characters)
        run(args)

    def press_key(self, key: Key) -> None:
        if key == Key.ENTER:
            key_name = "return"
        elif key == Key.TAB:
            key_name = "tab"
        else:
            raise Exception("Unknown key")

        run(["wtype", "-k", key_name])

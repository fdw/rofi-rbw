from subprocess import run
from time import sleep

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

    def type_characters(self, characters: str, start_delay: float, key_delay: int, active_window: str) -> None:
        sleep(start_delay)
        args = ["wtype"]

        if key_delay > 0:
            args = args + ["-d", str(key_delay)]

        args.append("--")
        args.append(characters)
        run(args)

    def press_key(self, key: Key) -> None:
        match key:
            case Key.ENTER:
                key_name = "return"
            case Key.TAB:
                key_name = "tab"
            case _:
                raise Exception("Unknown key")

        run(["wtype", "-k", key_name])

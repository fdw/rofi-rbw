from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from .typer import Key, Typer


class YDotoolTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("ydotool")

    @staticmethod
    def name() -> str:
        return "ydotool"

    def get_active_window(self) -> str:
        return "not possible with ydotool"

    def type_characters(self, characters: str, key_delay: int, active_window: str) -> None:
        run(["ydotool", "type", "--key-delay", str(key_delay), characters])

    def press_key(self, key: Key) -> None:
        if key == Key.ENTER:
            key_name = "28"
        elif key == Key.TAB:
            key_name = "15"
        else:
            raise Exception("Unknown key")

        run(["ydotool", "key", f"{key_name}:1", f"{key_name}:0"])

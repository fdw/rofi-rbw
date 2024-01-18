from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from .typer import Typer


class YDotoolTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("ydotool")

    @staticmethod
    def name() -> str:
        return "ydotool"

    def get_active_window(self) -> str:
        return "not possible with ydotool"

    def type_characters(self, characters: str, active_window: str) -> None:
        time.sleep(0.05)
        run(["ydotool", "type", "--key-delay", "0", characters])

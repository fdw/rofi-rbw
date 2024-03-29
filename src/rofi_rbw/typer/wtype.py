from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from .typer import Typer


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
        run(["wtype", "-d", str(key_delay), characters])

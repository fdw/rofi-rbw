from subprocess import run

from ..abstractionhelper import is_installed
from .typer import Typer


class DotoolTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return is_installed("dotool")

    @staticmethod
    def name() -> str:
        return "dotool"

    def get_active_window(self) -> str:
        return "not possible with dotool"

    def type_characters(self, characters: str, active_window: str) -> None:
        run(["dotool"], text=True, input=f"type {characters}")

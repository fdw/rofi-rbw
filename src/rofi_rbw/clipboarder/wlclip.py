import time
from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from .clipboarder import Clipboarder


class WlClipboarder(Clipboarder):
    __last_copied_characters: str | None

    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("wl-copy")

    @staticmethod
    def name() -> str:
        return "wl-copy"

    def copy_to_clipboard(self, characters: str) -> None:
        run(["wl-copy"], input=characters, encoding="utf-8")

        self.__last_copied_characters = characters

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)

            if self.__fetch_clipboard_content() == self.__last_copied_characters:
                run(["wl-copy", "--clear"])
                self.__last_copied_characters = None

    def __fetch_clipboard_content(self) -> str:
        return run(["wl-paste"], capture_output=True, encoding="utf-8").stdout

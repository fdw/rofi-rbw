import time
from subprocess import PIPE, Popen, run

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
        process = Popen(["wl-copy", "--sensitive"], stdin=PIPE, encoding="utf-8")
        process.stdin.write(characters)
        process.stdin.close()
        self.__last_copied_characters = characters

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)

            if self.__fetch_clipboard_content() == self.__last_copied_characters:
                run(["wl-copy", "--clear"])
                self.__last_copied_characters = None

    def __fetch_clipboard_content(self) -> str:
        return run(["wl-paste"], capture_output=True, encoding="utf-8").stdout

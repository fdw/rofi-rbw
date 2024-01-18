import time
from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from .clipboarder import Clipboarder


class XSelClipboarder(Clipboarder):
    __last_copied_characters: str

    @staticmethod
    def supported() -> bool:
        return not is_wayland() and is_installed("xsel")

    @staticmethod
    def name() -> str:
        return "xsel"

    def copy_to_clipboard(self, characters: str) -> None:
        run(["xsel", "--input", "--clipboard"], input=characters, encoding="utf-8")

        self.__last_copied_characters = characters

    def fetch_clipboard_content(self) -> str:
        return run(
            [
                "xsel",
                "--output",
                "--clipboard",
            ],
            capture_output=True,
            encoding="utf-8",
        ).stdout

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)

            # Only clear clipboard if nothing has been copied since the password
            if self.fetch_clipboard_content() == self.__last_copied_characters:
                run(["xsel", "--clear", "--clipboard"])
                self.__last_copied_characters = None

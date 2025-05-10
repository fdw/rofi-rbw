import time
from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from .clipboarder import Clipboarder


class WlClipboarder(Clipboarder):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("wl-copy")

    @staticmethod
    def name() -> str:
        return "wl-copy"

    def copy_to_clipboard(self, characters: str) -> None:
        run(["wl-copy"], input=characters, encoding="utf-8")

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)
            run(["wl-copy", "--clear"])

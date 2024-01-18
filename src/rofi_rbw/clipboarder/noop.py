from .clipboarder import Clipboarder, NoClipboarderFoundException


class NoopClipboarder(Clipboarder):
    @staticmethod
    def supported() -> bool:
        return True

    @staticmethod
    def name() -> str:
        return "noop"

    def copy_to_clipboard(self, characters: str) -> None:
        raise NoClipboarderFoundException()

    def clear_clipboard_after(self, clear: int) -> None:
        raise NoClipboarderFoundException()

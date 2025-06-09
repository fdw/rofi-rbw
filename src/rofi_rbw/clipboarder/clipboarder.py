from abc import ABC, abstractmethod


class Clipboarder(ABC):
    @staticmethod
    def best_option(name: str | None = None) -> "Clipboarder":
        from .noop import NoopClipboarder
        from .wlclip import WlClipboarder
        from .xclip import XClipClipboarder
        from .xsel import XSelClipboarder

        available_clipboarders = [XSelClipboarder, XClipClipboarder, WlClipboarder, NoopClipboarder]

        if name is not None:
            return next(clipboarder for clipboarder in available_clipboarders if clipboarder.name() == name)()
        else:
            return next(clipboarder for clipboarder in available_clipboarders if clipboarder.supported())()

    @staticmethod
    @abstractmethod
    def supported() -> bool:
        pass

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @abstractmethod
    def copy_to_clipboard(self, characters: str) -> None:
        pass

    @abstractmethod
    def clear_clipboard_after(self, clear: int) -> None:
        pass


class NoClipboarderFoundException(Exception):
    def __str__(self) -> str:
        return "Could not find a valid way to copy to clipboard. Please check the required dependencies."

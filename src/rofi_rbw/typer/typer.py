import enum
from abc import ABC, abstractmethod


class Typer(ABC):
    @staticmethod
    def best_option(name: str = None) -> "Typer":
        from .dotool import DotoolTyper
        from .noop import NoopTyper
        from .wtype import WTypeTyper
        from .xdotool import XDoToolTyper
        from .ydotool import YDotoolTyper

        available_typers = [XDoToolTyper, WTypeTyper, YDotoolTyper, DotoolTyper, NoopTyper]

        if name is not None:
            return next(typer for typer in available_typers if typer.name() == name)()
        else:
            return next(typer for typer in available_typers if typer.supported())()

    @staticmethod
    @abstractmethod
    def supported() -> bool:
        pass

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @abstractmethod
    def get_active_window(self) -> str:
        pass

    @abstractmethod
    def type_characters(self, characters: str, key_delay: int, active_window: str) -> None:
        pass

    @abstractmethod
    def press_key(self, key: "Key") -> None:
        pass


class NoTyperFoundException(Exception):
    def __str__(self) -> str:
        return "Could not find a valid way to type characters. Please check the required dependencies."


class Key(enum.Enum):
    ENTER = "enter"
    TAB = "tab"

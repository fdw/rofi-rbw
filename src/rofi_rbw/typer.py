import time
from subprocess import run

from .abstractionhelper import is_installed, is_wayland


class Typer:
    @staticmethod
    def best_option(name: str = None) -> "Typer":
        try:
            return next(typer for typer in Typer.__subclasses__() if typer.name() == name)()
        except StopIteration:
            try:
                return next(typer for typer in Typer.__subclasses__() if typer.supported())()
            except StopIteration:
                return Typer()

    @staticmethod
    def supported() -> bool:
        pass

    @staticmethod
    def name() -> str:
        pass

    def get_active_window(self) -> str:
        raise NoTyperFoundException()

    def type_characters(self, characters: str, active_window: str) -> None:
        raise NoTyperFoundException()


class XDoToolTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return not is_wayland() and is_installed("xdotool")

    @staticmethod
    def name() -> str:
        return "xdotool"

    def get_active_window(self) -> str:
        return run(args=["xdotool", "getactivewindow"], capture_output=True, encoding="utf-8").stdout[:-1]

    def type_characters(self, characters: str, active_window: str) -> None:
        run(
            [
                "xdotool",
                "windowactivate",
                "--sync",
                active_window,
                "type",
                "--clearmodifiers",
                "--delay",
                "0",
                characters,
            ]
        )
        # workaround for https://github.com/jordansissel/xdotool/issues/43
        run(["xdotool", "keyup", "Shift_L", "Shift_R", "Alt_L", "Alt_R"])


class WTypeTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("wtype")

    @staticmethod
    def name() -> str:
        return "wtype"

    def get_active_window(self) -> str:
        return "not possible with wtype"

    def type_characters(self, characters: str, active_window: str) -> None:
        run(["wtype", characters])


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


class NoTyperFoundException(Exception):
    def __str__(self) -> str:
        return "Could not find a valid way to type characters. Please check the required dependencies."

from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from .typer import Key, Typer


class XDoToolTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return not is_wayland() and is_installed("xdotool")

    @staticmethod
    def name() -> str:
        return "xdotool"

    def get_active_window(self) -> str:
        return run(args=["xdotool", "getactivewindow"], capture_output=True, encoding="utf-8").stdout[:-1]

    def type_characters(self, characters: str, key_delay: int, active_window: str) -> None:
        run(
            [
                "xdotool",
                "windowactivate",
                "--sync",
                active_window,
                "type",
                "--clearmodifiers",
                "--delay",
                str(key_delay),
                characters,
            ]
        )
        # workaround for https://github.com/jordansissel/xdotool/issues/43
        run(["xdotool", "keyup", "Shift_L", "Shift_R", "Alt_L", "Alt_R"])

    def press_key(self, key: Key) -> None:
        if key == Key.ENTER:
            key_name = "Return"
        elif key == Key.TAB:
            key_name = "Tab"
        else:
            raise Exception("Unknown key")

        run(["xdotool", "key", key_name])

from .typer import Key, NoTyperFoundException, Typer


class NoopTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return True

    @staticmethod
    def name() -> str:
        return "noop"

    def get_active_window(self) -> str:
        raise NoTyperFoundException()

    def type_characters(self, characters: str, key_delay: int, active_window: str) -> None:
        raise NoTyperFoundException()

    def press_key(self, key: Key) -> None:
        raise NoTyperFoundException()

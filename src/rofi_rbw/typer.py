from subprocess import run

try:
    from rofi_rbw.abstractionhelper import is_wayland, is_installed
except ModuleNotFoundError:
    from abstractionhelper import is_wayland, is_installed


class Typer:
    @staticmethod
    def best_option(name: str = None) -> 'Typer':
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
        print('Could not find a valid way to type characters. Please check the required dependencies.')
        exit(5)

    def type_characters(self, characters: str, active_window: str) -> None:
        print('Could not find a valid way to type characters. Please check the required dependencies.')
        exit(5)


class XDoToolTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return not is_wayland() and is_installed('xdotool')

    @staticmethod
    def name() -> str:
        return 'xdotool'

    def get_active_window(self) -> str:
        return run(args=['xdotool', 'getactivewindow'], capture_output=True,
                   encoding='utf-8').stdout[:-1]

    def type_characters(self, characters: str, active_window: str) -> None:
        run([
            'xdotool',
            'type',
            '--clearmodifiers',
            '--window',
            active_window,
            characters
        ])


class WTypeTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed('wtype')

    @staticmethod
    def name() -> str:
        return 'wtype'

    def get_active_window(self) -> str:
        return "not possible with wtype"

    def type_characters(self, characters: str, active_window: str) -> None:
        run([
            'wtype',
            characters
        ])


class YDotoolTyper(Typer):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed('ydotool')

    @staticmethod
    def name() -> str:
        return 'ydotool'

    def get_active_window(self) -> str:
        return "not possible with ydotool"

    def type_characters(self, characters: str, active_window: str) -> None:
        run([
            'ydotool',
            'sleep',
            '50',
            ',',
            'type',
            characters
        ])

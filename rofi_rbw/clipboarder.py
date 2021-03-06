from subprocess import run

try:
    from rofi_rbw.abstractionhelper import is_wayland, is_installed
    from rofi_rbw.typer import Typer
except ModuleNotFoundError:
    from abstractionhelper import is_wayland, is_installed
    from typer import Typer


class Clipboarder:
    @staticmethod
    def best_option(name: str = None) -> 'Clipboarder':
        try:
            return next(clipboarder for clipboarder in Clipboarder.__subclasses__() if clipboarder.name() == name)()
        except StopIteration:
            try:
                return next(clipboarder for clipboarder in Clipboarder.__subclasses__() if clipboarder.supported())()
            except StopIteration:
                return Clipboarder()

    @staticmethod
    def supported() -> bool:
        pass

    @staticmethod
    def name() -> str:
        pass

    def copy_to_clipboard(self, characters: str) -> None:
        print('Could not find a valid way to copy to clipboard. Please check the required dependencies.')
        exit(6)


class XSelClipboarder(Clipboarder):
    @staticmethod
    def supported() -> bool:
        return not is_wayland() and is_installed('xsel')

    @staticmethod
    def name() -> str:
        return 'xsel'

    def copy_to_clipboard(self, characters: str) -> None:
        run([
            'xsel',
            '-i',
            '-b'
        ],
            input=characters,
            encoding='utf-8'
        )


class XClipClipboarder(Clipboarder):
    @staticmethod
    def supported() -> bool:
        return not is_wayland() and is_installed('xclip')

    @staticmethod
    def name() -> str:
        return 'xclip'

    def copy_to_clipboard(self, characters: str) -> None:
        run([
            'xclip',
            '-i',
            '-selection',
            'clipboard'
        ],
            input=characters,
            encoding='utf-8'
        )


class WlClipboarder(Clipboarder):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed('wl-copy')

    @staticmethod
    def name() -> str:
        return 'wl-copy'

    def copy_to_clipboard(self, characters: str) -> None:
        run(
            ['wl-copy'],
            input=characters,
            encoding='utf-8'
        )

import time
from subprocess import run

from .abstractionhelper import is_wayland, is_installed


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

    def clear_clipboard_after(self, clear: int) -> None:
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

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)
            run(['xsel', '-delete'])


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

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)
            self.copy_to_clipboard("")


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

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)
            run(['wl-copy', '--clear'])

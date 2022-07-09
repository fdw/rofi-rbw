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
        raise NoClipboarderFoundException()

    def clear_clipboard_after(self, clear: int) -> None:
        raise NoClipboarderFoundException()


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
            '--input',
            '--clipboard'
        ],
            input=characters,
            encoding='utf-8'
        )

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)
            run([
                'xsel',
                '--clear',
                '--clipboard'
            ])


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
            '-in',
            '-selection',
            'clipboard'
        ],
            input=characters,
            encoding='utf-8'
        )

        self.previously_copied = characters

    def get_clipboard(self) -> str:
        return run([
            'xclip',
            '-o',
            '-selection',
            'clipboard'
        ],
            capture_output=True,
            text=True
        ).stdout

    def clear_clipboard_after(self, clear: int) -> None:
        if clear > 0:
            time.sleep(clear)

            # Only clear clipboard if nothing has been copied since the password
            if self.get_clipboard() == self.previously_copied:
                self.copy_to_clipboard("")
                self.previously_copied = None


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


class NoClipboarderFoundException(Exception):
    def __str__(self) -> str:
        return 'Could not find a valid way to copy to clipboard. Please check the required dependencies.'

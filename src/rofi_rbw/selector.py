from rofi_rbw.abstractionhelper import is_wayland, is_installed

from typing import List, Tuple
from subprocess import run


class Selector:
    @staticmethod
    def best_option(name: str = None) -> 'Selector':
        try:
            return next(selector for selector in Selector.__subclasses__() if selector.name() == name)()
        except StopIteration:
            try:
                return next(selector for selector in Selector.__subclasses__() if selector.supported())()
            except StopIteration:
                return Selector()

    @staticmethod
    def supported() -> bool:
        pass

    @staticmethod
    def name() -> str:
        pass

    def show_selection(self, entries: str, prompt: str, show_help_message: bool, additional_args: List[str]) -> Tuple[int, str]:
        print('Could not find a valid way to show the selection. Please check the required dependencies.')
        exit(4)


class Rofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_installed('rofi')

    @staticmethod
    def name() -> str:
        return 'rofi'

    def show_selection(self, entries: str, prompt: str, show_help_message: bool, additional_args: List[str]) -> Tuple[int, str]:
        parameters = [
            'rofi',
            '-dmenu',
            '-i',
            '-sort',
            '-p',
            prompt,
            '-kb-custom-11',
            'Alt+p',
            '-kb-custom-12',
            'Alt+u',
            '-kb-custom-13',
            'Alt+t',
            *additional_args
        ]

        if show_help_message:
            parameters.extend([
                '-mesg',
                '<b>Alt+1</b>: Autotype username and password | <b>Alt+2</b> Type username | <b>Alt+u</b> Copy username | <b>Alt+p</b> Copy password | <b>Alt+t</b> Copy totp'
            ])

        rofi = run(
            parameters,
            input=entries,
            capture_output=True,
            encoding='utf-8'
        )
        return rofi.returncode, rofi.stdout


class Wofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed('wofi')

    @staticmethod
    def name() -> str:
        return 'wofi'

    def show_selection(self, entries: str, prompt: str, show_help_message: bool, additional_args: List[str]) -> Tuple[int, str]:
        parameters = [
            'wofi',
            '--dmenu',
            '-p',
            prompt,
            *additional_args
        ]

        wofi = run(
            parameters,
            input=entries,
            capture_output=True,
            encoding='utf-8'
        )
        return wofi.returncode, wofi.stdout


from typing import List, Tuple
from subprocess import run

try:
    from rofi_rbw.abstractionhelper import is_wayland, is_installed
    from rofi_rbw.action import Action
except:
    from abstractionhelper import is_wayland, is_installed
    from action import Action


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

    def show_selection(
        self,
        entries: List[str],
        default_action: Action,
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Action, str]:
        print('Could not find a valid way to show the selection. Please check the required dependencies.')
        exit(4)


class Rofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_installed('rofi')

    @staticmethod
    def name() -> str:
        return 'rofi'

    def show_selection(
        self,
        entries: List[str],
        default_action: Action,
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Action, str]:
        parameters = [
            'rofi',
            '-markup-rows',
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
            '-kb-custom-15',
            'Alt+m',
            *additional_args
        ]

        if show_help_message:
            parameters.extend([
                '-mesg',
                '<b>Alt+1</b>: Autotype username and password | <b>Alt+2</b> Type username | <b>Alt+u</b> Copy username | <b>Alt+p</b> Copy password | <b>Alt+t</b> Copy totp'
            ])

        rofi = run(
            parameters,
            input='\n'.join(entries),
            capture_output=True,
            encoding='utf-8'
        )
        returnaction = None
        if rofi.returncode == 0:
            returnaction = default_action
        elif rofi.returncode == 12:
            returnaction = Action.TYPE_PASSWORD
        elif rofi.returncode == 11:
            returnaction = Action.TYPE_USERNAME
        elif rofi.returncode == 10:
            returnaction = Action.TYPE_BOTH
        elif rofi.returncode == 13:
            returnaction = Action.AUTOTYPE_MENU
        elif rofi.returncode == 20:
            returnaction = Action.COPY_PASSWORD
        elif rofi.returncode == 21:
            returnaction = Action.COPY_USERNAME
        elif rofi.returncode == 22:
            returnaction = Action.COPY_TOTP

        return returnaction, rofi.stdout


class Wofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed('wofi')

    @staticmethod
    def name() -> str:
        return 'wofi'

    def show_selection(
        self,
        entries: List[str],
        default_action: Action,
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Action, str]:
        parameters = [
            'wofi',
            '--dmenu',
            '-p',
            prompt,
            *additional_args
        ]

        wofi = run(
            parameters,
            input='\n'.join(entries),
            capture_output=True,
            encoding='utf-8'
        )
        returnaction = None
        if wofi.returncode == 0:
            returnaction = default_action
        return returnaction, wofi.stdout


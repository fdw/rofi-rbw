from subprocess import run
from typing import List, Tuple, Union

from .abstractionhelper import is_wayland, is_installed
from .models import Action, Target, Targets, CANCEL, DEFAULT


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
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], DEFAULT, CANCEL], Union[Action, DEFAULT, CANCEL], str]:
        print('Could not find a valid way to show the selection. Please check the required dependencies.')
        exit(4)

    def select_target(
        self,
        targets: List[str],
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], CANCEL], Union[Action, DEFAULT, CANCEL]]:
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
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], DEFAULT, CANCEL], Union[Action, DEFAULT, CANCEL], str]:
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
            'Alt+o',
            '-kb-custom-14',
            'Alt+m',
            *additional_args
        ]

        if show_help_message:
            parameters.extend([
                '-mesg',
                '<b>Alt+1</b>: Autotype username and password | <b>Alt+2</b> Type username | <b>Alt+3</b> Type password | <b>Alt+u</b> Copy username | <b>Alt+p</b> Copy password | <b>Alt+t</b> Copy totp'
            ])

        rofi = run(
            parameters,
            input='\n'.join(entries),
            capture_output=True,
            encoding='utf-8'
        )

        if rofi.returncode == 1:
            return_action = CANCEL()
            return_targets = CANCEL()
        elif rofi.returncode == 10:
            return_action = Action.TYPE
            return_targets = [Targets.USERNAME, Targets.PASSWORD]
        elif rofi.returncode == 11:
            return_action = Action.TYPE
            return_targets = [Targets.USERNAME]
        elif rofi.returncode == 12:
            return_action = Action.TYPE
            return_targets = [Targets.PASSWORD]
        elif rofi.returncode == 20:
            return_action = Action.COPY
            return_targets = [Targets.PASSWORD]
        elif rofi.returncode == 21:
            return_action = Action.COPY
            return_targets = [Targets.USERNAME]
        elif rofi.returncode == 22:
            return_action = Action.COPY
            return_targets = [Targets.TOTP]
        elif rofi.returncode == 23:
            return_action = DEFAULT
            return_targets = [Targets.MENU]
        else:
            return_action = DEFAULT()
            return_targets = DEFAULT()

        return return_targets, return_action, rofi.stdout

    def select_target(
        self,
        targets: List[str],
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], CANCEL], Union[Action, DEFAULT, CANCEL]]:
        parameters = [
            'rofi',
            '-markup-rows',
            '-dmenu',
            '-i',
            '-kb-custom-11',
            'Alt+t',
            '-kb-custom-12',
            'Alt+c',
            *additional_args
        ]

        if show_help_message:
            parameters.extend([
                '-mesg',
                '<b>Alt+t</b>: Type | <b>Alt+c</b> Copy'
            ])

        rofi = run(
            parameters,
            input='\n'.join(targets),
            capture_output=True,
            encoding='utf-8'
        )

        if rofi.returncode == 1:
            return CANCEL(), CANCEL()
        elif rofi.returncode == 20:
            action = Action.TYPE
        elif rofi.returncode == 21:
            action = Action.COPY
        else:
            action = DEFAULT()

        targets = [Target(entry.split(':')[0]) for entry in rofi.stdout.strip().split('\n')]

        return targets, action


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
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], DEFAULT, CANCEL], Union[Action, DEFAULT, CANCEL],  str]:
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
        if wofi.returncode == 0:
            return DEFAULT(), DEFAULT(), wofi.stdout
        else:
            return CANCEL(), CANCEL(), wofi.stdout

    def select_target(
        self,
        targets: List[str],
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], CANCEL], Union[Action, DEFAULT, CANCEL]]:
        parameters = [
            'wofi',
            '--dmenu',
            *additional_args
        ]

        wofi = run(
            parameters,
            input='\n'.join(targets),
            capture_output=True,
            encoding='utf-8'
        )

        if wofi.returncode == 1:
            return CANCEL(), CANCEL()

        return [Target(entry.split(':')[0]) for entry in wofi.stdout.strip().split('\n')], DEFAULT()


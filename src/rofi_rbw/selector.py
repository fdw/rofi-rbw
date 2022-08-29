from subprocess import run
from typing import List, Tuple, Union

from .abstractionhelper import is_wayland, is_installed
from .models import Action, Target, Targets, CANCEL


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
        default_targets: List[Target],
        default_action: Action,
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[List[Target], Union[Action, CANCEL], str]:
        print('Could not find a valid way to show the selection. Please check the required dependencies.')
        exit(4)

    def select_target(
        self,
        targets: List[str],
        default_action: Action,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[List[Target], Union[Action, CANCEL]]:
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
        default_targets: List[Target],
        default_action: Action,
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[List[Target], Union[Action, CANCEL], str]:
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
            '-kb-custom-14',
            'Alt+m',
            *additional_args
        ]
        keys = {
            10: ('<b>Alt+1</b> Type username and password', [Targets.USERNAME, Targets.PASSWORD], Action.TYPE),
            11: ('<b>Alt+2</b> Type username', [Targets.USERNAME], Action.TYPE),
            12: ('<b>Alt+3</b> Type password', [Targets.PASSWORD], Action.TYPE),
            21: ('<b>Alt+u</b> Copy username', [Targets.USERNAME], Action.COPY),
            20: ('<b>Alt+p</b> Copy password', [Targets.PASSWORD], Action.COPY),
            22: ('<b>Alt+t</b> Copy totp', [Targets.TOTP], Action.COPY),
            23: ('<b>Alt+m</b> Show menu', [Targets.MENU], default_action)
        }

        if show_help_message:
            parameters.extend([
                '-mesg',
                ' | '.join(keys[k][0] for k in keys if not (keys[k][1] == default_targets and keys[k][2] == default_action))
            ])

        rofi = run(
            parameters,
            input='\n'.join(entries),
            capture_output=True,
            encoding='utf-8'
        )

        if rofi.returncode == 1:
            return_action = CANCEL()
            return_targets = []
        elif rofi.returncode in keys:
            return_action = keys[rofi.returncode][2]
            return_targets = keys[rofi.returncode][1]
        else:
            return_action = default_action
            return_targets = default_targets

        return return_targets, return_action, rofi.stdout

    def select_target(
        self,
        targets: List[str],
        default_action: Action,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[List[Target], Union[Action, CANCEL]]:
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
            return [], CANCEL()
        elif rofi.returncode == 20:
            action = Action.TYPE
        elif rofi.returncode == 21:
            action = Action.COPY
        else:
            action = default_action

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
        default_targets: List[Target],
        default_action: Action,
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[List[Target], Union[Action, CANCEL], str]:
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
            return default_targets, default_action, wofi.stdout
        else:
            return [], CANCEL(), wofi.stdout

    def select_target(
        self,
        targets: List[str],
        default_action: Action,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[List[Target], Union[Action, CANCEL]]:
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
            return [], CANCEL()

        return [Target(entry.split(':')[0]) for entry in wofi.stdout.strip().split('\n')], default_action


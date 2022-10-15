from subprocess import run
from typing import List, Tuple, Union

from .abstractionhelper import is_wayland, is_installed
from .credentials import Credentials
from .entry import Entry
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
        entries: List[Entry],
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], DEFAULT, CANCEL], Union[Action, DEFAULT, CANCEL], Union[Entry, None]]:
        raise NoSelectorFoundException()

    def select_target(
        self,
        credentials: Credentials,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], CANCEL], Union[Action, DEFAULT, CANCEL]]:
        raise NoSelectorFoundException()

    def _format_entries(self, entries: List[Entry]) -> List[str]:
        max_length = max(len(it) for it in entries)
        return sorted(it.formatted_string(max_length) for it in entries)

    def _format_targets_from_credential(self, credentials: Credentials) -> List[str]:
        targets = []
        if credentials.username:
            targets.append(f'Username: {credentials.username}')
        if credentials.password:
            targets.append(f'Password: {credentials.password[0]}{"*" * (len(credentials.password) - 1)}')
        if credentials.has_totp:
            targets.append(f'TOTP: {credentials.totp}')
        if len(credentials.uris) == 1:
            targets.append(f'URI: {credentials.uris[0]}')
        else:
            for (key, value) in enumerate(credentials.uris):
                targets.append(f'URI {key + 1}: {value}')
        for (key, value) in credentials.further.items():
            targets.append(f'{key}: {value[0]}{"*" * (len(value) - 1)}')

        return targets

    def _extract_targets(self, output: str) -> List[Target]:
        return [Target(line.split(':')[0]) for line in output.strip().split('\n')]


class Rofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_installed('rofi')

    @staticmethod
    def name() -> str:
        return 'rofi'

    def show_selection(
        self,
        entries: List[Entry],
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], DEFAULT, CANCEL], Union[Action, DEFAULT, CANCEL], Union[Entry, None]]:
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

        if show_help_message:
            parameters.extend([
                '-mesg',
                '<b>Alt+1</b>: Autotype username and password | <b>Alt+2</b> Type username | <b>Alt+3</b> Type password | <b>Alt+u</b> Copy username | <b>Alt+p</b> Copy password | <b>Alt+t</b> Copy totp'
            ])

        rofi = run(
            parameters,
            input='\n'.join(self._format_entries(entries)),
            capture_output=True,
            encoding='utf-8'
        )

        if rofi.returncode == 1:
            return CANCEL(), CANCEL(), None
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

        return return_targets, return_action, Entry.parse_formatted_string(rofi.stdout)

    def select_target(
        self,
        credentials: Credentials,
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
            input='\n'.join(self._format_targets_from_credential(credentials)),
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

        return (self._extract_targets(rofi.stdout)), action


class Wofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed('wofi')

    @staticmethod
    def name() -> str:
        return 'wofi'

    def show_selection(
        self,
        entries: List[Entry],
        prompt: str,
        show_help_message: bool,
        additional_args: List[str]
    ) -> Tuple[Union[List[Target], DEFAULT, CANCEL], Union[Action, DEFAULT, CANCEL], Union[Entry, None]]:
        parameters = [
            'wofi',
            '--dmenu',
            '-p',
            prompt,
            *additional_args
        ]

        wofi = run(
            parameters,
            input='\n'.join(self._format_entries(entries)),
            capture_output=True,
            encoding='utf-8'
        )
        if wofi.returncode == 0:
            return DEFAULT(), DEFAULT(), Entry.parse_formatted_string(wofi.stdout)
        else:
            return CANCEL(), CANCEL(), None

    def select_target(
        self,
        credentials: Credentials,
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
            input='\n'.join(self._format_targets_from_credential(credentials)),
            capture_output=True,
            encoding='utf-8'
        )

        if wofi.returncode == 1:
            return CANCEL(), CANCEL()

        return self._extract_targets(wofi.stdout), DEFAULT()


class NoSelectorFoundException(Exception):
    def __str__(self) -> str:
        return 'Could not find a valid way to show the selection. Please check the required dependencies.'

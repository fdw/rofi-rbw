import re
from subprocess import run
from typing import Dict, List, Tuple, Union

from .abstractionhelper import is_installed, is_wayland
from .credentials import Credentials
from .entry import Entry
from .models import Action, Keybinding, Target, Targets


class Selector:
    @staticmethod
    def best_option(name: str = None) -> "Selector":
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
        show_folders: bool,
        keybindings: Dict[str, Tuple[Action, List[Target]]],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None], Union[Entry, None]]:
        raise NoSelectorFoundException()

    def select_target(
        self,
        credentials: Credentials,
        show_help_message: bool,
        keybindings: Dict[str, Action],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None]]:
        raise NoSelectorFoundException()

    def _format_targets_from_credential(self, credentials: Credentials) -> List[str]:
        targets = []
        if credentials.username:
            targets.append(f"Username: {credentials.username}")
        if credentials.password:
            targets.append(f'Password: {credentials.password[0]}{"*" * (len(credentials.password) - 1)}')
        if credentials.has_totp:
            targets.append(f"TOTP: {credentials.totp}")
        if credentials.notes:
            targets.append(f"Notes: {credentials.notes}")
        if len(credentials.uris) == 1:
            targets.append(f"URI: {credentials.uris[0]}")
        else:
            for key, value in enumerate(credentials.uris):
                targets.append(f"URI {key + 1}: {value}")
        for (key, value) in credentials.further.items():
            targets.append(f'{self._format_further_item_name(key)}: {value[0]}{"*" * (len(value) - 1)}')

        return targets

    def _format_further_item_name(self, key: str) -> str:
        if key.lower() in ["username", "password", "totp"] or re.match(r"^URI \d+$", key):
            return f"{key} (field)"
        return key

    @staticmethod
    def _extract_targets(output: str) -> List[Target]:
        return [Target(line.split(":")[0]) for line in output.strip().split("\n")]

    @staticmethod
    def _calculate_max_width(entries: List[Entry], show_folders: bool) -> int:
        if show_folders:
            return max(len(it.name) + len(it.folder) + 1 for it in entries)
        else:
            return max(len(it.name) for it in entries)

    @staticmethod
    def _format_folder(entry: Entry, show_folders: bool) -> str:
        if not show_folders or not entry.folder:
            return ""
        return f"{entry.folder}/"

    @staticmethod
    def justify(entry: Entry, max_width: int, show_folders: bool) -> str:
        whitespace_length = max_width - len(entry.name)
        if show_folders:
            whitespace_length -= len(entry.folder)
            if entry.folder:
                whitespace_length -= 1
        return " " * whitespace_length


class Rofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_installed("rofi")

    @staticmethod
    def name() -> str:
        return "rofi"

    def show_selection(
        self,
        entries: List[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: List[Keybinding],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None], Union[Entry, None]]:
        parameters = [
            "rofi",
            "-markup-rows",
            "-dmenu",
            "-i",
            "-sort",
            "-p",
            prompt,
            *self.__build_parameters_for_keybindings(keybindings),
            *additional_args,
        ]

        if show_help_message and keybindings:
            parameters.extend(self.__format_keybindings_message(keybindings))

        rofi = run(
            parameters,
            input="\n".join(self.__format_entries(entries, show_folders)),
            capture_output=True,
            encoding="utf-8",
        )

        if rofi.returncode == 1:
            return None, Action.CANCEL, None
        elif rofi.returncode >= 10:
            keybinding = keybindings[(rofi.returncode - 10)]
            return_action = keybinding.action
            return_targets = keybinding.targets
        else:
            return_action = None
            return_targets = None

        return return_targets, return_action, self.__parse_formatted_string(rofi.stdout)

    def __format_entries(self, entries: List[Entry], show_folders: bool) -> List[str]:
        max_width = self._calculate_max_width(entries, show_folders)
        return [
            f"{self._format_folder(it, show_folders)}<b>{it.name}</b>{self.justify(it, max_width, show_folders)}  {it.username}"
            for it in entries
        ]

    def __parse_formatted_string(self, formatted_string: str) -> Entry:
        match = re.compile("(?:(?P<folder>.+)/)?<b>(?P<name>.*?) *</b>(?P<username>.*)").search(formatted_string)

        return Entry(match.group("name"), match.group("folder"), match.group("username").strip())

    def select_target(
        self,
        credentials: Credentials,
        show_help_message: bool,
        keybindings: List[Keybinding],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None]]:
        parameters = [
            "rofi",
            "-markup-rows",
            "-dmenu",
            "-p",
            "Choose target",
            "-i",
            *self.__build_parameters_for_keybindings(keybindings),
            *additional_args,
        ]

        if show_help_message and keybindings:
            parameters.extend(self.__format_keybindings_message(keybindings))

        rofi = run(
            parameters,
            input="\n".join(self._format_targets_from_credential(credentials)),
            capture_output=True,
            encoding="utf-8",
        )

        if rofi.returncode == 1:
            return None, Action.CANCEL
        elif rofi.returncode >= 10:
            action = keybindings[(rofi.returncode - 10)].action
        else:
            action = None

        return (self._extract_targets(rofi.stdout)), action

    def __build_parameters_for_keybindings(self, keybindings: List[Keybinding]) -> List[str]:
        params = []
        for index, keybinding in enumerate(keybindings):
            params.extend([f"-kb-custom-{1 + index}", keybinding.shortcut])

        return params

    def __format_keybindings_message(self, keybindings: List[Keybinding]):
        return [
            "-mesg",
            " | ".join(
                [
                    f"<b>{keybinding.shortcut}</b>: {self.__format_action_and_targets(keybinding)}"
                    for keybinding in keybindings
                ]
            ),
        ]

    def __format_action_and_targets(self, keybinding: Keybinding) -> str:
        if keybinding.targets and Targets.MENU in keybinding.targets:
            return "Menu"
        elif keybinding.action == Action.SYNC:
            return "Sync logins"
        elif keybinding.targets:
            return f"{keybinding.action.value.title()} {', '.join([target.raw for target in keybinding.targets])}"
        else:
            return keybinding.action.value.title()


class Wofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("wofi")

    @staticmethod
    def name() -> str:
        return "wofi"

    def show_selection(
        self,
        entries: List[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: Dict[str, Tuple[Action, List[Target]]],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None], Union[Entry, None]]:
        parameters = ["wofi", "--dmenu", "-p", prompt, *additional_args]

        wofi = run(
            parameters,
            input="\n".join(self.__format_entries(entries, show_folders)),
            capture_output=True,
            encoding="utf-8",
        )
        if wofi.returncode == 0:
            return None, None, self.__parse_formatted_string(wofi.stdout)
        else:
            return None, Action.CANCEL, None

    def __format_entries(self, entries: List[Entry], show_folders: bool) -> List[str]:
        max_width = self._calculate_max_width(entries, show_folders)
        return [
            f"{self._format_folder(it, show_folders)}{it.name}{self.justify(it, max_width, show_folders)}  {it.username}"
            for it in entries
        ]

    def __parse_formatted_string(self, formatted_string: str) -> Entry:
        match = re.compile("(?:(?P<folder>.+)/)?(?P<name>.*?) *  (?P<username>.*)").search(formatted_string)

        return Entry(match.group("name").strip(), match.group("folder"), match.group("username").strip())

    def select_target(
        self,
        credentials: Credentials,
        show_help_message: bool,
        keybindings: Dict[str, Action],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None]]:
        parameters = ["wofi", "--dmenu", "-p", "Choose target", *additional_args]

        wofi = run(
            parameters,
            input="\n".join(self._format_targets_from_credential(credentials)),
            capture_output=True,
            encoding="utf-8",
        )

        if wofi.returncode == 1:
            return None, Action.CANCEL

        return self._extract_targets(wofi.stdout), None


class NoSelectorFoundException(Exception):
    def __str__(self) -> str:
        return "Could not find a valid way to show the selection. Please check the required dependencies."

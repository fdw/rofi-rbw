import re
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Union

from rofi_rbw.credentials import Credentials
from rofi_rbw.entry import Entry
from rofi_rbw.models import Action, Target


class Selector(ABC):
    @staticmethod
    def best_option(name: str = None) -> "Selector":
        from .bemenu import Bemenu
        from .rofi import Rofi
        from .wofi import Wofi

        available_selectors = [Rofi, Wofi, Bemenu]

        if name is not None:
            try:
                return next(selector for selector in available_selectors if selector.name() == name)()
            except StopIteration:
                raise NoSelectorFoundException()
        else:
            try:
                return next(selector for selector in available_selectors if selector.supported())()
            except StopIteration:
                raise NoSelectorFoundException()

    @staticmethod
    @abstractmethod
    def supported() -> bool:
        pass

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @abstractmethod
    def show_selection(
        self,
        entries: List[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: Dict[str, Tuple[Action, List[Target]]],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None], Union[Entry, None]]:
        pass

    @abstractmethod
    def select_target(
        self,
        credentials: Credentials,
        show_help_message: bool,
        keybindings: Dict[str, Action],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None]]:
        pass

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
        for key, value in credentials.further.items():
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


class NoSelectorFoundException(Exception):
    def __str__(self) -> str:
        return "Could not find a valid way to show the selection. Please check the required dependencies."

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Union

from rofi_rbw.credentials import Card, Credentials
from rofi_rbw.entry import Entry
from rofi_rbw.models import Action, Target


class Selector(ABC):
    @staticmethod
    def best_option(name: str = None) -> "Selector":
        from .bemenu import Bemenu
        from .fuzzel import Fuzzel
        from .rofi import Rofi
        from .wofi import Wofi

        available_selectors = [Rofi, Wofi, Bemenu, Fuzzel]

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
        credentials: Union[Credentials, Card],
        show_help_message: bool,
        keybindings: Dict[str, Action],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None]]:
        pass

    def _format_targets_from_entry(self, entry: Union[Credentials, Card]) -> List[str]:
        if isinstance(entry, Credentials):
            return self._format_targets_from_credential(entry)
        elif isinstance(entry, Card):
            return self._format_targets_from_card(entry)

    def _format_targets_from_credential(self, credentials: Credentials) -> List[str]:
        targets = []
        if credentials.username:
            targets.append(f"Username: {credentials.username}")
        if credentials.password:
            targets.append(f"Password: {credentials.password[0]}{'*' * (len(credentials.password) - 1)}")
        if credentials.has_totp:
            targets.append(f"TOTP: {credentials.totp}")
        if credentials.notes:
            targets.append(f"Notes: {credentials.notes}")
        if len(credentials.uris) == 1:
            targets.append(f"URI: {credentials.uris[0]}")
        else:
            for key, value in enumerate(credentials.uris):
                targets.append(f"URI {key + 1}: {value}")
        for field in credentials.fields:
            targets.append(f"{self._format_further_item_name(field.key)}: {field.masked_string()}")

        return targets

    def _format_targets_from_card(self, card: Card) -> List[str]:
        targets = []
        if card.number:
            targets.append(f"Number: {card.number}")
        if card.cardholder_name:
            targets.append(f"Cardholder: {card.cardholder_name}")
        if card.brand:
            targets.append(f"Brand: {card.brand}")
        if card.exp_month and card.exp_year:
            targets.append(f"Expiry: {card.exp_year:0>4}-{card.exp_month:0>2}")
        if card.code:
            targets.append(f"Code: {card.code[0]}{'*' * (len(card.code) - 1)}")
        if card.notes:
            targets.append(f"Notes: {card.notes}")
        for field in card.fields:
            targets.append(f"{self._format_further_item_name(field.key)}: {field.masked_string()}")

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

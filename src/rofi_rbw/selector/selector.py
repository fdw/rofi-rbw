import re
from abc import ABC, abstractmethod

from ..models.action import Action
from ..models.card import Card
from ..models.credentials import Credentials
from ..models.detailed_entry import DetailedEntry
from ..models.display_field_token import DisplayFieldToken
from ..models.entry import Entry
from ..models.keybinding import Keybinding
from ..models.note import Note
from ..models.targets import Target, Targets


class Selector(ABC):
    @staticmethod
    def best_option(name: str | None = None) -> "Selector":
        from .bemenu import Bemenu
        from .fuzzel import Fuzzel
        from .rofi import Rofi
        from .wofi import Wofi

        available_selectors = [Rofi, Wofi, Fuzzel, Bemenu]

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
        entries: list[Entry],
        prompt: str,
        show_help_message: bool,
        display_fields: list[DisplayFieldToken],
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None, Entry | None]:
        pass

    @abstractmethod
    def select_target(
        self,
        entry: DetailedEntry,
        show_help_message: bool,
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None]:
        pass

    def _format_entries(self, entries: list[Entry], display_fields: list[DisplayFieldToken]) -> list[str]:
        number_tokens = len(display_fields)
        formatted_entries = [[self._format_field(entry, token) for token in display_fields] for entry in entries]
        max_lengths = [max(len(field) for field in pivoted_fields) for pivoted_fields in zip(*formatted_entries)]

        return [
            "  ".join([entry[field_index].ljust(max_lengths[field_index]) for field_index in range(number_tokens)])
            for entry in formatted_entries
        ]

    def _find_entry(
        self, entries: list[Entry], formatted_string: str, display_fields: list[DisplayFieldToken]
    ) -> Entry:
        pattern = f"^{' {2,}'.join(f'(?P<{token.name.lower()}>.*?)' for token in display_fields)}$"
        match = re.compile(pattern).search(formatted_string)

        return next(
            entry
            for entry in entries
            if all(
                self._format_field(entry, token) == match.group(token.name.lower()).strip() for token in display_fields
            )
        )

    def _format_targets_from_entry(self, entry: DetailedEntry) -> list[str]:
        match entry:
            case Credentials():
                return self._format_targets_from_credential(entry)
            case Card():
                return self._format_targets_from_card(entry)
            case Note():
                return self._format_targets_from_note(entry)
            case _:
                return []

    def _format_targets_from_credential(self, credentials: Credentials) -> list[str]:
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

    def _format_targets_from_card(self, card: Card) -> list[str]:
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

    def _format_targets_from_note(self, note: Note) -> list[str]:
        targets = []
        if note.notes:
            value = note.notes.replace("\n", "|")
            targets.append(f"Notes: {value}")
        for field in note.fields:
            targets.append(f"{self._format_further_item_name(field.key)}: {field.masked_string()}")

        return targets

    def _format_further_item_name(self, key: str) -> str:
        if key.lower() in ["username", "password", "totp"] or re.match(r"^URI \d+$", key):
            return f"{key} (field)"
        return key

    def _format_action_and_targets(self, keybinding: Keybinding) -> str:
        if keybinding.targets and Targets.MENU in keybinding.targets:
            return "Menu"
        elif keybinding.action == Action.SYNC:
            return "Sync logins"
        elif keybinding.targets:
            return f"{keybinding.action.value.title()} {', '.join([target.raw for target in keybinding.targets])}"
        else:
            return keybinding.action.value.title()

    def _format_field(self, entry: Entry, token: DisplayFieldToken) -> str:
        match token:
            case DisplayFieldToken.NAME_ONLY:
                return entry.name
            case DisplayFieldToken.NAME_WITH_FOLDER:
                return f"{entry.folder}/{entry.name}" if entry.folder else entry.name
            case DisplayFieldToken.FOLDER:
                return entry.folder
            case DisplayFieldToken.USER:
                return entry.username
            case DisplayFieldToken.FIRST_URI:
                return entry.uris[0] if entry.uris else ""

    def _extract_targets(self, output: str) -> list[Target]:
        return [Target(line.split(":")[0]) for line in output.strip().split("\n")]


class NoSelectorFoundException(Exception):
    def __str__(self) -> str:
        return "Could not find a valid way to show the selection. Please check the required dependencies."

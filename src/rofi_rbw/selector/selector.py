from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Union

from ..models.action import Action
from ..models.card import Card
from ..models.credentials import Credentials
from ..models.detailed_entry import DetailedEntry
from ..models.entry import Entry
from ..models.keybinding import Keybinding
from ..models.note import Note
from ..models.targets import Target


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
        entries: List[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: List[Keybinding],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None], Union[Entry, None]]:
        pass

    @abstractmethod
    def select_target(
        self,
        entry: DetailedEntry,
        show_help_message: bool,
        keybindings: Dict[str, Action],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None]]:
        pass

    @abstractmethod
    def show_input_dialog(self, prompt: str, default_value: str = "") -> str | None:
        pass

    def _format_targets_from_entry(self, entry: DetailedEntry) -> List[str]:
        if isinstance(entry, Credentials):
            return self._format_targets_from_credential(entry)
        elif isinstance(entry, Card):
            return self._format_targets_from_card(entry)
        elif isinstance(entry, Note):
            return self._format_targets_from_note(entry)
        return []

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

    def _format_targets_from_note(self, note: Note) -> List[str]:
        targets = []
        if note.notes:
            notes_text = note.notes.replace('\n', '|')
            targets.append(f"Notes: {notes_text}")
        return targets

    def _format_further_item_name(self, key: str) -> str:
        """Format field names for display."""
        return key.replace('_', ' ').title()

    def _format_folder(self, entry: Entry, show_folders: bool) -> str:
        """Format folder display for an entry."""
        if show_folders and entry.folder:
            return f"{entry.folder}/"
        return ""

    def _calculate_max_width(self, entries: List[Entry], show_folders: bool) -> int:
        """Calculate the maximum width needed for entry names."""
        if not entries:
            return 0
        
        max_width = 0
        for entry in entries:
            folder_width = len(entry.folder) + 1 if show_folders and entry.folder else 0
            name_width = len(entry.name)
            total_width = folder_width + name_width
            max_width = max(max_width, total_width)
        
        return max_width

    def justify(self, entry: Entry, max_width: int, show_folders: bool) -> str:
        """Add spacing to justify entry display."""
        folder_width = len(entry.folder) + 1 if show_folders and entry.folder else 0
        name_width = len(entry.name)
        current_width = folder_width + name_width
        spaces_needed = max_width - current_width
        return " " * max(0, spaces_needed)

    def _extract_targets(self, selected_text: str) -> List[Target]:
        """Extract targets from selected text."""
        if not selected_text.strip():
            return []
        
        # Parse the selected text to extract the target type
        selected_text = selected_text.strip()
        
        if selected_text.startswith("Username:"):
            return [Target("username")]
        elif selected_text.startswith("Password:"):
            return [Target("password")]
        elif selected_text.startswith("TOTP:"):
            return [Target("totp")]
        elif selected_text.startswith("Notes:"):
            return [Target("notes")]
        elif selected_text.startswith("URI"):
            return [Target("uri")]
        elif selected_text.startswith("Number:"):
            return [Target("number")]
        elif selected_text.startswith("Cardholder:"):
            return [Target("cardholder")]
        elif selected_text.startswith("Brand:"):
            return [Target("brand")]
        elif selected_text.startswith("Expiry:"):
            return [Target("expiry")]
        elif selected_text.startswith("Code:"):
            return [Target("code")]
        else:
            # For custom fields, extract the field name
            if ":" in selected_text:
                field_name = selected_text.split(":")[0].strip()
                return [Target(field_name)]
            return []

class NoSelectorFoundException(Exception):
    def __str__(self) -> str:
        return "Could not find a valid selector. Please check the required dependencies."

import re
from subprocess import run

from ..abstractionhelper import is_installed
from ..models.action import Action
from ..models.detailed_entry import DetailedEntry
from ..models.entry import Entry
from ..models.keybinding import Keybinding
from ..models.targets import Target, Targets
from .selector import Selector


class Rofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_installed("rofi")

    @staticmethod
    def name() -> str:
        return "rofi"

    def show_selection(
        self,
        entries: list[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None, Entry | None]:
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

        return return_targets, return_action, self.__find_entry(entries, rofi.stdout)

    def __format_entries(self, entries: list[Entry], show_folders: bool) -> list[str]:
        max_width = self._calculate_max_width(entries, show_folders)
        return [
            f"{self._format_folder(it, show_folders)}<b>{it.name}</b>{self.justify(it, max_width, show_folders)}  {it.username}"
            for it in entries
        ]

    def __find_entry(self, entries: list[Entry], formatted_string: str) -> Entry:
        # Use \s+ to swallow padding
        pattern = re.compile(r"(?:(?P<folder>.+)/)?<b>(?P<name>.*?) *</b>\s*(?P<username>.*)")
        match = pattern.search(formatted_string.strip())

        if not match:
            raise Exception(f"Regex failed to parse selection: {formatted_string}")

        # Clean the captured data
        target_name = match.group("name")
        target_folder = match.group("folder") or "" # Normalize None to empty string
        target_user = match.group("username").strip()

        return next(
            entry for entry in entries
            if entry.name == target_name
            and (entry.folder or "") == target_folder
            and entry.username.strip() == target_user
        )

    def select_target(
        self,
        entry: DetailedEntry,
        show_help_message: bool,
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None]:
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
            input="\n".join(self._format_targets_from_entry(entry)),
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

    def __build_parameters_for_keybindings(self, keybindings: list[Keybinding]) -> list[str]:
        params = []
        for index, keybinding in enumerate(keybindings):
            params.extend([f"-kb-custom-{1 + index}", keybinding.shortcut])

        return params

    def __format_keybindings_message(self, keybindings: list[Keybinding]):
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

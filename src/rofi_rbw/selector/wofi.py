import re
from subprocess import run

from rofi_rbw.models.entry import Entry

from ..abstractionhelper import is_installed, is_wayland
from ..models.action import Action
from ..models.detailed_entry import DetailedEntry
from ..models.keybinding import Keybinding
from ..models.targets import Target
from .selector import Selector


class Wofi(Selector):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("wofi")

    @staticmethod
    def name() -> str:
        return "wofi"

    def show_selection(
        self,
        entries: list[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[None, Action | None, Entry | None]:
        parameters = ["wofi", "--dmenu", "-p", prompt, *additional_args]

        wofi = run(
            parameters,
            input="\n".join(self.__format_entries(entries, show_folders)),
            capture_output=True,
            encoding="utf-8",
        )
        if wofi.returncode == 0:
            return None, None, self.__find_entry(entries, wofi.stdout)
        else:
            return None, Action.CANCEL, None

    def __format_entries(self, entries: list[Entry], show_folders: bool) -> list[str]:
        max_width = self._calculate_max_width(entries, show_folders)
        return [
            f"{self._format_folder(it, show_folders)}{it.name}{self.justify(it, max_width, show_folders)}  {it.username}"
            for it in entries
        ]

    def __find_entry(self, entries: list[Entry], formatted_string: str) -> Entry:
        match = re.compile("(?:(?P<folder>.+)/)?(?P<name>.*?) *  (?P<username>.*)").search(formatted_string)

        return next(
            entry
            for entry in entries
            if entry.name == match.group("name")
            and (match.group("folder") is None or entry.folder == match.group("folder"))
            and (match.group("username") is None or entry.username == match.group("username").strip())
        )

    def select_target(
        self,
        entry: DetailedEntry,
        show_help_message: bool,
        keybindings: dict[str, Action],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None]:
        parameters = ["wofi", "--dmenu", "-p", "Choose target", *additional_args]

        wofi = run(
            parameters,
            input="\n".join(self._format_targets_from_entry(entry)),
            capture_output=True,
            encoding="utf-8",
        )

        if wofi.returncode == 1:
            return None, Action.CANCEL

        return self._extract_targets(wofi.stdout), None

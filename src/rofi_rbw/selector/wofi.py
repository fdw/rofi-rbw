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
            input="\n".join(self._format_entries(entries, show_folders)),
            capture_output=True,
            encoding="utf-8",
        )
        if wofi.returncode == 0:
            return None, None, self._find_entry(entries, wofi.stdout)
        else:
            return None, Action.CANCEL, None

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

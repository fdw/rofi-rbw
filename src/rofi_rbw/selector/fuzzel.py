from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from ..models.action import Action
from ..models.detailed_entry import DetailedEntry
from ..models.entry import Entry
from ..models.keybinding import Keybinding
from ..models.targets import Target
from .selector import Selector


class Fuzzel(Selector):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("fuzzel")

    @staticmethod
    def name() -> str:
        return "fuzzel"

    def show_selection(
        self,
        entries: list[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[None, Action | None, Entry | None]:
        parameters = ["fuzzel", "--dmenu", "-p", prompt, *additional_args]

        fuzzel = run(
            parameters,
            input="\n".join(self._format_entries(entries, show_folders)),
            capture_output=True,
            encoding="utf-8",
        )
        if fuzzel.returncode == 0:
            return None, None, self._find_entry(entries, fuzzel.stdout)
        else:
            return None, Action.CANCEL, None

    def select_target(
        self,
        entry: DetailedEntry,
        show_help_message: bool,
        keybindings: dict[str, Action],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None]:
        parameters = ["fuzzel", "--dmenu", "-p", "Choose target", *additional_args]

        fuzzel = run(
            parameters,
            input="\n".join(self._format_targets_from_entry(entry)),
            capture_output=True,
            encoding="utf-8",
        )

        if fuzzel.returncode == 1:
            return None, Action.CANCEL

        return self._extract_targets(fuzzel.stdout), None

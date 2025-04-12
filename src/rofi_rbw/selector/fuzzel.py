import re
from subprocess import run
from typing import Dict, List, Tuple, Union

from ..abstractionhelper import is_installed, is_wayland
from ..credentials import Card, Credentials
from ..entry import Entry
from ..models import Action, Target
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
        entries: List[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: Dict[str, Tuple[Action, List[Target]]],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None], Union[Entry, None]]:
        parameters = ["fuzzel", "--dmenu", "-p", prompt, *additional_args]

        fuzzel = run(
            parameters,
            input="\n".join(self.__format_entries(entries, show_folders)),
            capture_output=True,
            encoding="utf-8",
        )
        if fuzzel.returncode == 0:
            return None, None, self.__parse_formatted_string(fuzzel.stdout)
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
        entry: Union[Credentials, Card],
        show_help_message: bool,
        keybindings: Dict[str, Action],
        additional_args: List[str],
    ) -> Tuple[Union[List[Target], None], Union[Action, None]]:
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

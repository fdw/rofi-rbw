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
    ) -> tuple[list[Target] | None, Action | None, Entry | None]:
        parameters = [
            "fuzzel",
            "--dmenu",
            "--index",
            "-p",
            prompt,
            *self.__build_parameters_for_keybindings(keybindings),
            *additional_args,
        ]

        if show_help_message and keybindings:
            parameters.extend(self.__format_keybindings_message(keybindings))

        fuzzel = run(
            parameters,
            input="\n".join(self._format_entries(entries, show_folders)),
            capture_output=True,
            encoding="utf-8",
        )

        if fuzzel.returncode == 1:
            return None, Action.CANCEL, None
        elif fuzzel.returncode >= 10:
            keybinding = keybindings[(fuzzel.returncode - 10)]
            return_action = keybinding.action
            return_targets = keybinding.targets
        else:
            return_action = None
            return_targets = None

        selected = entries[int(fuzzel.stdout.strip())] if fuzzel.stdout.strip() else None
        return return_targets, return_action, selected

    def select_target(
        self,
        entry: DetailedEntry,
        show_help_message: bool,
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None]:
        parameters = [
            "fuzzel",
            "--dmenu",
            "-p",
            "Choose target",
            *self.__build_parameters_for_keybindings(keybindings),
            *additional_args,
        ]

        if show_help_message and keybindings:
            parameters.extend(self.__format_keybindings_message(keybindings))

        fuzzel = run(
            parameters,
            input="\n".join(self._format_targets_from_entry(entry)),
            capture_output=True,
            encoding="utf-8",
        )

        if fuzzel.returncode == 1:
            return None, Action.CANCEL
        elif fuzzel.returncode >= 10:
            action = keybindings[(fuzzel.returncode - 10)].action
        else:
            action = None

        return (self._extract_targets(fuzzel.stdout)), action

    def __build_parameters_for_keybindings(self, keybindings: list[Keybinding]) -> list[str]:
        params = []
        for index, keybinding in enumerate(keybindings):
            params.append(f"--override=key-bindings.custom-{1 + index}={self.__translate_shortcut(keybinding.shortcut)}")
        return params

    def __translate_shortcut(self, shortcut: str) -> str:
        return "+".join("Mod1" if token == "Alt" else token for token in shortcut.split("+"))

    def __format_keybindings_message(self, keybindings: list[Keybinding]) -> list[str]:
        return [
            "--mesg",
            " | ".join(
                f"{keybinding.shortcut}: {self._format_action_and_targets(keybinding)}"
                for keybinding in keybindings
            ),
        ]

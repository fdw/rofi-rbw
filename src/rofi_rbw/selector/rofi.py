from subprocess import run

from ..abstractionhelper import is_installed
from ..models.action import Action
from ..models.detailed_entry import DetailedEntry
from ..models.display_field_token import DisplayFieldToken
from ..models.entry import Entry
from ..models.keybinding import Keybinding
from ..models.targets import Target
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
        display_fields: list[DisplayFieldToken],
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None, Entry | None]:
        parameters = [
            "rofi",
            "-markup-rows",
            "-dmenu",
            "-format",
            "i",
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
            input="\n".join(self._format_entries(entries, display_fields)),
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

        return return_targets, return_action, (entries[int(rofi.stdout.strip())])

    def _format_field(self, entry: Entry, token: DisplayFieldToken) -> str:
        match token:
            case DisplayFieldToken.NAME_ONLY:
                return f"<b>{super()._format_field(entry, token)}</b>"
            case DisplayFieldToken.NAME_WITH_FOLDER:
                if entry.folder:
                    return f"{entry.folder}/<b>{entry.name}</b>"
                return f"<b>{entry.name}</b>"
            case _:
                return super()._format_field(entry, token)

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
                    f"<b>{keybinding.shortcut}</b>: {self._format_action_and_targets(keybinding)}"
                    for keybinding in keybindings
                ]
            ),
        ]

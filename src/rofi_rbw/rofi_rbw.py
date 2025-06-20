import time
from subprocess import run
from typing import List, Tuple, Union

from .argument_parsing import parse_arguments
from .cache import Cache
from .clipboarder.clipboarder import Clipboarder
from .models.action import Action
from .models.credentials import Credentials
from .models.detailed_entry import DetailedEntry
from .models.targets import Target, Targets, TypeTargets
from .rbw import Rbw
from .selector.selector import Selector
from .typer.typer import Key, Typer


class RofiRbw(object):
    def __init__(self) -> None:
        self.args = parse_arguments()
        self.rbw = Rbw()
        self.selector = Selector.best_option(self.args.selector)
        self.typer = Typer.best_option(self.args.typer)
        self.clipboarder = Clipboarder.best_option(self.args.clipboarder)
        self.active_window = self.typer.get_active_window()

    def main(self) -> None:
        entries = self.rbw.list_entries()

        if self.args.use_cache:
            cache = Cache()
            entries = cache.sorted(entries)

        (selected_targets, selected_action, selected_entry) = self.selector.show_selection(
            entries,
            self.args.prompt,
            self.args.show_help,
            self.args.show_folders,
            self.args.parsed_keybindings,
            self.args.selector_args,
        )

        if selected_action == Action.SYNC:
            self.rbw.sync()
            (selected_targets, selected_action, selected_entry) = self.selector.show_selection(
                self.rbw.list_entries(),
                self.args.prompt,
                self.args.show_help,
                self.args.show_folders,
                self.args.parsed_keybindings,
                self.args.selector_args,
            )

        if selected_action == Action.CANCEL:
            return

        entry = self.rbw.fetch_credentials(selected_entry)

        if self.args.use_cache:
            cache.update(selected_entry)

        if selected_targets is not None:
            self.args.targets = selected_targets

        if selected_action is not None:
            self.args.action = selected_action

        if self.args.targets is not None and Targets.MENU in self.args.targets:
            targets, action = self.__show_target_menu(
                entry,
                self.args.show_help,
            )
            self.args.targets = targets
            if action is not None:
                self.args.action = action

        self.__execute_action(entry)

    def __show_target_menu(
        self, entry: DetailedEntry, show_help_message: bool
    ) -> Tuple[List[Target], Union[Action, None]]:
        targets, action = self.selector.select_target(
            entry, show_help_message, self.args.parsed_menu_keybindings, additional_args=self.args.selector_args
        )

        if action == Action.CANCEL:
            self.main()
            exit(0)

        return targets, action

    def __execute_action(self, detailed_entry: DetailedEntry) -> None:
        targets = self.__configure_targets(detailed_entry)
        if self.args.action == Action.TYPE:
            self.__type_targets(detailed_entry, targets)
        elif self.args.action == Action.COPY:
            for target in targets:
                self.clipboarder.copy_to_clipboard(detailed_entry[target])
            if len(targets) == 1 and targets[0] == Targets.PASSWORD:
                self.clipboarder.clear_clipboard_after(self.args.clear)
        elif self.args.action == Action.PRINT:
            print("\n".join([detailed_entry[target] for target in targets]))

    def __configure_targets(self, detailed_entry: DetailedEntry) -> List[Target]:
        if self.args.targets:
            return self.args.targets

        if self.args.action == Action.TYPE:
            if detailed_entry.autotype_sequence is not None:
                return detailed_entry.autotype_sequence
            else:
                return [Targets.USERNAME, TypeTargets.TAB, Targets.PASSWORD]

        return [Targets.USERNAME, Targets.PASSWORD]

    def __type_targets(self, detailed_entry: DetailedEntry, targets: List[Target]):
        for target in targets:
            if target == TypeTargets.DELAY:
                time.sleep(1)
            elif target == TypeTargets.ENTER:
                self.typer.press_key(Key.ENTER)
            elif target == TypeTargets.TAB:
                self.typer.press_key(Key.TAB)
            else:
                self.typer.type_characters(detailed_entry[target], self.args.key_delay, self.active_window)
        if Targets.PASSWORD in targets and isinstance(detailed_entry, Credentials) and detailed_entry.totp != "":
            self.clipboarder.copy_to_clipboard(detailed_entry.totp)
            if self.args.use_notify_send:
                run(["notify-send", "-u", "normal", "-t", "3000", "rofi-rbw", "totp copied to clipboard"], check=True)

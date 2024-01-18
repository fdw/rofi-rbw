from typing import List, Tuple, Union

from .argument_parsing import parse_arguments
from .cache import Cache
from .clipboarder.clipboarder import Clipboarder
from .credentials import Credentials
from .models import Action, Target, Targets
from .rbw import Rbw
from .selector.selector import Selector
from .typer.typer import Typer


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

        credential = self.rbw.fetch_credentials(selected_entry)

        if self.args.use_cache:
            cache.update(credential)

        if selected_targets is not None:
            self.args.targets = selected_targets

        if selected_action is not None:
            self.args.action = selected_action

        if Targets.MENU in self.args.targets:
            targets, action = self.__show_target_menu(
                credential,
                self.args.show_help,
            )
            self.args.targets = targets
            if action is not None:
                self.args.action = action

        self.__execute_action(credential)

    def __show_target_menu(
        self, cred: Credentials, show_help_message: bool
    ) -> Tuple[List[Target], Union[Action, None]]:
        targets, action = self.selector.select_target(
            cred, show_help_message, self.args.parsed_menu_keybindings, additional_args=self.args.selector_args
        )

        if action == Action.CANCEL:
            self.main()
            exit(0)

        return targets, action

    def __execute_action(self, cred: Credentials) -> None:
        if self.args.action == Action.TYPE:
            characters = "\t".join([cred[target] for target in self.args.targets])
            self.typer.type_characters(characters, self.active_window)
            if Targets.PASSWORD in self.args.targets and cred.totp != "":
                self.clipboarder.copy_to_clipboard(cred.totp)
        elif self.args.action == Action.COPY:
            for target in self.args.targets:
                self.clipboarder.copy_to_clipboard(cred[target])
            if len(self.args.targets) == 1 and self.args.targets[0] == Targets.PASSWORD:
                self.clipboarder.clear_clipboard_after(self.args.clear)
        elif self.args.action == Action.PRINT:
            print("\n".join([cred[target] for target in self.args.targets]))

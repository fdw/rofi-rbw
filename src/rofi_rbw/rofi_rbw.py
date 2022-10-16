import argparse
import shlex
from typing import List, Tuple, Union

import configargparse

from .clipboarder import Clipboarder
from .credentials import Credentials
from .models import Action, Target, Targets, CANCEL, DEFAULT, SYNC
from .paths import *
from .rbw import Rbw
from .selector import Selector
from .typer import Typer

__version__ = '1.0.1'


class RofiRbw(object):
    def __init__(self) -> None:
        self.args = self.__parse_arguments()
        self.rbw = Rbw()
        self.selector = Selector.best_option(self.args.selector)
        self.typer = Typer.best_option(self.args.typer)
        self.clipboarder = Clipboarder.best_option(self.args.clipboarder)
        self.active_window = self.typer.get_active_window()

    def __parse_arguments(self) -> argparse.Namespace:
        parser = configargparse.ArgumentParser(
            description='Insert or copy passwords and usernames from Bitwarden using rofi.',
            default_config_files=config_file_locations
        )
        parser.add_argument('--version', action='version', version='rofi-rbw ' + __version__)
        parser.add_argument(
            '--action',
            '-a',
            dest='action',
            action='store',
            choices=[action.value for action in Action],
            default=Action.TYPE.value,
            help='What to do with the selected entry'
        )
        parser.add_argument(
            '--target',
            '-t',
            dest='targets',
            action='append',
            help='Which part of the entry do you want?'
        )
        parser.add_argument(
            '--prompt',
            '-r',
            dest='prompt',
            action='store',
            default='Select entry',
            help='Set rofi-rbw\'s  prompt'
        )
        parser.add_argument(
            '--selector-args',
            dest='selector_args',
            action='store',
            default='',
            help='A string of arguments to give to the selector'
        )
        parser.add_argument(
            '--selector',
            dest='selector',
            action='store',
            type=str,
            choices=['rofi', 'wofi'],
            default=None,
            help='Choose the application to select the characters with'
        )
        parser.add_argument(
            '--clipboarder',
            dest='clipboarder',
            action='store',
            type=str,
            choices=['xsel', 'xclip', 'wl-copy'],
            default=None,
            help='Choose the application to access the clipboard with'
        )
        parser.add_argument(
            '--typer',
            dest='typer',
            action='store',
            type=str,
            choices=['xdotool', 'wtype', 'ydotool'],
            default=None,
            help='Choose the application to type with'
        )
        parser.add_argument(
            '--clear-after',
            dest='clear',
            action='store',
            type=int,
            default=0,
            help='Limit the duration in seconds passwords stay in your clipboard. When not set or <= 0, passwords stay indefinitely.'
        )
        parser.add_argument(
            '--no-help',
            dest='show_help',
            action='store_false',
            help='Don\'t show a help message about the shortcuts'
        )

        parsed_args = parser.parse_args()

        parsed_args.selector_args = shlex.split(parsed_args.selector_args)

        parsed_args.action = Action(parsed_args.action)

        if parsed_args.targets:
            parsed_args.targets = [Target(target) for target in parsed_args.targets]
        else:
            parsed_args.targets = [Targets.USERNAME, Targets.PASSWORD]

        return parsed_args

    def main(self) -> None:
        (selected_targets, selected_action, selected_entry) = self.selector.show_selection(
            self.rbw.list_entries(),
            self.args.prompt,
            self.args.show_help,
            self.args.selector_args
        )
        
        if selected_action == SYNC():
            self.rbw.sync()
            (selected_targets, selected_action, selected_entry) = self.selector.show_selection(
                self.rbw.list_entries(),
                self.args.prompt,
                self.args.show_help,
                self.args.selector_args
            )

        if selected_action == CANCEL():
            return

        credential = self.rbw.fetch_credentials(selected_entry)

        if selected_targets != DEFAULT():
            self.args.targets = selected_targets

        if selected_action != DEFAULT():
            self.args.action = selected_action

        if Targets.MENU in self.args.targets:
            targets, action = self.__show_target_menu(credential, self.args.show_help, )
            self.args.targets = targets
            if action != DEFAULT():
                self.args.action = action

        self.__execute_action(credential)

    def __show_target_menu(
        self,
        cred: Credentials,
        show_help_message: bool
    ) -> Tuple[List[Target], Union[Action, DEFAULT]]:


        targets, action = self.selector.select_target(cred, show_help_message, additional_args=self.args.selector_args)

        if targets == CANCEL():
            self.main()
            return

        return targets, action

    def __execute_action(self, cred: Credentials) -> None:
        if self.args.action == Action.TYPE:
            characters = '\t'.join([cred[target] for target in self.args.targets])
            self.typer.type_characters(characters, self.active_window)
            if Targets.PASSWORD in self.args.targets and cred.totp != "":
                self.clipboarder.copy_to_clipboard(cred.totp)
        elif self.args.action == Action.COPY:
            for target in self.args.targets:
                self.clipboarder.copy_to_clipboard(cred[target])
            if len(self.args.targets) == 1 and self.args.targets[0] == Targets.PASSWORD:
                self.clipboarder.clear_clipboard_after(self.args.clear)
        elif self.args.action == Action.PRINT:
            print('\n'.join([cred[target] for target in self.args.targets]))

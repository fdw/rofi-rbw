import argparse
import shlex
from subprocess import run
from typing import List, Tuple, Union

import configargparse

from .models import Action, Target, Targets, CANCEL, DEFAULT
from .clipboarder import Clipboarder
from .typer import Typer
from .selector import Selector
from .credentials import Credentials
from .entry import Entry
from .paths import *

__version__ = '1.0.1'


class RofiRbw(object):
    def __init__(self) -> None:
        self.args = self.parse_arguments()
        self.selector = Selector.best_option(self.args.selector)
        self.typer = Typer.best_option(self.args.typer)
        self.clipboarder = Clipboarder.best_option(self.args.clipboarder)
        self.active_window = self.typer.get_active_window()

    def parse_arguments(self) -> argparse.Namespace:
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
        parsed_entries = self.get_entries()
        maxwidth = max(len(it) for it in parsed_entries)
        entries = sorted(it.formatted_string(maxwidth) for it in parsed_entries)

        (selected_targets, selected_action, selected_string) = self.selector.show_selection(
            entries,
            self.args.prompt,
            self.args.show_help,
            self.args.selector_args
        )
        if selected_action == CANCEL():
            return

        selected_entry = Entry.parse_formatted_string(selected_string)

        credential = self.get_credentials(selected_entry.name, selected_entry.folder, selected_entry.username)

        if selected_targets != DEFAULT():
            self.args.targets = selected_targets

        if selected_action != DEFAULT():
            self.args.action = selected_action

        if Targets.MENU in self.args.targets:
            targets, action = self.show_target_menu(credential, self.args.show_help,)
            self.args.targets = targets
            if action != DEFAULT():
                self.args.action = action

        self.execute_action(credential)

    def get_entries(self):
        rofi = run(
            ['rbw', 'ls', '--fields', 'folder,name,user'],
            encoding='utf-8',
            capture_output=True
        )

        if rofi.returncode != 0:
            print('There was a problem calling rbw. Is it correctly configured?')
            print(rofi.stderr)
            exit(2)

        return [Entry.parse_rbw_output(it) for it in (rofi.stdout.strip().split('\n'))]

    def get_credentials(self, name: str, folder: str, username: str) -> Credentials:
        return Credentials(name, username, folder)

    def show_target_menu(
        self,
        cred: Credentials,
        show_help_message: bool
    ) -> Tuple[List[Target], Union[Action, DEFAULT]]:
        entries = []
        if cred.username:
            entries.append(f'Username: {cred.username}')
        if cred.password:
            entries.append(f'Password: {cred.password[0]}{"*" * (len(cred.password) - 1)}')
        if cred.has_totp:
            entries.append(f'TOTP: {cred.totp}')
        if len(cred.uris) == 1:
            entries.append(f'URI: {cred.uris[0]}')
        else:
            for (key, value) in enumerate(cred.uris):
                entries.append(f'URI {key + 1}: {value}')
        for (key, value) in cred.further.items():
            entries.append(f'{key}: {value[0]}{"*" * (len(value) - 1)}')

        targets, action = self.selector.select_target(entries, show_help_message, additional_args=self.args.selector_args)

        if targets == CANCEL():
            self.main()
            return

        return targets, action

    def execute_action(self, cred: Credentials) -> None:
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

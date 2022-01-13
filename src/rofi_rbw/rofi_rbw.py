#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import enum
import shlex
from subprocess import run

import configargparse

try:
    from rofi_rbw.clipboarder import Clipboarder
    from rofi_rbw.typer import Typer
    from rofi_rbw.selector import Selector
    from rofi_rbw.credentials import Credentials
    from rofi_rbw.entry import Entry
    from rofi_rbw.paths import *
except ModuleNotFoundError:
    from clipboarder import Clipboarder
    from typer import Typer
    from selector import Selector
    from credentials import Credentials
    from entry import Entry
    from paths import *

__version__ = '0.5.0'


class RofiRbw(object):
    class Action(enum.Enum):
        TYPE_PASSWORD = 'type-password'
        TYPE_USERNAME = 'type-username'
        TYPE_BOTH = 'autotype'
        COPY_USERNAME = 'copy-username'
        COPY_PASSWORD = 'copy-password'
        COPY_TOTP = 'copy-totp'
        AUTOTYPE_MENU = 'menu'

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
            choices=[action.value for action in self.Action],
            default=self.Action.TYPE_PASSWORD.value,
            help='What to do with the selected entry'
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
            '--rofi-args',
            dest='rofi_args',
            action='store',
            default='',
            help='A string of arguments to give to rofi'
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
            '--no-help',
            dest='show_help',
            action='store_false',
            help='Don\'t show a help message about the shortcuts'
        )

        parsed_args = parser.parse_args()
        parsed_args.selector_args = shlex.split(parsed_args.selector_args)
        if parsed_args.rofi_args and not parsed_args.selector_args:
            print("The --rofi-args option is deprecated. Please migrate to using --selector-args exclusively.")
            parsed_args.selector_args = shlex.split(parsed_args.rofi_args)

        parsed_args.action = next(action for action in self.Action if action.value == parsed_args.action)

        return parsed_args

    def main(self) -> None:
        parsed_entries = self.get_entries()
        maxwidth = max(len(it) for it in parsed_entries)
        entries = sorted(it.formatted_string(maxwidth) for it in parsed_entries)

        (returncode, selected_string) = self.selector.show_selection(
            entries,
            self.args.prompt,
            self.args.show_help,
            self.args.selector_args
        )
        if returncode == 1:
            return
        self.choose_action_from_return_code(returncode)

        selected_entry = Entry.parse_formatted_string(selected_string)

        data = self.get_credentials(selected_entry.name, selected_entry.folder, selected_entry.username)

        self.execute_action(data)

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

    def choose_action_from_return_code(self, return_code: int) -> None:
        if return_code == 12:
            self.args.action = self.Action.TYPE_PASSWORD
        elif return_code == 11:
            self.args.action = self.Action.TYPE_USERNAME
        elif return_code == 10:
            self.args.action = self.Action.TYPE_BOTH
        elif return_code == 13:
            self.args.action = self.Action.AUTOTYPE_MENU
        elif return_code == 20:
            self.args.action = self.Action.COPY_PASSWORD
        elif return_code == 21:
            self.args.action = self.Action.COPY_USERNAME
        elif return_code == 22:
            self.args.action = self.Action.COPY_TOTP

    def execute_action(self, cred: Credentials) -> None:
        if self.args.action == self.Action.TYPE_PASSWORD:
            self.typer.type_characters(cred.password, self.active_window)
            if cred.totp != "":
                self.clipboarder.copy_to_clipboard(cred.totp)
        elif self.args.action == self.Action.TYPE_USERNAME:
            self.typer.type_characters(cred.username, self.active_window)
        elif self.args.action == self.Action.TYPE_BOTH:
            self.typer.type_characters(f"{cred.username}\t{cred.password}", self.active_window)
            if cred.totp != "":
                self.clipboarder.copy_to_clipboard(cred.totp)
        elif self.args.action == self.Action.COPY_PASSWORD:
            self.clipboarder.copy_to_clipboard(cred.password)
        elif self.args.action == self.Action.COPY_USERNAME:
            self.clipboarder.copy_to_clipboard(cred.username)
        elif self.args.action == self.Action.COPY_TOTP:
            self.clipboarder.copy_to_clipboard(cred.totp)
        elif self.args.action == self.Action.AUTOTYPE_MENU:
            self.show_autotype_menu(cred)

    def get_credentials(self, name: str, folder: str, username: str) -> Credentials:
        return Credentials(name, username, folder)

    def show_autotype_menu(self, cred: Credentials):
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

        (returncode, entry) = self.selector.show_selection(
            entries,
            prompt='Autotype field',
            show_help_message=False,
            additional_args=[]
        )

        if returncode == 1:
            self.main()
            return

        key, value = entry.split(': ', 1)

        if key == 'URI':
            value = cred.uris[0]
        elif key.startswith('URI'):
            value = cred.uris[int(key[4:]) - 1]
        else:
            value = cred[key]

        self.typer.type_characters(value, self.active_window)


def main():
    RofiRbw().main()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import enum
import shlex
import sys
from collections import namedtuple
from subprocess import run

import configargparse

try:
    from rofi_rbw.clipboarder import Clipboarder
    from rofi_rbw.typer import Typer
    from rofi_rbw.selector import Selector
    from rofi_rbw.credentials import Credentials
    from rofi_rbw.paths import *
except ModuleNotFoundError:
    from clipboarder import Clipboarder
    from typer import Typer
    from selector import Selector
    from credentials import Credentials
    from paths import *

__version__ = '0.4.0'


class RofiRbw(object):
    class Action(enum.Enum):
        TYPE_PASSWORD = 'type-password'
        TYPE_USERNAME = 'type-username'
        TYPE_BOTH = 'autotype'
        COPY_USERNAME = 'copy-username'
        COPY_PASSWORD = 'copy-password'
        COPY_TOTP = 'copy-totp'

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
            '--show-help',
            dest='show_help',
            action='store',
            type=bool,
            default=True,
            help='Show a help message about the shortcuts'
        )

        parsed_args = parser.parse_args()
        parsed_args.rofi_args = shlex.split(parsed_args.rofi_args)
        parsed_args.action = next(action for action in self.Action if action.value == parsed_args.action)

        return parsed_args

    def main(self) -> None:
        entries = run(
            ['rbw', 'ls', '--fields', 'folder,name'],
            encoding='utf-8',
            capture_output=True
        ).stdout.strip().split('\n')
        entries = sorted(map(lambda it: it.replace('\t', '/'), entries))

        (returncode, entry) = self.selector.show_selection(
            '\n'.join(entries),
            self.args.prompt,
            self.args.show_help,
            self.args.rofi_args
        )
        self.choose_action_from_return_code(returncode)

        (selected_folder, selected_entry) = entry.rsplit('/', 1)

        data = self.get_credentials(selected_entry.strip(), selected_folder.strip())

        self.execute_action(data)

    def choose_action_from_return_code(self, return_code: int) -> None:
        if return_code == 1:
            sys.exit()
        elif return_code == 12:
            self.args.action = self.Action.TYPE_PASSWORD
        elif return_code == 11:
            self.args.action = self.Action.TYPE_USERNAME
        elif return_code == 10:
            self.args.action = self.Action.TYPE_BOTH
        elif return_code == 20:
            self.args.action = self.Action.COPY_PASSWORD
        elif return_code == 21:
            self.args.action = self.Action.COPY_USERNAME
        elif return_code == 22:
            self.args_action = self.Action.COPY_TOTP

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

    def get_credentials(self, name: str, folder: str) -> Credentials:
        command = ['rbw', 'get', '--full', name]
        if folder != "":
            command.extend(["--folder", folder])

        result = run(
            command,
            capture_output=True,
            encoding='utf-8'
        ).stdout

        return Credentials(result)


def main():
    RofiRbw().main()


if __name__ == "__main__":
    main()

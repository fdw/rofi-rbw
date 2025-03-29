import argparse
import shlex

import configargparse

from . import __version__
from .models import Action, Keybinding, Target, TypeTarget
from .paths import config_file_locations


def parse_arguments() -> argparse.Namespace:
    parser = configargparse.ArgumentParser(
        description="Insert or copy passwords and usernames from Bitwarden using rofi or rofi-likes.",
        default_config_files=config_file_locations,
    )
    parser.add_argument("--version", action="version", version="rofi-rbw " + __version__)
    parser.add_argument(
        "--action",
        "-a",
        dest="action",
        action="store",
        choices=[action.value for action in Action],
        default=Action.TYPE.value,
        help="What to do with the selected entry",
    )
    parser.add_argument("--target", "-t", dest="targets", action="append", help="Which part of the entry do you want?")
    parser.add_argument(
        "--prompt", "-r", dest="prompt", action="store", default="Choose entry", help="Set rofi-rbw's prompt"
    )
    parser.add_argument(
        "--selector-args",
        dest="selector_args",
        action="store",
        default="",
        help="A string of arguments to give to the selector",
    )
    parser.add_argument(
        "--selector",
        dest="selector",
        action="store",
        type=str,
        choices=["rofi", "wofi", "fuzzel"],
        default=None,
        help="Choose the selector frontend",
    )
    parser.add_argument(
        "--clipboarder",
        dest="clipboarder",
        action="store",
        type=str,
        choices=["xsel", "xclip", "wl-copy"],
        default=None,
        help="Choose the application to access the clipboard with",
    )
    parser.add_argument(
        "--typer",
        dest="typer",
        action="store",
        type=str,
        choices=["xdotool", "wtype", "ydotool", "dotool"],
        default=None,
        help="Choose the application to type with",
    )
    parser.add_argument(
        "--clear-after",
        dest="clear",
        action="store",
        type=int,
        default=0,
        help="Limit the duration in seconds passwords stay in your clipboard. When not set or <= 0, passwords stay indefinitely.",
    )
    parser.add_argument(
        "--no-help", dest="show_help", action="store_false", help="Don't show a help message about the shortcuts"
    )
    parser.add_argument("--no-folder", dest="show_folders", action="store_false", help="Don't show the entry's folder")
    parser.set_defaults(show_folders=True)
    parser.add_argument("--no-cache", dest="use_cache", action="store_false", help="Don't save history in cache")
    parser.set_defaults(use_cache=True)
    parser.add_argument(
        "--use-notify-send",
        dest="use_notify_send",
        action="store_true",
        help="Send desktop notification after copying TOTP",
    )
    parser.set_defaults(use_notify_send=False)
    parser.add_argument(
        "--keybindings",
        dest="keybindings",
        action="store",
        type=str,
        default=",".join(
            [
                "Alt+1:type:username:tab:password",
                "Alt+2:type:username",
                "Alt+3:type:password",
                "Alt+4:type:totp",
                "Alt+c:copy:password",
                "Alt+u:copy:username",
                "Alt+t:copy:totp",
                "Alt+m::menu",
                "Alt+s:sync",
            ]
        ),
        help="Define keyboard shortcuts in the format <shortcut>:<action>:<target>, separated with a comma",
    )
    parser.add_argument(
        "--menu-keybindings",
        dest="menu_keybindings",
        action="store",
        type=str,
        default=",".join(["Alt+t:type", "Alt+c:copy"]),
        help="Define the keyboard shortcuts in the target menu in the format <shortcut>:<action> separated with a comma",
    )
    parser.add_argument(
        "--typing-key-delay",
        dest="key_delay",
        action="store",
        type=int,
        default=0,
        help="Set the delay between key presses when typing.",
    )

    parsed_args = parser.parse_args()

    parsed_args.selector_args = shlex.split(parsed_args.selector_args)

    parsed_args.action = Action(parsed_args.action)

    if parsed_args.targets:
        parsed_args.targets = [Target(target) for target in parsed_args.targets]
    else:
        parsed_args.targets = None

    parsed_args.parsed_keybindings = []
    for keybinding in parsed_args.keybindings.split(","):
        elements = keybinding.split(":")
        parsed_args.parsed_keybindings.append(
            Keybinding(
                elements[0],
                Action(elements[1]) if elements[1] else None,
                [TypeTarget(target_string) for target_string in elements[2:]],
            )
        )

    parsed_args.parsed_menu_keybindings = []
    for keybinding in parsed_args.menu_keybindings.split(","):
        elements = keybinding.split(":")
        parsed_args.parsed_menu_keybindings.append(
            Keybinding(elements[0], Action(elements[1]) if elements[1] else None, None)
        )

    return parsed_args

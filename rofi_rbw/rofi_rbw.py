#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import namedtuple
from subprocess import run
from time import sleep

Data = namedtuple('Data', ['username', 'password'])


def main() -> None:
    active_window = run(args=['xdotool', 'getactivewindow'],
                        capture_output=True, encoding='utf-8').stdout[:-1]

    entries = run(
        ['rbw', 'ls', '--fields', 'folder,name'],
        encoding='utf-8',
        capture_output=True
    ).stdout.strip().split('\n')
    entries = sorted(map(lambda it: it.replace('\t', '/'), entries))

    rofi = run(
        [
            'rofi',
            '-p',
            'Select entry',
            '-dmenu',
            '-kb-custom-11',
            'Alt+p',
            '-kb-custom-12',
            'Alt+u'
        ],
        encoding='utf-8',
        input='\n'.join(entries),
        capture_output=True
    )

    (selected_folder, selected_entry) = rofi.stdout.rsplit('/', 1)

    data = get_data(selected_entry.strip(), selected_folder.strip())

    if rofi.returncode == 0 or rofi.returncode == 12:
        type(data.password, active_window)
    elif rofi.returncode == 11:
        type(data.username, active_window)
    elif rofi.returncode == 10:
        type(f"{data.username}\t{data.password}", active_window)
    elif rofi.returncode == 20:
        copy_to_clipboard(data.password)
    elif rofi.returncode == 21:
        copy_to_clipboard(data.username)


def get_data(name: str, folder: str) -> Data:
    command = ['rbw', 'get', '--full', name]
    if folder != "":
        command.extend(["--folder", folder])

    result = run(
        command,
        capture_output=True,
        encoding='utf-8'
    ).stdout.split('\n')

    password = result[0].strip()
    username = extract_username(result)

    return Data(username, password)


def extract_username(result: [str]) -> str:
    for resultline in result:
        if resultline.startswith('Username:'):
            return resultline.replace('Username: ', '')
    return ""


def type(text: str, active_window: str) -> None:
    sleep(0.05)
    run([
        'xdotool',
        'type',
        '--window',
        active_window,
        '--clearmodifiers',
        text
    ])


def copy_to_clipboard(text: str) -> None:
    run(['xsel', '-i', '-b'], encoding='utf-8', input=text)


if __name__ == "__main__":
    main()

# rbw-rofi
## A rofi frontend for Bitwarden

Based on the alternative [Bitwarden](https://bitwarden.com/) CLI [rbw](https://github.com/doy/rbw/) and inspired by [rofi-pass](https://github.com/carnager/rofi-pass), `rbw-rofi` is a simplistic password typer/copier using [rofi](https://github.com/davatorium/rofi) and [wofi](https://hg.sr.ht/~scoopta/wofi).

## Features
- Autotype password or username (`Enter`/`Alt+3` and `Alt+2`, respectively)
- Autotype username and password (with a `tab` character in between) with `Alt+1` (and copy TOTP to clipboard)
- Copy username, password or TOTP to the clipboard (`Alt+u`, `Alt+p` and `Alt+t`, respectively)
- Show an autotype menu with all fields

## Usage
First, you need to configure `rbw`. See its documentation for that.
Then, you can start `rofi-rbw`. It is *not* available as a rofi mode.

# Configuration
You can configure `rofi-rbw` either with cli arguments or with a config file called `$XDG_CONFIG_HOME/rofi-rbw.rc`. In the file, use the long option names without double dashes.

## Options

| long option       | short option | possible values                                      | description                                                                                                                                                                                                                                               |
|-------------------|--------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--action`        | `-a`         | `type` (default), `copy`, `print`                    | Choose what `rofi-rbw` should do.                                                                                                                                                                                                                         |
| `--target`        | `-t`         | `username`, `password`, `totp` (or any custom field) | Choose which components of the selected entry are interesting. Can be passed multiple times to type/copy/print several components. Default is `username` and `password`.                                                                                  |
| `--prompt`        | `-r`         | any string                                           | Define the text of the prompt.                                                                                                                                                                                                                            |
| `--selector-args` |              |                                                      | Define arguments that will be passed through to `rofi` or `wofi`.<br/>Please note that you need to specify it as `--selector-args="<args>"` or `--selector-args " <args>"` because of a [bug in argparse](https://github.com/python/cpython/issues/53580) |
| `--selector`      |              | `rofi`, `wofi`                                       | Show the selection dialog with this application. Chosen automatically by default.                                                                                                                                                                         |
| `--clipboarder`   |              | `xsel`, `xclip`, `wl-copy`                           | Access the clipboard with this application. Chosen automatically by default.                                                                                                                                                                              |
| `--typer`         |              | `xdotool`, `wtype`                                   | Type the characters using this application. Chosen automatically by default.                                                                                                                                                                              |
| `--clear-after`   |              | integer number >= 0 (default is `0`)                 | Limit the duration in seconds passwords stay in your clipboard (unless overwritten). When set to 0, passwords will be kept indefinitely.                                                                                                                  |
| `--no-help`       |              |                                                      | Don't show the help message about the available shortcuts.                                                                                                                                                                                                |

# Installation

## From distribution repositories
[![Packaging status](https://repology.org/badge/vertical-allrepos/rofi-rbw.svg)](https://repology.org/project/rofi-rbw/versions)

## From PyPI
`rofi-rbw` is on [PyPI](https://pypi.org/project/rofi-rbw/). You can install it with `pip install --user rofi-rbw` (or `sudo pip install rofi-rbw`).

## Manually
Download the wheel file from releases and install it with  `sudo pip install $filename` (or you can use `pip install --user $filename` to only install it for the local user).
Note that it needs `configargparse` to work.

## Dependencies
You also need:
- Python 3.7 or higher
- `rofi` or `wofi`
- Something to programmatically type characters into other applications. Depending on your display server, it's `xdotool` or `wtype`.
- Something to copy text to the clipboard. Again, depending on the display server, you want `xclip`, `xsel` or `wl-copy`.

# rbw-rofi
## A rofi frontend for Bitwarden

Based on the alternative [Bitwarden](https://bitwarden.com/) CLI [rbw](https://git.tozt.net/rbw) and inspired by [rofi-pass](https://github.com/carnager/rofi-pass), `rbw-rofi` is a simplistic password typer/copier using [rofi](https://github.com/davatorium/rofi).

## Features
- Type the selected password with `Enter` or `Alt+3` (and copy TOTP to clipboard)
- Type the selected username with `Alt+2`
- Autotype username and password (with a `tab` character in between) with `Alt+1` (and copy TOTP to clipboard)
- Copy the username to your clipboard with `Alt+u`
- Copy the password to your clipboard with `Alt+p`
- Copy the totp to your clipboard with `Alt+t`

## Configuration
You can configure `rofi-rbw` either with cli arguments or with a config file called `$XDG_CONFIG_HOME/rofi-rbw.rc`. In the file, use the long option names without double dashes.

### Options

| long option | short option | possible values | description |
| --- | --- | --- | --- |
| `--action` | `-a` | `type-password` (default), `type-username`, `autotype`, `copy-username`, `copy-password` | Chose what `rofi-rbw` should do. |
| `--prompt` | `-r` | any string | Define the prompt text for `rofimoji`. |
| `--fields` | `-f` | any string | What to pass for `--field` when running `rbw list`. |
| `--show-help` | | `true` (default), `false` | Show a help message with the available shortcuts. |
| `--rofi-args` | | | Define arguments that will be passed through to `rofi`.<br/>Please note that you need to specify it as `--rofi-args="<rofi-args>"` or `--rofi-args " <rofi-args>"` because of a [bug in argparse](https://bugs.python.org/issue9334) |
| `--selector` | | `rofi`, `wofi` | Show the selection dialog with this application. |
| `--clipboarder` | | `xsel`, `xclip`, `wl-copy` | Access the clipboard with this application. |
| `--typer` | | `xdotool`, `wtype` | Type the characters using this application. |

## Installation

### Arch Linux
Install the [rofi-rbw](https://aur.archlinux.org/packages/rofi-rbw/) AUR package.

### From PyPI
`rofi-rbw` is on [PyPI](https://pypi.org/project/rofi-rbw/). You can install it with `pip install --user rofi-rbw` (or `sudo pip install rofi-rbw`).

### Manual
Download the wheel file from releases and install it with  `sudo pip install $filename` (or you can use `pip install --user $filename` to only install it for the local user).
Note that it needs `configargparse` to work.

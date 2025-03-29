# rbw-rofi
## A rofi frontend for Bitwarden

Based on the alternative [Bitwarden](https://bitwarden.com/) CLI [rbw](https://github.com/doy/rbw/) and inspired by [rofi-pass](https://github.com/carnager/rofi-pass), `rbw-rofi` is a simplistic password typer/copier using [rofi](https://github.com/davatorium/rofi), [wofi](https://hg.sr.ht/~scoopta/wofi), and [fuzzel](https://codeberg.org/dnkl/fuzzel).

![Screenshot of rofi-rbw](screenshot.png?raw=true)
![Screenshot of a rofi-rbw entry menu](screenshot-menu.png?raw=true)

## Features
- Autotype password or username (`Enter`/`Alt+3` and `Alt+2`, respectively)
- Autotype username and password (with a `tab` character in between) with `Alt+1` (and copy TOTP to clipboard)
- Configure autotyping either as a keybinding or by having a `_autotype` field in your credential
- Copy username, password or TOTP to the clipboard (`Alt+u`, `Alt+p` and `Alt+t`, respectively)
- Show an autotype menu with all fields

## Usage
First, you need to configure `rbw`. See its documentation for that.
Then, you can start `rofi-rbw`. It is *not* available as a rofi mode.

# Configuration
You can configure `rofi-rbw` either with cli arguments or with a config file called `$XDG_CONFIG_HOME/rofi-rbw.rc`. In the file, use the long option names without double dashes.

## Options

| long option          | short option | possible values                                               | description                                                                                                                                                                                                                                                                 |
|----------------------|--------------|---------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--action`           | `-a`         | `type` (default), `copy`, `print`                             | Choose what `rofi-rbw` should do.                                                                                                                                                                                                                                           |
| `--target`           | `-t`         | `username`, `password`, `notes`, `totp` (or any custom field) | Choose which components of the selected entry are interesting. Can be passed multiple times to type/copy/print several components. Default is `username` and `password`.                                                                                                    |
| `--prompt`           | `-r`         | any string                                                    | Define the text of the prompt.                                                                                                                                                                                                                                              |
| `--keybindings`      |              |                                                               | Define custom keybindings in the format `<shortcut>:<action>:<target>`, for example `Alt+x:copy:username`. Multiple keybindings can be concatenated with `,`; multiple targets for one shortcut can be concatenated with `:`. Note that `wofi` and `fuzzel` don't support keybindings. |
| `--menu-keybindings` |              |                                                               | Define custom keybindings for the target menu in the format `<shortcut>:<action>`, similar to `--keybindings`. Note that `wofi` and `fuzzel` don't support keybindings.                                                                                                    |
| `--no-cache`         |              |                                                               | Disable the automatic frecency cache. It contains sha1-hashes of the selected entries and how often they were used.                                                                                                                                                         |
| `--clear-after`      |              | integer number >= 0 (default is `0`)                          | Limit the duration in seconds passwords stay in your clipboard (unless overwritten). When set to 0, passwords will be kept indefinitely.                                                                                                                                    |
| `--typing-key-delay` |              | delay in milliseconds                                         | Set a delay between key presses when typing. `0` by default, but that may result in problems.                                                                                                                                                                               |
| `--no-help`          |              |                                                               | Don't show the help message about the available shortcuts.                                                                                                                                                                                                                  |
| `--no-folder`        |              |                                                               | Don't show the entry's folder in the list.                                                                                                                                                                                                                                  |
| `--selector-args`    |              |                                                               | Define arguments that will be passed through to `rofi`, `wofi`, or `fuzzel`.<br/>Please note that you need to specify it as `--selector-args="<args>"` or `--selector-args " <args>"` because of a [bug in argparse](https://github.com/python/cpython/issues/53580)        |
| `--selector`         |              | `rofi`, `wofi`, `fuzzel`                                      | Show the selection dialog with this application. Chosen automatically by default.                                                                                                                                                                                           |
| `--clipboarder`      |              | `xsel`, `xclip`, `wl-copy`                                    | Access the clipboard with this application. Chosen automatically by default.                                                                                                                                                                                                |
| `--typer`            |              | `xdotool`, `wtype`, `ydotool`, `dotool`                       | Type the characters using this application. Chosen automatically by default.                                                                                                                                                                                                |
| `--use-notify-send`  |              |                                                               | Send desktop notification after copying TOTP.                                                                                                                                                                                                                               |
## Autotyping
By default, `Alt+1` will type username and password, separated with a `tab` character. However, you can change this behavior by defining your own keybinding (if your selector supports this). For example, `Alt+1:type:username:enter:delay:password:enter` will type the username, `enter`, wait for a second and then type the password and `enter` again.

This sequence can also be defined as a field `_autotype` on each credential.

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
- `rofi`, `wofi`, or `fuzzel`
- Something to programmatically type characters into other applications. Depending on your display server, it's `xdotool`, `wtype`, `ydotool` or `dotool`.
- Something to copy text to the clipboard. Again, depending on the display server, you want `xclip`, `xsel` or `wl-copy`.
- Optionally `libnotify` to provide `notify-send` needed for `--use-notify-send`

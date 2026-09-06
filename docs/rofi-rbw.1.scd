rofi-rbw(1) "Version 1.7.0" "Rofi Third-party Add-on Documentation"

# NAME

*rofi-rbw* - A rofi frontend for the alternative Bitwarden client *rbw*

# SYNOPSIS

*rofi-rbw* [_OPTION_]...

*rofi-rbw* *-h* | *--help*

*rofi-rbw* *--version*

# DESCRIPTION

*rofi-rbw* is a frontend for the alternative Bitwarden client *rbw*(1).
It presents the entries of your Bitwarden vault in *rofi* or another
dmenu-like selector (rofi-likes), and types, copies, or prints the
components of the selected entry.

# OPTIONS

*--action*=_ACTION_, *-a* _ACTION_
	Possible values: _type_ (default), _copy_, _print_

	Choose what to do with the selected entry: type it using the
	"Typer", copy it to the clipboard using the "Clipboarder", or print
	it to standard output.

*--target*=_TARGET_, *-t* _TARGET_
	Possible values: _username_, _password_, _totp_, _notes_, _number_,
	_cardholder_, _brand_, _expiry_, _code_, _CUSTOM FIELD NAME_,
	_menu_

	Choose which component of the selected entry to type, copy, or
	print. Can be passed multiple times to use multiple targets. Not
	all entries have all fields. _menu_ is a special value that opens
	the target menu.

*--prompt*=_PROMPT_, *-r* _PROMPT_
	Set the text of the prompt. Default is "Choose entry".

*--display-fields*=_DISPLAY_FIELDS_ [_DISPLAY_FIELDS_ ...]
	Possible values: _name_only_, _name_with_folder_, _folder_,
	_user_, _uri_

	Ordered list of fields to show in the selection list, given as
	separate arguments (e.g. *--display-fields* _name_only_ _user_).
	_name_with_folder_ renders as _folder/name_. Defaults to
	_name_with_folder_ _user_.

*--no-folder* (deprecated)
	Don't show folders in the list of possible entries. Superseded by
	*--display-fields*; translates to *--display-fields* _name_only_
	_user_.

*--keybindings*=_KEYBINDINGS_
	Define custom keybindings in the format
	_<shortcut>:<action>:<target>_, where _shortcut_ is the desired
	keybinding, _action_ is one of the values of *--action*, and
	_target_ is one of the values of *--target*. Multiple keybindings
	are concatenated with a comma; multiple targets for one shortcut
	are concatenated with a colon. Within a sequence, the special
	targets _enter_, _tab_, and _delay_ can be used; _delay_ waits for
	the duration given by *--action-sequence-delay*.

	This feature is only available in selectors that support custom
	keybindings (currently *rofi* and *fuzzel*).

*--menu-keybindings*=_KEYBINDINGS_
	Define custom keybindings for the target menu in the format
	_<shortcut>:<action>_. Multiple keybindings are concatenated with
	a comma.

	This feature is only available in selectors that support custom
	keybindings.

*--clear-after*=_SECONDS_
	Clear the password from the clipboard after _SECONDS_ seconds. Set
	to 0 (the default) to disable.

*--action-sequence-delay*=_MILLISECONDS_
	Define the duration to wait for a _delay_ step in a keybinding
	sequence (e.g. _Alt+c:copy:username:delay:password_). It applies
	to both _type_ and _copy_ actions. 1000 by default.

*--typing-start-delay*=_MILLISECONDS_
	Set a delay before typing starts. 0 by default.

*--typing-key-delay*=_MILLISECONDS_
	Set a delay between key presses when typing. 0 by default.

*--selector*=_SELECTOR_
	Possible values: _rofi_, _wofi_, _fuzzel_, _bemenu_

	Choose the selector application manually. Usually _rofi_, but on
	Wayland you may want _wofi_. Chosen automatically by default.

*--selector-args*=_SELECTOR_ARGS_
	A string of arguments to give to the selector. Due to an argparse
	limitation, specify it as *--selector-args*=_ARGS_ or
	*--selector-args* " ARGS".

*--clipboarder*=_CLIPBOARDER_
	Possible values: _xsel_, _xclip_, _wl-copy_

	Choose the application to access the clipboard with manually.
	Chosen automatically by default.

*--typer*=_TYPER_
	Possible values: _xdotool_, _wtype_, _ydotool_, _dotool_

	Choose the application to type with manually. Chosen
	automatically by default.

*--use-notify-send*
	Send a desktop notification after each field is copied (e.g.
	"username copied to clipboard").

*--no-cache*
	Disable the automatic frecency cache. It contains sha1-hashes of
	the selected entries and how often they were used.

*--no-help*
	Don't show the help message about the available keyboard shortcuts.

*-h*, *--help*
	Print brief usage information and exit.

*--version*
	Print the version number and exit.

# KEYBINDINGS

The following keybindings are active by default (configurable via
*--keybindings*):

- _Enter_: perform the default action (see *--action*)
- _Alt+1_: type the username and the password, separated with a _tab_
  character
- _Alt+2_: type the username
- _Alt+3_: type the password
- _Alt+4_: type the TOTP
- _Alt+c_: copy the password
- _Alt+u_: copy the username
- _Alt+t_: copy the TOTP
- _Alt+m_: show a menu of the entry's components
- _Alt+s_: sync the contents of the vault

The autotyping sequence of _Alt+1_ can also be defined as a custom
field named _autotype_ on each credential.

Custom keybindings are only supported by the _rofi_ and _fuzzel_
selectors; _wofi_ and _bemenu_ only provide the default _Enter_
confirmation.

# CONFIGURATION

Options starting with *--* can also be set in a config file. The
config file syntax allows: _key = value_ for options taking a value,
_flag = true_ for boolean options, and _stuff = [a, b, c]_ for
list-valued options. If an option is specified in more than one place,
command-line values override values from the config file.

The config file is searched for at _\$XDG_CONFIG_HOME/rofi-rbw.rc_ and
in the directories listed in _\$XDG_CONFIG_DIRS_.

# FILES

_~/.config/rofi-rbw.rc_
	Per-user configuration file.

_/etc/xdg/rofi-rbw.rc_
	System-wide configuration file.

_~/.cache/rofi-rbw.runcache_
	Saves the number of times an entry has been used, so that
	frequently used entries can be sorted first. Entries are hashed
	with sha1 so as not to leak any secrets.

# AUTHORS

Fabian Winter.

# WEBSITE

https://github.com/fdw/rofi-rbw

# SEE ALSO

*rbw*(1), *rofi*(1), *wofi*(1), *fuzzel*(1), *bemenu*(1),
*xdotool*(1), *wtype*(1), *ydotool*(1), *xsel*(1), *xclip*(1),
*wl-copy*(1)

# COPYRIGHT

Copyright (C) 2020-2026 Fabian Winter. Released under the MIT License.

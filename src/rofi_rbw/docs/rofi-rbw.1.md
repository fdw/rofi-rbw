% ROFI-RBW(1) Version 1.0.1 | Rofi Third-party Add-on Documentation
% Fabian Winter
% May 22, 2022

# NAME


**rofi-moji** \- A rofi frontend for the alternative Bitwarden client rbw

# SYNOPSIS

| **rofimoji** \[**-h**] \[**\--version**] \[**\--action** {*type*,*copy*,*print*}]
         \[**\--target** {*username*,*password*,*totp*,*OTHER*}]
         \[**\--prompt** *PROMPT*] \[**\--selector-args** *SELECTOR_ARGS*]
         \[**\--clipboarder** *CLIPBOARDER*] \[**\--typer** *TYPER*] \[**\--selector** *SELECTOR*]
         \[**--clear-after** *NUMBER*]

# DESCRIPTION

Type, copy or print your credentials from Bitwarden using rofi.

# OPTIONS

-h, \--help

:   Prints brief usage information.

\--version

:   show program's version number and exit

\--action, -a

: Possible values: type, copy, print

      Choose what to do with the selected characters: Directly type them with the "Typer", copy them to the clipboard using the "Clipboarder", or "print" them on stdout

\--target, -t

: Possible values: username, password, totp, _CUSTOM FIELD NAME_

      Choose which component of the selected entry to type/copy/print. Can be passed multiple times to use multiple targets.

\--prompt _PROMPT_, -r _PROMPT_

:  Set the text for the prompt.

\--selector-args _SELECTOR-ARGS_

:  A string of arguments to give to the selector.

\--clipboarder _CLIPBOARDER_

: Possible values: xsel, xclip, wl-copy

      Choose the application to access the clipboard with manually.

\--typer _TYPER_

: Possible values: xdotool, wtype

      Choose the application to type with manually.

\--selector _SELECTOR_

: Possible values: rofi, wofi

      Choose the selector application manually. Usually `rofi`, but for Wayland, you may want `wofi`.

\--no-help

: Don't show the help message about available keyboard shortcuts

\--clear-after _SECONDS_

: Clear the password from the clipboard after _SECONDS_ seconds. Set to `0` to disable

# KEYBINDINGS

*enter* to use the default action

*alt+p* to copy the password

*alt+u* to copy the username

*alt+t* to copy the TOTP

*alt+m* to show a menu of the entry's components

*alt+1* to autotype username and password, separated with a `tab` character

*alt+2* to type the username

*alt+3* to type the password

Please note that wofi does not support keybindings other than *enter*.

# CONFIGURATION

Args that start with "\--" (eg. \--version) can also be set in a config file.

Config file syntax allows: key=value, flag=true, stuff=[a,b,c]. If an arg is specified in more than one place, then commandline values override values from the config file.

# WEBSITE

https://github.com/fdw/rofi-rbw

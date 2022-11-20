# [NEXT]
## Changed
- Added customizable shortcuts.

## Added
- A shortcut to sync the local database. (#60)
- Modifier keys should not be stuck anymore. (#56)

## Fixed
- When using TOTP, the username is now also taken into consideration for identically named entries. (#59)
- Entries are formatted correctly when not using folders. (#64)

# [1.0.1]
## Fixed
- Fixed interaction with `wofi`. (#51)

# [1.0.0]
## Changed
- Split up `--action` into `--action` and `--target` for better handling.
- `--rofi-args` is now removed. Use `--selector-args` instead.

## Added
- Added an option to limit the time a passwords stay in the clipboard.
- Added a man page.

## Fixed
- Entries without username also work. (#42)
- Custom selector args are passed to the autotype menu. (#43)

# [0.5.0]
## Added
- Added an autotype menu that can works with all defined fields. (#17)
- 
## Fixed
- Entries without password can be handled.

## Changed
- TOTP is now handled by `rbw`. (#33)
- Username is shown in the menu.
- One entry can have multiple URIs. (#25)
- The `--rofi-args` parameter is replaced by an agnostic `--selector-args`.

# [0.4.1]
## Fixed
- Credentials can now be parsed again. (#14)

## Changed
- `xdotool` is now used differently, for hopefully better compatibility.

# [0.4.0]
## Added
- `rofi-rbw` can now deal with TOTPs as well; they're copied to the clipboard by default. (Thanks to #10)
- You can now use `ydotool` as a typer (but without `sudo`). (Thanks to #9)

# [0.3.0]
## Changed
- The search is now case insensitive. (#8)
- Entries are sorted by relevancy.

# [0.2.0]
## Added
- `rofi-rbw` now supports Wayland with `wofi`, `wl-copy` and `wtyper`.
- It also supports `xsel` and `xclip` on X. (Thanks to #4.)
- A help message is shown by default (but can be turned off). (Thanks to #3)\
- Arguments can be passed through to `rofi`.
- Everything can be configured in a config file.

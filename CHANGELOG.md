# [1.4.0] - 2024-04-27
## Added
- Added a parameter to set a key delay when typing. (#88)
- Characters `enter`, `tab` can be used in autotyping, as can a `delay` of one second. (#89)
- Autotyping will use a field `_autotype` on a credential.

# [1.3.0] - 2023-12-07
## Added
- The entries are sorted by frecency. (#79)
- Added `notes` as a field. (#85)

## Changed
- Custom fields can have reserved names (f.e. `password`). (#77)

# [1.2.0] - 2023-05-22
## Added
- Added `dotool` support. (#70, #72)

## Changed
- Use json output from `rbw`.

# [1.1.0] - 2023-01-03
## Added
- Shortcuts can be customized.
- There is a shortcut to sync the local database. (#60)
- Modifier keys should not be stuck anymore. (#56)
- With `--no-folder`, the entry's folder won't be shown in the list. (#64)

## Changed
- `rofi-rbw` is now being built py [Poetry](https://python-poetry.org/).

## Fixed
- When using TOTP, the username is now also taken into consideration for identically named entries. (#59)
- Entries are formatted correctly when not using folders. (#64)

# [1.0.1] - 2022-07-01
## Fixed
- Fixed interaction with `wofi`. (#51)

# [1.0.0] - 2022-06-18
## Changed
- Split up `--action` into `--action` and `--target` for better handling.
- `--rofi-args` is now removed. Use `--selector-args` instead.

## Added
- Added an option to limit the time a passwords stay in the clipboard.
- Added a man page.

## Fixed
- Entries without username also work. (#42)
- Custom selector args are passed to the autotype menu. (#43)

# [0.5.0] - 2021-12-26
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

# [0.4.1] - 2021-06-18
## Fixed
- Credentials can now be parsed again. (#14)

## Changed
- `xdotool` is now used differently, for hopefully better compatibility.

# [0.4.0] - 2021-05-29
## Added
- `rofi-rbw` can now deal with TOTPs as well; they're copied to the clipboard by default. (Thanks to #10)
- You can now use `ydotool` as a typer (but without `sudo`). (Thanks to #9)

# [0.3.0] - 2021-04-08
## Changed
- The search is now case insensitive. (#8)
- Entries are sorted by relevancy.

# [0.2.0] - 2021-03-06
## Added
- `rofi-rbw` now supports Wayland with `wofi`, `wl-copy` and `wtyper`.
- It also supports `xsel` and `xclip` on X. (Thanks to #4.)
- A help message is shown by default (but can be turned off). (Thanks to #3)\
- Arguments can be passed through to `rofi`.
- Everything can be configured in a config file.

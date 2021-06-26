# [NEXT]
## Fixed
- Entries without password can be handled.

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

import os
from pathlib import Path

if os.environ.get("XDG_CACHE_HOME"):
    cache_file = Path(os.environ.get("XDG_CACHE_HOME")) / "rofi-rbw.runcache"
else:
    cache_file = Path.home() / ".cache" / "rofi-rbw.runcache"

if os.environ.get("XDG_CONFIG_HOME"):
    config_home = Path(os.environ.get("XDG_CONFIG_HOME"))
else:
    config_home = Path.home() / ".config"

if os.environ.get("XDG_CONFIG_DIRS"):
    config_global = [Path(dir) for dir in os.environ.get("XDG_CONFIG_DIRS").split(":")]
else:
    config_global = [Path("/etc/xdg")]

config_file_locations = [str(directory / "rofi-rbw.rc") for directory in [config_home] + config_global]

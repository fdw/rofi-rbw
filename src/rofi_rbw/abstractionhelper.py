import os
import shutil


def is_installed(executable: str) -> bool:
    return shutil.which(executable) is not None

def is_x_window_system() -> bool:
    return os.environ.get("DISPLAY", False)

def is_wayland() -> bool:
    return os.environ.get("WAYLAND_DISPLAY", False)

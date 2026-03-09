import atexit
import os
import tempfile
from subprocess import PIPE, run

from ..abstractionhelper import is_installed, is_wayland
from ..models.action import Action
from ..models.detailed_entry import DetailedEntry
from ..models.entry import Entry
from ..models.keybinding import Keybinding
from ..models.targets import Target, Targets
from .selector import Selector


class Fuzzel(Selector):
    def __init__(self, config_path: str | None = None):
        self.config_path = config_path
        self._generated_configs: dict[int, str] = {}

    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("fuzzel")

    @staticmethod
    def name() -> str:
        return "fuzzel"

    def show_selection(
        self,
        entries: list[Entry],
        prompt: str,
        show_help_message: bool,
        show_folders: bool,
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None, Entry | None]:
        config_path = self.__keybinding_config(keybindings)
        fuzzel = run(
            [
                "fuzzel", "--dmenu", "--index", "-p", prompt,
                *(["--config", config_path] if config_path else []),
                *(self.__format_keybindings_message(keybindings) if show_help_message and keybindings else []),
                *additional_args,
            ],
            input="\n".join(self._format_entries(entries, show_folders)),
            stdout=PIPE,
            encoding="utf-8",
        )

        selected = entries[int(fuzzel.stdout.strip())] if fuzzel.stdout.strip() else None
        if fuzzel.returncode == 0:
            return None, None, selected
        elif fuzzel.returncode >= 10 and fuzzel.returncode - 10 < len(keybindings):
            keybinding = keybindings[fuzzel.returncode - 10]
            return keybinding.targets, keybinding.action, selected
        else:
            return None, Action.CANCEL, None

    def select_target(
        self,
        entry: DetailedEntry,
        show_help_message: bool,
        keybindings: list[Keybinding],
        additional_args: list[str],
    ) -> tuple[list[Target] | None, Action | None]:
        config_path = self.__keybinding_config(keybindings)
        fuzzel = run(
            [
                "fuzzel", "--dmenu", "-p", "Choose target",
                *(["--config", config_path] if config_path else []),
                *(self.__format_keybindings_message(keybindings) if show_help_message and keybindings else []),
                *additional_args,
            ],
            input="\n".join(self._format_targets_from_entry(entry)),
            stdout=PIPE,
            encoding="utf-8",
        )

        if fuzzel.returncode == 0:
            return self._extract_targets(fuzzel.stdout), None
        elif fuzzel.returncode >= 10 and fuzzel.returncode - 10 < len(keybindings):
            return self._extract_targets(fuzzel.stdout), keybindings[fuzzel.returncode - 10].action
        else:
            return None, Action.CANCEL

    def __keybinding_config(self, keybindings: list[Keybinding]) -> str | None:
        if not keybindings:
            return None

        # menu and sync actions close and reopen fuzzel, reuse generated config if able
        cache_key = id(keybindings)
        if cache_key in self._generated_configs:
            return self._generated_configs[cache_key]

        content = self.__build_config(keybindings)
        fd, path = tempfile.mkstemp(suffix=".ini", prefix="rofi-rbw-fuzzel-")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        atexit.register(os.unlink, path)

        self._generated_configs[cache_key] = path
        return path

    def __build_config(self, keybindings: list[Keybinding]) -> str:
        lines = []
        # base_config` may already use `include`, can't nest `include`s, so we copy+append instead
        base_config = self.config_path or self.__find_user_config()
        if base_config:
            with open(base_config) as f:
                lines.append(f.read().rstrip())
            lines.append("")

        # parity with rofi on empty menus
        lines.append("[dmenu]")
        lines.append("exit-immediately-if-empty=no")
        lines.append("")

        lines.append("[key-bindings]")
        for index, keybinding in enumerate(keybindings):
            lines.append(f"custom-{1 + index}={self.__convert_shortcut(keybinding.shortcut)}")
        # clear any remaining custom-* binds, we don't have handlers for them
        for index in range(len(keybindings) + 1, 20):
            lines.append(f"custom-{index}=none")

        return "\n".join(lines)

    @staticmethod
    def __find_user_config() -> str | None:
        # match fuzzel's search order
        candidates = []

        xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "")
        if xdg_config_home.startswith("/"):
            candidates.append(os.path.join(xdg_config_home, "fuzzel", "fuzzel.ini"))
        elif "HOME" in os.environ:
            candidates.append(os.path.join(os.environ["HOME"], ".config", "fuzzel", "fuzzel.ini"))

        xdg_config_dirs = os.environ.get("XDG_CONFIG_DIRS", "")
        if xdg_config_dirs:
            for d in xdg_config_dirs.split(":"):
                candidates.append(os.path.join(d, "fuzzel", "fuzzel.ini"))
        else:
            candidates.append("/etc/xdg/fuzzel/fuzzel.ini")

        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    @staticmethod
    def __convert_shortcut(shortcut: str) -> str:
        return shortcut.replace("Alt+", "Mod1+").replace("Super+", "Mod4+")

    @staticmethod
    def __format_keybindings_message(keybindings: list[Keybinding]):
        parts = []
        for keybinding in keybindings:
            if keybinding.targets and Targets.MENU in keybinding.targets:
                label = "Menu"
            elif keybinding.action == Action.SYNC:
                label = "Sync logins"
            elif keybinding.targets:
                label = f"{keybinding.action.value.title()} {', '.join([target.raw for target in keybinding.targets])}"
            else:
                label = keybinding.action.value.title()
            parts.append(f"{keybinding.shortcut}: {label}")

        return ["--mesg", " | ".join(parts)]

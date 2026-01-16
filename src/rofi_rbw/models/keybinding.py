from dataclasses import dataclass

from .action import Action
from .targets import TypeTarget


@dataclass
class Keybinding:
    shortcut: str
    action: Action | None
    targets: list[TypeTarget] | None

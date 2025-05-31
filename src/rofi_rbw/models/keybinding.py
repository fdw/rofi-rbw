from dataclasses import dataclass
from typing import List, Union

from .action import Action
from .targets import TypeTarget


@dataclass
class Keybinding:
    shortcut: str
    action: Action
    targets: Union[List[TypeTarget], None]

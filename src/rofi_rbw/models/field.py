from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FieldType(Enum):
    HIDDEN = "hidden"
    TEXT = "text"
    BOOLEAN = "boolean"
    LINKED = "linked"


@dataclass
class Field:
    key: str
    value: str
    type: Optional[FieldType]

    def masked_string(self):
        if self.type == FieldType.HIDDEN:
            return self.value[0] + ("*" * (len(self.value) - 1))

        return self.value

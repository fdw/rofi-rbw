from dataclasses import dataclass
from enum import Enum


class FieldType(Enum):
    HIDDEN = "hidden"
    TEXT = "text"
    BOOLEAN = "boolean"
    LINKED = "linked"


@dataclass
class Field:
    key: str
    value: str
    type: FieldType | None

    def masked_string(self):
        if self.type == FieldType.HIDDEN:
            return self.value[0] + ("*" * (len(self.value) - 1))

        return self.value

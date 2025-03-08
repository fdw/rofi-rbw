from dataclasses import dataclass, field
from enum import Enum
from subprocess import run
from typing import List, Optional, Union

from .entry import Entry
from .models import Target, Targets, TypeTarget


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


@dataclass(frozen=True)
class Credentials(Entry):
    password: Optional[str] = ""
    has_totp: bool = False
    notes: Optional[str] = ""
    uris: List[str] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)

    def __getitem__(self, target: Target) -> Optional[Union[str, List[str]]]:
        if target == Targets.USERNAME:
            return self.username
        elif target == Targets.PASSWORD:
            return self.password
        elif target == Targets.TOTP:
            return self.totp
        elif target == Targets.NOTES:
            return self.notes
        elif target.is_uri():
            return self.uris[target.uri_index()]
        else:
            return next((field for field in self.fields if field.key == target.raw.removesuffix(" (field)")), None)

    @property
    def totp(self):
        if not self.has_totp:
            return ""

        command = ["rbw", "code", self.name]
        if self.username:
            command.extend([self.username])
        if self.folder:
            command.extend(["--folder", self.folder])
        return run(command, capture_output=True, encoding="utf-8").stdout.strip()

    @property
    def autotype_sequence(self) -> Union[List[TypeTarget], None]:
        sequence = next((field for field in self.fields if field.key == "_autotype"), None)
        if sequence is None:
            return None

        return [TypeTarget(target_string) for target_string in sequence.value.strip().split(":")]

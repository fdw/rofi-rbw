from dataclasses import dataclass, field
from subprocess import run
from typing import Dict, List, Optional, Union

from .entry import Entry
from .models import Target, Targets, TypeTarget


@dataclass(frozen=True)
class Credentials(Entry):
    password: Optional[str] = ""
    has_totp: bool = False
    notes: Optional[str] = ""
    uris: List[str] = field(default_factory=list)
    further: Dict[str, str] = field(default_factory=dict)

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
            return self.further.get(target.raw.removesuffix(" (field)"), None)

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
        if "_autotype" not in self.further:
            return None

        return [TypeTarget(target_string) for target_string in self.further["_autotype"].strip().split(":")]

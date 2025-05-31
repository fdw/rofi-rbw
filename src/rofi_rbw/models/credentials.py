from dataclasses import dataclass, field
from subprocess import run
from typing import List, Optional

from .detailed_entry import DetailedEntry
from .field import Field
from .targets import Target, Targets


@dataclass(frozen=True)
class Credentials(DetailedEntry):
    username: Optional[str] = ""
    password: Optional[str] = ""
    has_totp: bool = False
    notes: Optional[str] = ""
    uris: List[str] = field(default_factory=list)
    fields: List[Field] = field(default_factory=list)

    def __getitem__(self, target: Target) -> Optional[str]:
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
            return next(
                (field.value for field in self.fields if field.key == target.raw.removesuffix(" (field)")), None
            )

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

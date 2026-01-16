from dataclasses import dataclass, field
from subprocess import run

from .detailed_entry import DetailedEntry
from .field import Field
from .targets import Target, Targets


@dataclass(frozen=True)
class Credentials(DetailedEntry):
    username: str | None = ""
    password: str | None = ""
    has_totp: bool = False
    notes: str | None = ""
    uris: list[str] = field(default_factory=list)
    fields: list[Field] = field(default_factory=list)

    def __getitem__(self, target: Target) -> str | None:
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

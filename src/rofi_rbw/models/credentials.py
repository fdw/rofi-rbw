from dataclasses import dataclass, field
from subprocess import run

from .detailed_entry import DetailedEntry
from .field import Field
from .targets import Target, Targets, TypeTarget, TypeTargets


@dataclass(frozen=True)
class Credentials(DetailedEntry):
    username: str | None = ""
    password: str | None = ""
    has_totp: bool = False
    notes: str | None = ""
    uris: list[str] = field(default_factory=list)
    fields: list[Field] = field(default_factory=list)

    def __getitem__(self, target: Target) -> str | None:
        match target:
            case Targets.USERNAME:
                return self.username
            case Targets.PASSWORD:
                return self.password
            case Targets.TOTP:
                return self.totp
            case Targets.NOTES:
                return self.notes
            case _ if target.is_uri():
                return self.uris[target.uri_index()]
            case _:
                return next(
                    (field.value for field in self.fields if field.key == target.raw.removesuffix(" (field)")), None
                )

    @property
    def default_target(self) -> list[Target]:
        return [Targets.USERNAME, Targets.PASSWORD]

    @property
    def default_autotype_target(self) -> list[TypeTarget]:
        return [Targets.USERNAME, TypeTargets.TAB, Targets.PASSWORD]

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

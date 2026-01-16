from dataclasses import dataclass, field

from .detailed_entry import DetailedEntry
from .field import Field
from .targets import Target, Targets


@dataclass(frozen=True)
class Note(DetailedEntry):
    notes: str | None = ""
    fields: list[Field] = field(default_factory=list)

    def __getitem__(self, target: Target) -> str | None:
        if target == Targets.NOTES:
            return self.notes
        else:
            return next(
                (field.value for field in self.fields if field.key == target.raw.removesuffix(" (field)")), None
            )

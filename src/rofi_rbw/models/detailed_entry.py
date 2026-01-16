from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from rofi_rbw.models.field import Field
from rofi_rbw.models.targets import Target, TypeTarget


@dataclass(frozen=True)
class DetailedEntry(ABC):
    name: str
    folder: str | None = ""
    fields: list[Field] = field(default_factory=list)

    @abstractmethod
    def __getitem__(self, target: Target) -> str | None:
        pass

    @property
    def autotype_sequence(self) -> list[TypeTarget] | None:
        sequence = next((field for field in self.fields if field.key == "_autotype"), None)
        if sequence is None:
            return None

        return [TypeTarget(target_string) for target_string in sequence.value.strip().split(":")]

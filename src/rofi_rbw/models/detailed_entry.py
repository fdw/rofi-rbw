from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Union

from rofi_rbw.models.field import Field
from rofi_rbw.models.targets import Target, TypeTarget


@dataclass(frozen=True)
class DetailedEntry(ABC):
    name: str
    folder: Optional[str] = ""
    fields: List[Field] = field(default_factory=list)

    @abstractmethod
    def __getitem__(self, target: Target) -> Optional[str]:
        pass

    @property
    def autotype_sequence(self) -> Union[List[TypeTarget], None]:
        sequence = next((field for field in self.fields if field.key == "_autotype"), None)
        if sequence is None:
            return None

        return [TypeTarget(target_string) for target_string in sequence.value.strip().split(":")]

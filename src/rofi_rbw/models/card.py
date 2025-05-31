from dataclasses import dataclass
from typing import Optional

from .detailed_entry import DetailedEntry
from .targets import Target, Targets


@dataclass(frozen=True)
class Card(DetailedEntry):
    cardholder_name: Optional[str] = None
    number: Optional[str] = None
    brand: Optional[str] = None
    exp_month: Optional[str] = None
    exp_year: Optional[str] = None
    code: Optional[str] = None
    notes: Optional[str] = None

    def __getitem__(self, target: Target) -> Optional[str]:
        if target == Targets.NUMBER:
            return self.number
        elif target == Targets.CARDHOLDER:
            return self.cardholder_name
        elif target == Targets.BRAND:
            return self.brand
        elif target == Targets.EXPIRY:
            return f"{self.exp_year:0>4}-{self.exp_month:0>2}"
        elif target == Targets.CODE:
            return self.code
        else:
            return next(
                (field.value for field in self.fields if field.key == target.raw.removesuffix(" (field)")), None
            )

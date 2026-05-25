from dataclasses import dataclass

from .detailed_entry import DetailedEntry
from .targets import Target, Targets, TypeTarget, TypeTargets


@dataclass(frozen=True)
class Card(DetailedEntry):
    cardholder_name: str | None = None
    number: str | None = None
    brand: str | None = None
    exp_month: str | None = None
    exp_year: str | None = None
    code: str | None = None
    notes: str | None = None

    @property
    def default_target(self) -> list[Target]:
        return [Targets.NUMBER, Targets.EXPIRY, Targets.CODE]

    @property
    def default_autotype_target(self) -> list[TypeTarget]:
        return [Targets.NUMBER, TypeTargets.TAB, Targets.EXPIRY, TypeTargets.TAB, Targets.CODE]

    def __getitem__(self, target: Target) -> str | None:
        match target:
            case Targets.NUMBER:
                return self.number
            case Targets.CARDHOLDER:
                return self.cardholder_name
            case Targets.BRAND:
                return self.brand
            case Targets.EXPIRY:
                return f"{self.exp_year:0>4}-{self.exp_month:0>2}"
            case Targets.CODE:
                return self.code
            case _:
                return next(
                    (field.value for field in self.fields if field.key == target.raw.removesuffix(" (field)")), None
                )

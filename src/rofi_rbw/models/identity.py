from dataclasses import dataclass

from .detailed_entry import DetailedEntry
from .targets import Target, Targets, TypeTarget, TypeTargets


@dataclass(frozen=True)
class Identity(DetailedEntry):
    title: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    address1: str | None = None
    address2: str | None = None
    address3: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    phone: str | None = None
    email: str | None = None
    ssn: str | None = None
    license_number: str | None = None
    passport_number: str | None = None
    username: str | None = None
    notes: str | None = None

    @property
    def default_target(self) -> list[Target]:
        return [Targets.FIRST_NAME, Targets.LAST_NAME]

    @property
    def default_autotype_target(self) -> list[TypeTarget]:
        return [Targets.FIRST_NAME, TypeTargets.TAB, Targets.LAST_NAME]

    def __getitem__(self, target: Target) -> str | None:
        match target:
            case Targets.TITLE:
                return self.title
            case Targets.FIRST_NAME:
                return self.first_name
            case Targets.MIDDLE_NAME:
                return self.middle_name
            case Targets.LAST_NAME:
                return self.last_name
            case Targets.USERNAME:
                return self.username
            case Targets.EMAIL:
                return self.email
            case Targets.PHONE:
                return self.phone
            case Targets.ADDRESS_1:
                return self.address1
            case Targets.ADDRESS_2:
                return self.address2
            case Targets.ADDRESS_3:
                return self.address3
            case Targets.CITY:
                return self.city
            case Targets.STATE:
                return self.state
            case Targets.POSTAL_CODE:
                return self.postal_code
            case Targets.COUNTRY:
                return self.country
            case Targets.SSN:
                return self.ssn
            case Targets.LICENSE_NUMBER:
                return self.license_number
            case Targets.PASSPORT_NUMBER:
                return self.passport_number
            case Targets.NOTES:
                return self.notes
            case _:
                return next(
                    (field.value for field in self.fields if field.key == target.raw.removesuffix(" (field)")), None
                )

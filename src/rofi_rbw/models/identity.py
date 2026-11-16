from dataclasses import dataclass

from .detailed_entry import DetailedEntry
from .targets import Target, Targets, TypeTarget


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
    def target_values(self) -> list[tuple[Target, str | None]]:
        return [
            (Targets.TITLE, self.title),
            (Targets.FIRST_NAME, self.first_name),
            (Targets.MIDDLE_NAME, self.middle_name),
            (Targets.LAST_NAME, self.last_name),
            (Targets.USERNAME, self.username),
            (Targets.EMAIL, self.email),
            (Targets.PHONE, self.phone),
            (Targets.ADDRESS_1, self.address1),
            (Targets.ADDRESS_2, self.address2),
            (Targets.ADDRESS_3, self.address3),
            (Targets.CITY, self.city),
            (Targets.STATE, self.state),
            (Targets.POSTAL_CODE, self.postal_code),
            (Targets.COUNTRY, self.country),
            (Targets.SSN, self.ssn),
            (Targets.LICENSE_NUMBER, self.license_number),
            (Targets.PASSPORT_NUMBER, self.passport_number),
            (Targets.NOTES, self.notes),
        ]

    def __getitem__(self, target: Target) -> str | None:
        return next(
            (value for key, value in self.target_values if key == target),
            next((field.value for field in self.fields if field.key == target.raw.removesuffix(" (field)")), None),
        )

    @property
    def default_target(self) -> list[Target]:
        return [Targets.MENU]

    @property
    def default_autotype_target(self) -> list[TypeTarget]:
        return [Targets.MENU]

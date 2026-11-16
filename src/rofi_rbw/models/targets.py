class Target:
    __value: str

    def __init__(self, input: str):
        prepared_input = input.strip()
        if prepared_input.lower() in (
            "address 1",
            "address 2",
            "address 3",
            "brand",
            "cardholder",
            "city",
            "code",
            "country",
            "email",
            "expiry",
            "first name",
            "last name",
            "license number",
            "menu",
            "middle name",
            "notes",
            "number",
            "passport number",
            "password",
            "phone",
            "postal code",
            "ssn",
            "state",
            "title",
            "totp",
            "username",
        ) or prepared_input.lower().startswith("uri"):
            self.__value = prepared_input.lower()
        else:
            self.__value = prepared_input

    def is_uri(self) -> bool:
        return self.__value.startswith("uri")

    def uri_index(self) -> int:
        if not self.is_uri():
            raise IndexError()

        if len(self.__value) == 3:
            return 0
        else:
            return int(self.__value[4:]) - 1

    @property
    def raw(self):
        return self.__value

    def __eq__(self, other):
        return self.__value == other.__value


class TypeTarget(Target):
    pass


class Targets:
    USERNAME = Target("username")
    PASSWORD = Target("password")
    TOTP = Target("totp")
    NUMBER = Target("number")
    CARDHOLDER = Target("cardholder")
    BRAND = Target("brand")
    EXPIRY = Target("expiry")
    CODE = Target("code")
    TITLE = Target("title")
    FIRST_NAME = Target("first name")
    MIDDLE_NAME = Target("middle name")
    LAST_NAME = Target("last name")
    ADDRESS_1 = Target("address 1")
    ADDRESS_2 = Target("address 2")
    ADDRESS_3 = Target("address 3")
    CITY = Target("city")
    STATE = Target("state")
    POSTAL_CODE = Target("postal code")
    COUNTRY = Target("country")
    PHONE = Target("phone")
    EMAIL = Target("email")
    SSN = Target("ssn")
    LICENSE_NUMBER = Target("license number")
    PASSPORT_NUMBER = Target("passport number")
    NOTES = Target("notes")
    MENU = Target("menu")


class TypeTargets:
    DELAY = TypeTarget("delay")
    ENTER = TypeTarget("enter")
    TAB = TypeTarget("tab")

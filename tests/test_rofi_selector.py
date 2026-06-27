import pytest

from rofi_rbw.models.display_field_token import DisplayFieldToken
from rofi_rbw.models.entry import Entry
from rofi_rbw.models.EntryType import EntryType
from rofi_rbw.selector.rofi import Rofi

default_entry = Entry(
    name="github",
    folder="personal",
    username="user",
    type=EntryType.LOGIN,
    uris=["https://github.com", "https://second.com"],
)
second_entry = Entry(name="site", folder="", username="longeruser", type=EntryType.LOGIN, uris=["https://example.com"])

rofi = Rofi()


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        (DisplayFieldToken.NAME_ONLY, "<b>github</b>"),
        (DisplayFieldToken.NAME_WITH_FOLDER, "personal/<b>github</b>"),
        (DisplayFieldToken.FOLDER, "personal"),
        (DisplayFieldToken.USER, "user"),
        (DisplayFieldToken.FIRST_URI, "https://github.com"),
    ],
    ids=["name_only", "name_with_folder", "folder", "user", "first_uri"],
)
def test_rofi_format_field(token, expected):
    assert rofi._format_field(default_entry, token) == expected


@pytest.mark.parametrize(
    ("tokens", "expected"),
    [
        (
            [DisplayFieldToken.NAME_WITH_FOLDER, DisplayFieldToken.USER],
            ["personal/<b>github</b>  user      ", "<b>site</b>             longeruser"],
        ),
        (
            [DisplayFieldToken.NAME_ONLY, DisplayFieldToken.USER],
            ["<b>github</b>  user      ", "<b>site</b>    longeruser"],
        ),
        (
            [DisplayFieldToken.FOLDER, DisplayFieldToken.FIRST_URI],
            ["personal  https://github.com ", "          https://example.com"],
        ),
    ],
    ids=["name_with_folder_user", "name_only_user", "folder_uri"],
)
def test_rofi_format_entries(tokens, expected):
    assert rofi._format_entries([default_entry, second_entry], tokens) == expected


@pytest.mark.parametrize(
    ("tokens", "index"),
    [
        ([DisplayFieldToken.NAME_WITH_FOLDER, DisplayFieldToken.USER], 0),
        ([DisplayFieldToken.NAME_ONLY, DisplayFieldToken.USER], 1),
    ],
    ids=["name_with_folder_user", "name_only_user"],
)
def test_rofi_find_entry(tokens, index):
    formatted = rofi._format_entries([default_entry, second_entry], tokens)[index]
    found = rofi._find_entry([default_entry, second_entry], formatted, tokens)
    assert found == [default_entry, second_entry][index]

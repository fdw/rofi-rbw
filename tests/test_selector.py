import pytest

from rofi_rbw.models.display_field_token import DisplayFieldToken
from rofi_rbw.models.entry import Entry
from rofi_rbw.models.EntryType import EntryType

from .DummySelector import DummySelector

default_entry = Entry(
    name="github",
    folder="personal",
    username="user",
    type=EntryType.LOGIN,
    uris=["https://github.com", "https://second.com"],
)
second_entry = Entry(name="site", folder="", username="longeruser", type=EntryType.LOGIN, uris=["https://example.com"])

dummy_selector = DummySelector()


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        (DisplayFieldToken.NAME_ONLY, "github"),
        (DisplayFieldToken.NAME_WITH_FOLDER, "personal/github"),
        (DisplayFieldToken.FOLDER, "personal"),
        (DisplayFieldToken.USER, "user"),
        (DisplayFieldToken.FIRST_URI, "https://github.com"),
    ],
    ids=["name_only", "name_with_folder", "folder", "user", "first_uri"],
)
def test_format_field_populated(token, expected):
    assert dummy_selector._format_field(default_entry, token) == expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        (DisplayFieldToken.NAME_WITH_FOLDER, ""),
        (DisplayFieldToken.NAME_ONLY, ""),
        (DisplayFieldToken.FOLDER, ""),
        (DisplayFieldToken.FIRST_URI, ""),
        (DisplayFieldToken.USER, ""),
    ],
    ids=["name_with_folder_no_folder", "empty_folder", "no_uris", "no_name", "empty_username"],
)
def test_format_field_empty_defaults(token, expected):
    assert (
        dummy_selector._format_field(
            Entry(name="", folder="", username="", type=EntryType.LOGIN, uris=None or []), token
        )
        == expected
    )


def test_format_field_uris_picks_first():
    entry = Entry(
        name="github",
        folder="",
        username="user",
        type=EntryType.LOGIN,
        uris=["https://first.com", "https://second.com"],
    )
    assert dummy_selector._format_field(entry, DisplayFieldToken.FIRST_URI) == "https://first.com"


@pytest.mark.parametrize(
    ("entries", "tokens", "expected"),
    [
        (
            [default_entry, second_entry],
            [DisplayFieldToken.NAME_WITH_FOLDER, DisplayFieldToken.USER],
            ["personal/github  user      ", "site             longeruser"],
        ),
        (
            [default_entry, second_entry],
            [DisplayFieldToken.NAME_ONLY, DisplayFieldToken.USER],
            ["github  user      ", "site    longeruser"],
        ),
        (
            [default_entry, second_entry],
            [DisplayFieldToken.NAME_WITH_FOLDER, DisplayFieldToken.USER, DisplayFieldToken.FIRST_URI],
            [
                "personal/github  user        https://github.com ",
                "site             longeruser  https://example.com",
            ],
        ),
        (
            [default_entry],
            [DisplayFieldToken.NAME_ONLY],
            ["github"],
        ),
        (
            [
                default_entry,
                Entry(name="site", folder="", username="", type=EntryType.LOGIN, uris=[]),
            ],
            [DisplayFieldToken.NAME_WITH_FOLDER, DisplayFieldToken.USER, DisplayFieldToken.FIRST_URI],
            [
                "personal/github  user  https://github.com",
                "site                                     ",
            ],
        ),
    ],
    ids=["two_columns", "name_only_user", "three_columns", "single_column", "missing_value"],
)
def test_format_entries_padding(entries, tokens, expected):
    assert dummy_selector._format_entries(entries, tokens) == expected


@pytest.mark.parametrize(
    ("entries", "tokens", "index"),
    [
        (
            [default_entry, second_entry],
            [DisplayFieldToken.NAME_WITH_FOLDER, DisplayFieldToken.USER],
            0,
        ),
        (
            [
                default_entry,
                second_entry,
            ],
            [DisplayFieldToken.NAME_WITH_FOLDER, DisplayFieldToken.USER, DisplayFieldToken.FIRST_URI],
            1,
        ),
        (
            [default_entry, second_entry],
            [DisplayFieldToken.NAME_ONLY],
            1,
        ),
        (
            [default_entry, second_entry],
            [DisplayFieldToken.NAME_ONLY, DisplayFieldToken.USER],
            0,
        ),
    ],
    ids=["two_columns", "three_columns", "single_column", "name_only_user"],
)
def test_find_entry(entries, tokens, index):
    formatted = dummy_selector._format_entries(entries, tokens)[index]
    found = dummy_selector._find_entry(entries, formatted, tokens)
    assert found == entries[index]

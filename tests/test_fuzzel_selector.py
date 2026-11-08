from rofi_rbw.models.entry import Entry
from rofi_rbw.models.EntryType import EntryType
from rofi_rbw.selector.fuzzel import Fuzzel

fuzzel = Fuzzel()


def test_fuzzel_rows_have_display_and_match_columns():
    entry = Entry(name="github", folder="", username="user", type=EntryType.LOGIN, uris=["https://github.com"])
    assert fuzzel._format_rows([entry], ["github  user"]) == ["github  user\tgithub  user https://github.com"]


def test_fuzzel_rows_strip_tabs_from_display_text():
    entry = Entry(name="a\tb", folder="", username="", type=EntryType.NOTE)
    assert fuzzel._format_rows([entry], ["a\tb"]) == ["a b\ta b"]

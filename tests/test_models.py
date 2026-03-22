import pytest

from rofi_rbw.models.card import Card
from rofi_rbw.models.credentials import Credentials
from rofi_rbw.models.note import Note
from rofi_rbw.models.targets import Targets


@pytest.mark.parametrize(
    ("entry", "expected_targets", "expected_values"),
    [
        (Note("test", "", [], "some notes"), [Targets.NOTES], ["some notes"]),
        (
            Credentials("test", "", [], "user", "pass", False, "", []),
            [Targets.USERNAME, Targets.PASSWORD],
            ["user", "pass"],
        ),
        (
            Card("test", "", [], None, "1234", None, "1", "2025", "123", None),
            [Targets.NUMBER, Targets.EXPIRY, Targets.CODE],
            ["1234", "2025-01", "123"],
        ),
    ],
    ids=["note", "credentials", "card"],
)
def test_default_target_return_values(entry, expected_targets, expected_values):
    assert entry.default_target == expected_targets
    for target, expected in zip(entry.default_target, expected_values):
        assert entry[target] == expected

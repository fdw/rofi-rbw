import pytest

from rofi_rbw.argument_parsing import parse_arguments
from rofi_rbw.models.display_field_token import DisplayFieldToken


def test_parse_arguments_display_fields_default():
    args = parse_arguments([])
    assert args.display_fields == [DisplayFieldToken.NAME_WITH_FOLDER, DisplayFieldToken.USER]


def test_parse_arguments_display_fields_explicit():
    args = parse_arguments(["--display-fields", "name_only", "uri"])
    assert args.display_fields == [DisplayFieldToken.NAME_ONLY, DisplayFieldToken.FIRST_URI]


def test_parse_arguments_no_folder_translates():
    args = parse_arguments(["--no-folder"])
    assert args.display_fields == [DisplayFieldToken.NAME_ONLY, DisplayFieldToken.USER]


def test_parse_arguments_display_fields_overrides_no_folder():
    args = parse_arguments(["--no-folder", "--display-fields", "folder", "user", "uri"])
    assert args.display_fields == [DisplayFieldToken.FOLDER, DisplayFieldToken.USER, DisplayFieldToken.FIRST_URI]


def test_parse_arguments_display_fields_invalid_token():
    with pytest.raises(SystemExit):
        parse_arguments(["--display-fields", "name_only", "bogus"])


def test_parse_arguments_no_folder_warns_deprecation(capsys):
    parse_arguments(["--no-folder"])
    captured = capsys.readouterr()
    assert "--no-folder" in captured.err
    assert "deprecated" in captured.err.lower()


def test_parse_arguments_no_deprecation_warning_without_no_folder(capsys):
    parse_arguments([])
    captured = capsys.readouterr()
    assert "--no-folder" not in captured.err


def test_parse_arguments_no_deprecation_warning_with_display_fields(capsys):
    parse_arguments(["--display-fields", "name_only", "uri"])
    captured = capsys.readouterr()
    assert "--no-folder" not in captured.err

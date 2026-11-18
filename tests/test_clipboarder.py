from unittest.mock import patch

from rofi_rbw.clipboarder.clipboarder import Clipboarder
from rofi_rbw.clipboarder.wlclip import WlClipboarder, WlLegacyClipboarder


def copy(clipboarder, returncode=0):
    with patch("rofi_rbw.clipboarder.wlclip.run") as run:
        run.return_value.returncode = returncode
        clipboarder.copy_to_clipboard("secret")
    return run


def test_wl_copy_legacy_is_never_chosen_automatically():
    assert not WlLegacyClipboarder.supported()


def test_wl_copy_legacy_is_chosen_by_name():
    assert isinstance(Clipboarder.best_option("wl-copy-legacy"), WlLegacyClipboarder)


def test_wl_copy_sets_sensitive():
    assert copy(WlClipboarder()).call_args.args[0] == ["wl-copy", "--sensitive"]


def test_wl_copy_legacy_does_not_set_sensitive():
    assert copy(WlLegacyClipboarder()).call_args.args[0] == ["wl-copy"]


def test_wl_copy_success_prints_nothing(capsys):
    copy(WlClipboarder())
    assert capsys.readouterr().err == ""


def test_wl_copy_failure_names_the_exit_code_and_points_to_the_legacy_clipboarder(capsys):
    copy(WlClipboarder(), returncode=2)
    err = capsys.readouterr().err
    assert "exited with code 2" in err
    assert "wl-copy-legacy" in err
    assert "secret" not in err


def test_wl_copy_legacy_failure_does_not_mention_sensitive(capsys):
    copy(WlLegacyClipboarder(), returncode=1)
    assert capsys.readouterr().err == ""


def test_wl_copy_legacy_clears_the_clipboard_if_unchanged():
    clipboarder = WlLegacyClipboarder()
    copy(clipboarder)
    with patch("rofi_rbw.clipboarder.wlclip.time.sleep"), patch("rofi_rbw.clipboarder.wlclip.run") as run:
        run.return_value.stdout = "secret"
        clipboarder.clear_clipboard_after(1)
    assert run.call_args.args[0] == ["wl-copy", "--clear"]

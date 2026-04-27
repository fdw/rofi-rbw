import string

from hypothesis import given
from hypothesis import strategies as st

from rofi_rbw.models.entry import Entry
from rofi_rbw.models.EntryType import EntryType
from rofi_rbw.selector.bemenu import Bemenu

# Any concrete Selector works; we only need an instance to call inherited methods.
_selector = Bemenu()
_text = st.text(alphabet=string.ascii_letters + string.digits + "/-_.", min_size=1, max_size=20)


@given(
    name=_text,
    folder=st.one_of(st.just(""), _text),
    username=st.one_of(st.just(""), _text),
    entry_type=st.sampled_from(EntryType),
    show_folders=st.booleans(),
)
def test_format_find_round_trip(name, folder, username, entry_type, show_folders):
    """An entry must round-trip through _format_entries → _find_entry, even after the selector strips trailing whitespace."""
    entry = Entry(name=name, folder=folder, username=username, type=entry_type)
    formatted = _selector._format_entries([entry], show_folders=show_folders)
    # Selectors (e.g. fuzzel) strip trailing whitespace from echoed selections.
    assert _selector._find_entry([entry], formatted[0].rstrip()) == entry

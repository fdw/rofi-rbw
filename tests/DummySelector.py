from rofi_rbw.selector.selector import Selector


class DummySelector(Selector):
    @staticmethod
    def supported() -> bool:
        return False

    @staticmethod
    def name() -> str:
        return "dummy"

    def show_selection(self, entries, prompt, show_help_message, display_fields, keybindings, additional_args):
        raise NotImplementedError

    def select_target(self, entry, show_help_message, keybindings, additional_args):
        raise NotImplementedError

from enum import Enum


class EntryType(Enum):
    LOGIN = "Login"
    IDENTITY = "Identity"
    SSH_KEY = "SSH Key"
    NOTE = "Note"
    CARD = "Card"

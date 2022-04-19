from enum import Enum

class Action(Enum):
    TYPE_PASSWORD = 'type-password'
    TYPE_USERNAME = 'type-username'
    TYPE_BOTH = 'autotype'
    COPY_USERNAME = 'copy-username'
    COPY_PASSWORD = 'copy-password'
    COPY_TOTP = 'copy-totp'
    AUTOTYPE_MENU = 'menu'
    PRINT = 'print'


from enum import Enum


class DisplayFieldToken(Enum):
    NAME_ONLY = "name_only"
    NAME_WITH_FOLDER = "name_with_folder"
    FOLDER = "folder"
    USER = "user"
    FIRST_URI = "uri"

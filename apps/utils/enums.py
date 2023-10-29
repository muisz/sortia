from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def display_name(cls, value):
        for enum in cls:
            if enum.value == value:
                return enum.name
        return None

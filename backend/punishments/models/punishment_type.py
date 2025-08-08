from enum import auto, StrEnum


class PunishmentType(StrEnum):
    BAN = auto()
    MUTE = auto()
    KICK = auto()
    WARN = auto()

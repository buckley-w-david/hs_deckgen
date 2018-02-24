import enum

class HSClass(enum.Enum):
    DRUID = enum.auto()
    HUNTER = enum.auto()
    MAGE = enum.auto()
    PALADIN = enum.auto()
    PRIEST = enum.auto()
    ROGUE = enum.auto()
    SHAMAN = enum.auto()
    WARLOCK = enum.auto()
    WARRIOR = enum.auto()
    NEUTRAL = enum.auto()


class Rarity(enum.Enum):
    FREE = enum.auto()
    COMMON = enum.auto()
    RARE = enum.auto()
    EPIC = enum.auto()
    LEGENDARY = enum.auto()

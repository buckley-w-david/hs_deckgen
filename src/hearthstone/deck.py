import enum
import typing
import json
import urllib.request
from lxml import html, etree
import base64


from hearthstone import card
from hearthstone import hsdata


class DeckSerialization(enum.Enum):
    JSON = enum.auto()
    CODE = enum.auto()


_HSREPLAY_TO_CLASS = {
    274: hsdata.HSClass.DRUID,
    31: hsdata.HSClass.HUNTER,
    637: hsdata.HSClass.MAGE,
    671: hsdata.HSClass.PALADIN,
    813: hsdata.HSClass.PRIEST,
    930: hsdata.HSClass.ROGUE,
    1066: hsdata.HSClass.SHAMAN,
    893: hsdata.HSClass.WARLOCK,
    7: hsdata.HSClass.WARRIOR,
}

_CLASS_TO_DB = {
    hsdata.HSClass.DRUID: 274,
    hsdata.HSClass.HUNTER: 31,
    hsdata.HSClass.MAGE: 637,
    hsdata.HSClass.PALADIN: 671,
    hsdata.HSClass.PRIEST: 813,
    hsdata.HSClass.ROGUE: 930,
    hsdata.HSClass.SHAMAN: 1066,
    hsdata.HSClass.WARLOCK: 893,
    hsdata.HSClass.WARRIOR: 7,
}



class _Deck(typing.NamedTuple):
    cards: typing.List[card.Card]
    hs_class: hsdata.HSClass


def to_varint(i: int) -> bytes:
    buffer: typing.List[bytes] = []

    for _ in range((i.bit_length()-1) // 7):
        towrite = i & 0x7f
        i >>= 7
        buffer.append((towrite | 0x80).to_bytes(length=1, byteorder='big'))

    buffer.append(i.to_bytes(length=1, byteorder='big'))
    return b''.join(buffer)


class Deck(_Deck):

    @classmethod
    def from_cards(cls, cards: typing.List[card.Card], hs_class: typing.Optional[hsdata.HSClass]=None) -> 'Deck':
        if hs_class is None:
            scan = filter(
                lambda hs_class: hs_class is not hsdata.HSClass.NEUTRAL,
                map(
                    lambda card: card.hs_class,
                    cards
                )
            )
            hs_class = next(scan)

        return Deck(
            cards=cards,
            hs_class=hs_class
        )

    @classmethod
    def from_deck_code(cls, code: str) -> 'Deck':
        raise NotImplementedError()


    @classmethod
    def from_json(json: typing.Dict[str, typing.Any]) -> 'Deck':
        return Deck(
            cards=[card.Card.from_json(card_dict) for card_dict in json['cards']],
            hs_class=getattr(HSClass, json['hs_class'])
        )

    @classmethod
    def load(cls, stream: typing.IO[str]) -> 'Deck':
        return cls.from_json(json.load(stream))

    def save(self, stream: typing.IO[str], mode=DeckSerialization.CODE) -> None:
        if mode is DeckSerialization.JSON:
            json.dump({'cards': [card.to_json() for card in self.cards], 'hs_class': self.hs_class.name}, stream)
        else:
            stream.write(self.to_deck_code())

    @property
    def unique(self) -> typing.Set[card.Card]:
        return set(self.cards)

    @property
    def doubles(self) -> typing.Set[card.Card]:
        seen = set()
        doubles = set()
        for card in self.cards:
            if card in seen:
                doubles.add(card)
            else:
                seen.add(card)
        return doubles

    def to_deck_code(self) -> str:
        deck_code_list = [0, 1, 1]
        deck_code_list.append(1)
        deck_code_list.append(_CLASS_TO_DB.get(self.hs_class))

        unique = self.unique
        doubles = self.doubles
        singles = unique - doubles

        deck_code_list.append(len(singles))
        db_key = lambda card: card.db_id

        for card in sorted(singles, key=db_key):
            deck_code_list.append(card.db_id)

        deck_code_list.append(len(doubles))
        for card in sorted(doubles, key=db_key):
            deck_code_list.append(card.db_id)

        deck_code_list.append(0)
        deck_code = b''.join(map(to_varint, deck_code_list))

        encoded = base64.b64encode(deck_code)
        return encoded.decode("utf-8")

    def __iter__(self):
        for card in self.cards:
            yield card

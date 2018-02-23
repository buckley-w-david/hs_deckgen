import enum
import itertools
import json
import typing
import urllib.request
import urllib.parse
from lxml import html, etree
import requests
import base64


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


_HSREPLAY_TO_CLASS = {
    274: HSClass.DRUID,
    31: HSClass.HUNTER,
    637: HSClass.MAGE,
    671: HSClass.PALADIN,
    813: HSClass.PRIEST,
    930: HSClass.ROGUE,
    1066: HSClass.SHAMAN,
    893: HSClass.WARLOCK,
    7: HSClass.WARRIOR,
}

_CLASS_TO_DB = {
    HSClass.DRUID: 274,
    HSClass.HUNTER: 31,
    HSClass.MAGE: 637,
    HSClass.PALADIN: 671,
    HSClass.PRIEST: 813,
    HSClass.ROGUE: 930,
    HSClass.SHAMAN: 1066,
    HSClass.WARLOCK: 893,
    HSClass.WARRIOR: 7,
}


class _Card(typing.NamedTuple):
    db_id: int
    hs_class: HSClass
    rarity: Rarity
    name: str


class Card(_Card):

    @classmethod
    def from_id(db_id: int) -> 'Card':
        raise NotImplementedError()

    @classmethod
    def from_json(cls, json: typing.Dict[str, typing.Any]) -> 'Card':
        return Card(
            db_id=json['db_id'],
            hs_class=getattr(HSClass, json['hs_class']),
            rarity=getattr(Rarity, json['rarity']),
            name=json['name'],
        )

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {
            'db_id': self.db_id,
            'hs_class': self.hs_class.name,
            'rarity': self.rarity.name,
            'name': self.name,
        }


class _Deck(typing.NamedTuple):
    cards: typing.List[Card]
    hs_class: HSClass


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
    def from_cards(cls, cards: typing.List[Card], hs_class: typing.Optional[HSClass]=None) -> 'Deck':
        if hs_class is None:
            scan = filter(
                lambda hs_class: hs_class is not HSClass.NEUTRAL,
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
    def from_hsreplay(cls, url: str) -> 'Deck':
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as request:
            document = html.parse(request)

        deck_info = document.xpath("body/div[@id = 'deck-info']")[0]
        cards = [HearthstoneAPI.card_from_id(int(id)) for id in deck_info.attrib['data-deck-cards'].split(',')]

        hs_class = getattr(HSClass, deck_info.attrib['data-deck-class'])

        return Deck(cards, hs_class)

    @classmethod
    def from_json(json: typing.Dict[str, typing.Any]) -> 'Deck':
        return Deck(
            cards=[Card.from_json(card) for card in json['cards']],
            hs_class=getattr(HSClass, json['hs_class'])
        )

    @classmethod
    def load(cls, stream: typing.IO[str]) -> 'Deck':
        return Deck.from_json(json.load(stream))

    def save(self, stream: typing.IO[str]) -> None:
        json.dump({'cards': [card.to_json() for card in self.cards], 'hs_class': self.hs_class.name}, stream)

    @property
    def unique(self) -> typing.Set[Card]:
        return set(self.cards)

    @property
    def doubles(self) -> typing.Set[Card]:
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


class ReplayAPI:

    @classmethod
    def top_decks(cls, n=None) -> typing.Iterator[Deck]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

        base = 'https://hsreplay.net'
        url = urllib.parse.urljoin(base, 'decks')

        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as request:
            document = html.parse(request)

        query = "body/div[@id = 'decks-container']/div[@class = 'deck-list-wrapper']/div[@class = 'deck-list']/ul/li/a/@href"
        if n:
            snipper = range(n)
        else:
            snipper = itertools.count()

        for _, href in zip(snipper, document.xpath(query)):
            url = urllib.parse.urljoin(base, href)
            yield Deck.from_hsreplay(url)


class HearthstoneAPI:

    _CARDS = None

    @classmethod
    def _get_cards(cls) -> None:
        endpoint = 'https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json'
        with requests.get(endpoint) as r:
            cards = r.json()

        cls._CARDS = {
            card['dbfId']: Card(
                db_id=card['dbfId'],
                hs_class=getattr(HSClass, card['playerClass']),
                rarity=getattr(Rarity, card['rarity']),
                name=card['name'],
            ) for card in cards
        }

    def lazy_cards(func):
        def decorated(*args, **kwargs):
            if HearthstoneAPI._CARDS is None:
                HearthstoneAPI._get_cards()
            return func(*args, **kwargs)
        return decorated

    @classmethod
    @lazy_cards
    def card_from_id(cls, card_id: int) -> typing.Optional[Card]:
        return cls._CARDS.get(card_id)


    @classmethod
    @lazy_cards
    def all_cards(cls) -> typing.Set[Card]:
        return cls._CARDS.values()
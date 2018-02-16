import enum
import json
import typing
import urllib.request
from lxml import html, etree


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



class Card(typing.NamedTuple):
    db_id: int


class Deck:

    def __init__(self, cards: typing.List[Card]):
        assert len(cards) == 30, 'Bad deck size'
        self.deck = deck = sorted(cards, key=lambda card: card.db_id)
        self.unique = set(deck)
        self.doubles = set()

        seen = set()

        for card in deck:
            if card not in seen:
                seen.add(card)
            else:
                self.doubles.add(card)

    @classmethod
    def from_hsreplay(cls, url: str) -> 'Deck':
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

        request = urllib.request.urlopen(urllib.request.Request(url, headers=headers))

        document = html.parse(request)
        deck_info = document.xpath("body/div[@id = 'deck-info']")[0]
        cards = [Card(db_id=int(id)) for id in deck_info.attrib['data-deck-cards'].split(',')]

        hs_class = deck_info.attrib['data-deck-class']

        return Deck(cards)

    @classmethod
    def from_ids(cls, cards: typing.List[int]) -> 'Deck':
        return Deck([Card(db_id=card_id) for card_id in cards])

    @classmethod
    def load(cls, stream: typing.IO[str]) -> 'Deck':
        return Deck(json.load(stream))

    def save(self, stream: typing.IO[str]) -> None:
        json.dump([card.db_id for card in self.deck], stream)

    def __iter__(self):
        for card in self.deck:
            yield card
